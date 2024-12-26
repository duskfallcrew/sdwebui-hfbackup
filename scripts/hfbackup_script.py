# This is the full code we built on last step

import os
import time
import datetime
import threading
import gradio as gr
import subprocess
import logging
from modules import script_callbacks, shared
from git import Repo

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


# --- Git Related Functions ---
def clone_or_create_repo(repo_url, repo_path, script):
    script.status = "Checking/Cloning Repo..."
    if os.path.exists(repo_path) and os.path.isdir(repo_path):
        logger.info(f"Repository already exists at {repo_path}, updating...")
        repo = Repo(repo_path)
        if repo.is_dirty():
            logger.warning("Local repo has uncommitted changes. Commit those before running to make sure nothing breaks.")
            script.status = "Local repo has uncommitted changes"
        
    else:
        logger.info(f"Cloning repository from {repo_url} to {repo_path}")
        script.status = "Cloning repository"
        try:
            Repo.clone_from(repo_url, repo_path)
        except Exception as e:
            logger.error(f"Error creating or cloning repo: {e}")
            script.status = f"Error creating or cloning repo: {e}"
            raise
    script.status = "Repo ready"
    return repo

def git_push_files(repo_path, commit_message, script):
    script.status = "Pushing changes..."
    try:
        repo = Repo(repo_path)
        repo.git.add(all=True)
        repo.index.commit(commit_message)
        origin = repo.remote(name='origin')
        origin.push()
        logger.info(f"Changes pushed successfully to remote repository.")
        script.status = "Pushing Complete"
    except Exception as e:
         logger.error(f"Git push failed: {e}")
         script.status = f"Git push failed: {e}"
         raise

# --- Backup Logic ---
def backup_files(paths, hf_client, script):
    logger.info("Starting backup...")
    script.status = "Starting Backup..."
    repo_id = script.hf_user + "/" + REPO_NAME
    repo_path = os.path.join(script.basedir, 'backup')
    sd_path = script.sd_path

    try:
        repo = clone_or_create_repo(f"https://huggingface.co/{repo_id}", repo_path, script)
    except Exception as e:
        logger.error("Error starting the backup, please see the traceback.")
        return

    for base_path in paths:
        logger.info(f"Backing up: {base_path}")
        for root, _, files in os.walk(os.path.join(sd_path, base_path)):
            for file in files:
                local_file_path = os.path.join(root, file)
                repo_file_path = os.path.relpath(local_file_path, start=sd_path)
                try:
                    os.makedirs(os.path.dirname(os.path.join(repo_path, repo_file_path)), exist_ok=True)
                    subprocess.run(["cp", local_file_path, os.path.join(repo_path, repo_file_path)], check=True, capture_output=True)
                    logger.info(f"Copied: {repo_file_path}")
                    script.status = f"Copied: {repo_file_path}"
                except Exception as e:
                    logger.error(f"Error copying {repo_file_path}: {e}")
                    script.status = f"Error copying: {repo_file_path}: {e}"
                    return

    try:
        git_push_files(repo_path, f"Backup at {datetime.datetime.now()}", script)
        logger.info("Backup complete")
        script.status = "Backup Complete"
    except Exception as e:
         logger.error("Error pushing to the repo: ", e)
         return

def start_backup_thread(script):
    threading.Thread(target=backup_loop, args=(script,), daemon=True).start()

def backup_loop(script):
    try:
      backup_files(script.backup_paths, None, script)
    except Exception as e:
      print(f"Backup error: {e}")
    time.sleep(BACKUP_INTERVAL)

# Gradio UI Setup
def on_ui(script):
    with gr.Column():
        with gr.Row():
            with gr.Column(scale=3):
                hf_token_box = gr.Textbox(label="Huggingface Token", type='password', value=script.hf_token)
                def on_token_change(token):
                    script.hf_token = token
                    script.save()
                hf_token_box.change(on_token_change, inputs=[hf_token_box], outputs=None)
            with gr.Column(scale=1):
                status_box = gr.Textbox(label="Status", value=script.status)
                
                def on_start_button():
                    start_backup_thread(script)
                    return "Starting Backup"

                start_button = gr.Button(value="Start Backup")
                start_button.click(on_start_button, inputs=None, outputs=[status_box])

        with gr.Row():
             with gr.Column():
                  sd_path_box = gr.Textbox(label="SD Webui Path", value=script.sd_path)
                  def on_sd_path_change(path):
                        script.sd_path = path
                        script.save()
                  sd_path_box.change(on_sd_path_change, inputs=[sd_path_box], outputs=None)
             with gr.Column():
                  hf_user_box = gr.Textbox(label="Huggingface Username", value=script.hf_user)
                  def on_hf_user_change(user):
                        script.hf_user = user
                        script.save()
                  hf_user_box.change(on_hf_user_change, inputs=[hf_user_box], outputs=None)
        with gr.Row():
             backup_paths_box = gr.Textbox(label="Backup Paths (one path per line)", lines=4, value='\n'.join(script.backup_paths))
             def on_backup_paths_change(paths):
                paths_list = paths.split('\n')
                paths_list = [p.strip() for p in paths_list if p.strip()]
                script.backup_paths = paths_list
                script.save()
             backup_paths_box.change(on_backup_paths_change, inputs=[backup_paths_box], outputs=None)

def on_run(script, p, *args):
    pass
  
def on_script_load(script):
    script.hf_token = script.load().get(HF_TOKEN_KEY, '')
    script.backup_paths = script.load().get(BACKUP_PATHS_KEY, DEFAULT_BACKUP_PATHS)
    script.sd_path = script.load().get(SD_PATH_KEY, '')
    script.hf_user = script.load().get(HF_USER_KEY, '')
    script.status = "Not running"

script_callbacks.on_ui_tabs(on_ui)
script_callbacks.on_script_load(on_script_load)
