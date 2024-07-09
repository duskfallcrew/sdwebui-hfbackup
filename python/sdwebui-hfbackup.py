import os
import glob
from huggingface_hub import HfApi

def upload_ckpts(username, repository, write_key, dir_picker, files, file_type_picker, pr_message):
    repo_id = f"{username}/{repository}"
    api = HfApi(token=write_key)

    # Get the list of files in the selected directory
    file_list = glob.glob(os.path.join(dir_picker, f"*.{file_type_picker}"))

    # Upload the files to Hugging Face Hub
    for file in file_list:
        print(f"Uploading to HF: huggingface.co/{repo_id}/{file}")
        response = api.upload_file(
            path_or_fileobj=file,
            path_in_repo=file,
            repo_id=repo_id,
            repo_type=None,
            create_pr=1,
            commit_message=pr_message
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
        gr.Filebox(label="Select Directory", multiple=False, type="directory"),
        gr.Filebox(label="Checkpoint Files", multiple=True),
        gr.Radio(label="File Type", choices=["zip", "pt", "ckpt", "safetensors", "bin"], type="index"),
        gr.Textbox(label="Pull Request Message")
    ],
    outputs="text",
    title="Hugging Face Hub Uploader",
    description="Upload your checkpoint files to the Hugging Face Hub"
)

iface.launch()
