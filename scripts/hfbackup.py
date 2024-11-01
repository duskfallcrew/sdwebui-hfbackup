# scripts/hf_backup.py
import modules.scripts as scripts
import gradio as gr
import os
from modules import shared, script_callbacks
from huggingface_hub import HfApi
import glob

def upload_to_huggingface(username, repo, write_key, dir_path, file_type, pr_message):
    try:
        # Initialize HF API
        api = HfApi(token=write_key or shared.opts.data.get("hf_write_key", ""))
        if not api.token:
            return "Error: No Hugging Face Write API Key provided"

        repo_id = f"{username}/{repo}"
        results = []
        
        # Get files from directory
        if dir_path:
            files = glob.glob(os.path.join(dir_path, f"*.{file_type}"))
            if not files:
                return f"No .{file_type} files found in {dir_path}"
                
            for file_path in files:
                try:
                    file_name = os.path.basename(file_path)
                    results.append(f"Uploading: {file_name}")
                    
                    response = api.upload_file(
                        path_or_fileobj=file_path,
                        path_in_repo=file_name,
                        repo_id=repo_id,
                        create_pr=True,
                        commit_message=pr_message or f"Upload {file_name}"
                    )
                    results.append(f"✓ Successfully uploaded {file_name}")
                    
                except Exception as e:
                    results.append(f"✗ Error uploading {file_name}: {str(e)}")
        
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
                dir_picker = gr.Textbox(
                    label="Directory Path",
                    placeholder="Path to directory containing files"
                )
                file_type = gr.Radio(
                    label="File Type",
                    choices=["safetensors", "ckpt", "pt", "bin", "zip", "jpg", "png"],
                    value="safetensors",
                    type="value"
                )
            
            pr_message = gr.Textbox(
                label="Pull Request Message",
                placeholder="Description of your upload",
                value="Backup files"
            )
            
            upload_button = gr.Button("🚀 Upload to Hugging Face")
            result = gr.Textbox(label="Results", interactive=False)
            
            upload_button.click(
                fn=upload_to_huggingface,
                inputs=[
                    username,
                    repository,
                    write_key,
                    dir_picker,
                    file_type,
                    pr_message
                ],
                outputs=result
            )

        return [(hf_interface, "HF Backup", "hf_backup_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)
