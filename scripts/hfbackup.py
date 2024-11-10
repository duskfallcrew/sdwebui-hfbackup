# scripts/hf_backup.py
import modules.scripts as scripts
import gradio as gr
import os
from modules import shared, script_callbacks
from huggingface_hub import HfApi
import glob
from typing import List

def get_directory_list():
    """Get list of relevant directories in the SD webui folder"""
    base_dirs = [
        "models/Stable-diffusion",
        "models/Lora",
        "embeddings",
        "extensions",
        "textual_inversion"
    ]
    
    # Get absolute paths and ensure they exist
    dirs = [os.path.abspath(d) for d in base_dirs if os.path.exists(d)]
    # Add parent directory of each
    parent_dirs = list(set([os.path.dirname(d) for d in dirs]))
    
    return sorted(dirs + parent_dirs)

def upload_to_huggingface(username: str, repo: str, write_key: str, 
                         selected_files: List[str], pr_message: str, progress=gr.Progress()):
    try:
        # Get API token from input or settings
        api_token = write_key or shared.opts.data.get("hf_write_key", "")
        if not api_token:
            return "Error: No Hugging Face Write API Key provided"

        api = HfApi(token=api_token)
        repo_id = f"{username}/{repo}"
        results = []
        
        # Validate repository exists or create it
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
                
                response = api.upload_file(
                    path_or_fileobj=file_path,
                    path_in_repo=file_name,
                    repo_id=repo_id,
                    create_pr=True,
                    commit_message=f"{pr_message}: {file_name}"
                )
                
                pr_url = response.get("pullRequest", {}).get("url", "")
                if pr_url:
                    results.append(f"✓ Successfully uploaded {file_name}")
                    results.append(f"Pull request: {pr_url}")
                else:
                    results.append(f"✓ Uploaded {file_name} (no PR created)")
                
            except Exception as e:
                results.append(f"✗ Error uploading {file_name}: {str(e)}")
                
            results.append("-" * 40)  # Separator between files
        
        progress(1.0, desc="Upload complete!")
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
            
            with gr.Row():
                username = gr.Textbox(
                    label="Hugging Face Username",
                    placeholder="Your HF username",
                    value=shared.opts.data.get("hf_default_username", "")
                )
                repository = gr.Textbox(
                    label="Repository Name",
                    placeholder="Name of the repository"
                )
            
            with gr.Row():
                write_key = gr.Textbox(
                    label="Write Key (optional if set in settings)",
                    placeholder="Your HF write token",
                    type="password"
                )
            
            with gr.Row():
                dir_dropdown = gr.Dropdown(
                    label="Quick Directory Select",
                    choices=get_directory_list(),
                    type="value",
                    allow_custom_value=True
                )
            
            with gr.Row():
                file_picker = gr.File(
                    label="Select Files to Upload",
                    file_count="multiple",
                    file_types=[
                        ".safetensors", ".ckpt", ".pt", ".bin",
                        ".zip", ".jpg", ".png"
                    ]
                )
            
            pr_message = gr.Textbox(
                label="Pull Request Message",
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
            
            def prepare_upload(username, repo, write_key, files, pr_message):
                if not files:
                    return "Please select files to upload"
                file_paths = [f.name for f in files]
                return upload_to_huggingface(username, repo, write_key, file_paths, pr_message)
            
            upload_button.click(
                fn=prepare_upload,
                inputs=[
                    username,
                    repository,
                    write_key,
                    file_picker,
                    pr_message
                ],
                outputs=result
            )

        return [(hf_interface, "HF Backup", "hf_backup_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)
