import os
import glob
from huggingface_hub import HfApi

def upload_ckpts(username, repository, write_key, files):
    repo_id = f"{username}/{repository}"
    api = HfApi(token=write_key)
    for file in files:
        print(f"Uploading to HF: huggingface.co/{repo_id}/{file}")
        response = api.upload_file(
            path_or_fileobj=file,
            path_in_repo=file,
            repo_id=repo_id,
            repo_type=None,
            create_pr=1,
            commit_message="Upload with 🤗 Earth & Dusk's Amazing HF Backup for Vast & Runpod"
        )
        print(response)
    print("DONE")
    print("Go to your repo and accept the PRs this created to see your files")

# Create a Gradio interface
import gradio as gr

iface = gr.Interface(
    fn=upload_ckpts,
    inputs=[
        gr.Textbox(label="Hugging Face Username"),
        gr.Textbox(label="Hugging Face Repository"),
        gr.Textbox(label="Hugging Face Write Key"),
        gr.Filebox(label="Checkpoint Files", multiple=True)
    ],
    outputs="text",
    title="Hugging Face Hub Uploader",
    description="Upload your checkpoint files to the Hugging Face Hub"
)

iface.launch()
