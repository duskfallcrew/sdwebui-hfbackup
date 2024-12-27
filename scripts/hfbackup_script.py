import os
import datetime
#import threading
import gradio as gr
import logging
from modules import scripts, script_callbacks, shared, paths
from modules.scripts import basedir
from huggingface_hub import HfApi, HfFolder
import shutil
from pathlib import Path
import hashlib
import gc
from apscheduler.schedulers.background import BackgroundScheduler

# Constants
REPO_NAME = 'sd-webui-backups'
BACKUP_INTERVAL = 3600  # 1 hour in seconds
HF_TOKEN_KEY = 'hf_token'
BACKUP_PATHS_KEY = 'backup_paths'
SD_PATH_KEY = 'sd_path'
HF_USER_KEY = 'hf_user'
DEFAULT_BACKUP_PATHS = ['models/Stable-diffusion', 'models/VAE', 'embeddings', 'loras']

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

# --- Helper function for updating the status ---
def update_status(script, status, file=None):
    if file:
        script.status = f"{status}: {file}"
        print(f"{status}: {file}") # For console logging.
    else:
        script.status = status
        print(status)  # For console logging

# --- HfApi Related Functions ---
def get_hf_token(script):
    if shared.opts.hf_write_key: hf_token = shared.opts.hf_write_key
    elif script.hf_token: hf_token = script.hf_token
    elif HfFolder.get_token(): hf_token = HfFolder.get_token()
    else: hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        update_status(script, "HF_TOKEN environment variable not found")
        raise Exception("HF_TOKEN environment variable not found")
    return hf_token

def get_hf_user(script):
    if script.hf_user: return script.hf_user
    hf_token = get_hf_token(script)
    api = HfApi(token=hf_token)
    whoami = api.whoami(token=hf_token)
    return whoami.get("name", "") if isinstance(whoami, dict) else ""

def clone_or_create_repo(repo_id: str, repo_type: str, repo_path: str, script):
    update_status(script, "Checking/Cloning Repo...")
    logger.info(f"Cloning repository from {repo_id} to {repo_path}")
    update_status(script, "Cloning repository")
    try:
        hf_token = get_hf_token(script)
        api = HfApi(token=hf_token)
        if os.path.exists(repo_path) and os.path.isdir(repo_path):
            logger.info(f"Repository already exists at {repo_path}, updating...")
            ignore_paths = get_ingore_paths(repo_path, repo_id, repo_type, hf_token)
        else:
            os.makedirs(repo_path, exist_ok=True)
            ignore_paths = []
        if api.repo_exists(repo_id=repo_id, repo_type=repo_type, token=hf_token):
            api.snapshot_download(repo_id=repo_id, repo_type=repo_type, local_dir=repo_path, ignore_patterns=ignore_paths, token=hf_token)
    except Exception as e:
        logger.error(f"Error creating or cloning repo: {e}")
        update_status(script, f"Error creating or cloning repo: {e}")
        raise
    update_status(script, "Repo ready")

def get_path_in_repo(path: str):
    return str(Path(path)).replace("\\", "/")

def get_sha256(filename: str):
    if not Path(filename).exists(): return None
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def is_same_file(filename: str, dst_repo: str, dst_type: str, dst_path: str, hf_token: str):
    api = HfApi(token=hf_token)
    if not filename or not Path(filename).exists() or Path(filename).is_dir(): return False
    dst_path = get_path_in_repo(dst_path)
    if not api.file_exists(repo_id=dst_repo, filename=dst_path, repo_type=dst_type, token=hf_token): return False
    src_sha256 = get_sha256(filename)
    src_size = os.path.getsize(filename)
    dst_info = api.get_paths_info(repo_id=dst_repo, paths=dst_path, repo_type=dst_type, token=hf_token)
    if not dst_info or len(dst_info) != 1 or dst_info[0].lfs is None: return False
    if src_size == dst_info[0].size and src_sha256 == dst_info[0].lfs.sha256: return True
    else: return False

def get_ingore_paths(path: str, repo_id: str, repo_type: str, hf_token: str):
    ignores = []
    for p in Path(path).glob("**/*"):
        if p.is_dir(): continue
        rp = p.resolve().relative_to(Path(path).resolve())
        if is_same_file(str(p), repo_id, repo_type, str(rp), hf_token): ignores.append(get_path_in_repo(str(rp)))
    if len(ignores) != 0: print(f"These files are already latest: {', '.join(ignores)}") # debug
    return ignores

def safe_copy(src: str, dst: str, script):
    if not Path(src).exists(): return
    if Path(dst).exists() and os.path.getsize(src) == os.path.getsize(dst) and get_sha256(src) == get_sha256(dst):
        logger.info(f"Skipped: {src}")
        update_status(script, "Skipped", src)
        return
    shutil.copy2(src, dst)
    logger.info(f"Copied: {src}")
    update_status(script, "Copied", src)

def hf_push_files(repo_id: str, repo_type: str, repo_path: str, commit_message: str, script):
    update_status(script, "Pushing changes...")
    try:
        hf_token = get_hf_token(script)
        api = HfApi(token=hf_token)
        ignore_paths = get_ingore_paths(repo_path, repo_id, repo_type, hf_token)
        api.create_repo(repo_id=repo_id, repo_type=repo_type, exist_ok=True, token=hf_token)
        api.upload_folder(repo_id=repo_id, repo_type=repo_type, folder_path=repo_path, path_in_repo="",
                          ignore_patterns=ignore_paths, commit_message=commit_message, token=hf_token)
        logger.info(f"Changes pushed successfully to remote repository.")
        update_status(script, "Pushing Complete")
    except Exception as e:
        logger.error(f"HF push failed: {e}")
        update_status(script, f"HF push failed: {e}")
        raise

# --- Backup Logic ---
def backup_files(backup_paths, script):
    repo_type = "model"
    logger.info("Starting backup...")
    update_status(script, "Starting Backup...")
    repo_id = get_hf_user(script) + "/" + script.hf_repo
    repo_path = os.path.join(script.basedir, 'backup')
    sd_path = script.sd_path if script.sd_path else paths.data_path
    try:
        clone_or_create_repo(repo_id, repo_type, repo_path, script)
    except Exception as e:
        logger.error("Error starting the backup, please see the traceback.")
        return
    for base_path in backup_paths:
        logger.info(f"Backing up: {base_path}")
        for root, _, files in os.walk(os.path.join(sd_path, base_path)):
            for file in files:
                local_file_path = os.path.join(root, file)
                repo_file_path = os.path.relpath(local_file_path, start=sd_path)
                try:
                    os.makedirs(os.path.dirname(os.path.join(repo_path, repo_file_path)), exist_ok=True)
                    safe_copy(local_file_path, os.path.join(repo_path, repo_file_path), script)
                except Exception as e:
                    logger.error(f"Error copying {repo_file_path}: {e}")
                    update_status(script, f"Error copying: {repo_file_path}: {e}")
                    return
    try:
        hf_push_files(repo_id, repo_type, repo_path, f"Backup at {datetime.datetime.now()}", script)
        logger.info("Backup complete")
        update_status(script, "Backup Complete")
    except Exception as e:
        logger.error("Error pushing to the repo: ", e)
        return

def start_backup_thread(script, is_scheduled: bool, backup_interval: int):
    backup_files(script.backup_paths, script)
    #threading.Thread(target=backup_files, args=(script.backup_paths, script), daemon=True).start()
    script.update_schedule(is_scheduled, backup_interval)
    gc.collect()

# Gradio UI Setup
def on_ui(script):
    with gr.Blocks(analytics_enabled=False) as hf_backup:
        with gr.Column():
            with gr.Row():
                with gr.Column(scale=3):
                    hf_token_box = gr.Textbox(label="Huggingface Token", type='password', value=script.hf_token)
                    def on_token_change(token: str):
                        script.hf_token = token
                    hf_token_box.change(on_token_change, inputs=[hf_token_box], outputs=None)
                with gr.Column(scale=1):
                    status_box = gr.Textbox(label="Status", value=script.status)
                    with gr.Row():
                        is_scheduled = gr.Checkbox(label="Scheduled backups", value=True)
                        backup_interval = gr.Number(label="Backup interval", step=1, minimum=60, maximum=36000, value=BACKUP_INTERVAL)
                    def on_start_button(is_scheduled: bool, backup_interval: int, progress=gr.Progress(track_tqdm=True)):
                        start_backup_thread(script, is_scheduled, backup_interval)
                        return "Starting Backup"
                    start_button = gr.Button(value="Start Backup")
                    start_button.click(on_start_button, inputs=[is_scheduled, backup_interval], outputs=[status_box])
            with gr.Row():
                with gr.Column():
                    sd_path_box = gr.Textbox(label="SD Webui Path", value=script.sd_path)
                    def on_sd_path_change(path: str):
                        script.sd_path = path
                    sd_path_box.change(on_sd_path_change, inputs=[sd_path_box], outputs=None)
                with gr.Column():
                    hf_user_box = gr.Textbox(label="Huggingface Username", value=script.hf_user)
                    def on_hf_user_change(user: str):
                        script.hf_user = user
                    hf_user_box.change(on_hf_user_change, inputs=[hf_user_box], outputs=None)
                with gr.Column():
                    hf_repo_box = gr.Textbox(label="Huggingface Reponame", value=script.hf_repo)
                    def on_hf_repo_change(repo: str):
                        script.hf_repo = repo
                    hf_repo_box.change(on_hf_repo_change, inputs=[hf_repo_box], outputs=None)
            with gr.Row():
                backup_paths_box = gr.Textbox(label="Backup Paths (one path per line)", lines=4, value='\n'.join(script.backup_paths) if isinstance(script.backup_paths, list) else "")
                def on_backup_paths_change(paths: list):
                    paths_list = [p.strip() for p in paths.split('\n') if p.strip()]
                    script.backup_paths = paths_list
                backup_paths_box.change(on_backup_paths_change, inputs=[backup_paths_box], outputs=None)
    return [(hf_backup, "Huggingface Backup", "hfbackup_script")]

class HFBackupScript():
    env = {}

    def __init__(self):
        self.hf_token = self.env.get(HF_TOKEN_KEY, "")
        self.backup_paths = self.env.get(BACKUP_PATHS_KEY, DEFAULT_BACKUP_PATHS)
        self.sd_path = self.env.get(SD_PATH_KEY, "")
        self.hf_user = self.env.get(HF_USER_KEY, "")
        self.hf_repo = REPO_NAME
        self.status = "Not running"
        self.basedir = basedir()
        self.scheduler = None

    def title(self):
        return "Huggingface Backup"

    def show(self, is_img2img=None):
        return scripts.AlwaysVisible

    def on_ui(self, is_img2img=None):
        return on_ui(self)
    
    def update_schedule(self, is_scheduled: bool, backup_interval: int):
        if self.scheduler is not None:
            self.scheduler.shutdown()
            del self.scheduler
            gc.collect()
        if is_scheduled:
            self.scheduler = BackgroundScheduler()
            self.scheduler.add_job(func=backup_files, args=[self.backup_paths, self], trigger="interval", id="backup", replace_existing=True, seconds=backup_interval)
            self.scheduler.start()
    
if __package__ == "hfbackup_script":
    script = HFBackupScript()
    script_callbacks.on_ui_tabs(script.on_ui)
