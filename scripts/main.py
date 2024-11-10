import os
import modules.scripts as scripts
from modules import script_callbacks
import gradio as gr
from modules import shared
from huggingface_hub import HfApi
from typing import List, Tuple

class HFBackupScript(scripts.Script):
    def title(self):
        return "HF Backup"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def after_component(self, component, **kwargs):
        return None

def get_directory_list():
    """Get list of relevant directories in the SD webui folder"""
    base_dirs = [
        os.path.join(scripts.basedir(), "models/Stable-diffusion"),
        os.path.join(scripts.basedir(), "models/Lora"),
        os.path.join(scripts.basedir(), "embeddings"),
        os.path.join(scripts.basedir(), "extensions"),
        os.path.join(scripts.basedir(), "textual_inversion")
    ]
    
    # Get absolute paths and ensure they exist
    dirs = [os.path.abspath(d) for d in base_dirs if os.path.exists(d)]
    return sorted(dirs)

def get_files_in_directory(directory: str) -> List[dict]:
    """Get list of relevant files in the selected directory"""
    if not directory or not os.path.exists(directory):
        return []
        
    extensions = ('.safetensors', '.ckpt', '.pt', '.bin', '.zip', '.jpg', '.png')
    files = []
    
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(extensions):
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, directory)
                # Create a dictionary with the file information
                files.append({
                    "value": full_path,  # The actual value for processing
                    "label": rel_path,   # What the user sees
                })
    
    return sorted(files, key=lambda x: x["label"].lower())

def upload_to_huggingface(repo: str, selected_files: List[str], pr_message: str, progress=gr.Progress()) -> str:
    try:
        username = getattr(shared.opts, "hf_username", None)
        api_token = getattr(shared.opts, "hf_write_token", None)
        
        if not username or not api_token:
            return "Error: Please configure Hugging Face credentials in settings"

        api = HfApi(token=api_token)
        repo_id = f"{username}/{repo}"
        results = []
        
        try:
            api.create_repo(repo_id, private=True, exist_ok=True)
        except Exception as e:
            return f"Error creating/accessing repository: {str(e)}"

        total_files = len(selected_files)
        for idx, file_path in enumerate(selected_files, 1):
            try:
                file_name = os.path.basename(file_path)
                progress(idx / total_files, desc=f"Uploading {file_name}")
                results.append(f"Uploading: {file_name}")
                
                api.upload_file(
                    path_or_fileobj=file_path,
                    path_in_repo=file_name,
                    repo_id=repo_id,
                    commit_message=f"{pr_message}: {file_name}"
                )
                
                results.append(f"✓ Successfully uploaded {file_name}")
                
            except Exception as e:
                results.append(f"✗ Error uploading {file_name}: {str(e)}")
                
            results.append("-" * 40)
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Error: {str(e)}"

def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as hf_interface:
        with gr.Column():
            gr.HTML("""
                <div style="text-align: center; margin-bottom: 1rem">
                    <h1 style="font-size: 1.5rem">🤗 Hugging Face Hub Uploader</h1>
                    <p>Backup your models and files to Hugging Face</p>
                </div>
            """)
            
            repository = gr.Textbox(
                label="Repository Name",
                placeholder="Name of the repository to upload to"
            )
            
            with gr.Row():
                dir_dropdown = gr.Dropdown(
                    label="Select Directory",
                    choices=get_directory_list(),
                    type="value",
                    allow_custom_value=True
                )
            
            with gr.Row():
                file_list = gr.Dropdown(
                    label="Available Files",
                    choices=[],
                    type="value",
                    multiselect=True,
                    allow_custom_value=False
                )
            
            pr_message = gr.Textbox(
                label="Commit Message",
                placeholder="Description of your upload",
                value="Backup files"
            )
            
            upload_button = gr.Button("🚀 Upload to Hugging Face")
            result = gr.Textbox(
                label="Results",
                interactive=False,
                max_lines=10,
                autoscroll=True
            )
            
            def update_file_list(directory):
                if not directory:
                    return gr.Dropdown(choices=[])
                return gr.Dropdown(choices=get_files_in_directory(directory))
            
            def prepare_upload(repo, selected_files, pr_message):
                if not selected_files:
                    return "Please select files to upload"
                return upload_to_huggingface(repo, selected_files, pr_message)
            
            dir_dropdown.change(
                fn=update_file_list,
                inputs=[dir_dropdown],
                outputs=[file_list]
            )
            
            upload_button.click(
                fn=prepare_upload,
                inputs=[
                    repository,
                    file_list,
                    pr_message
                ],
                outputs=result
            )

        return [(hf_interface, "HF Backup", "hf_backup_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)