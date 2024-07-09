import modules.scripts as scripts
import gradio as gr
import os

from modules import script_callbacks

def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as ui_component:
        with gr.Row():
            dir_picker = gr.Filebox(label="Select Directory", multiple=False, type="directory")
            file_picker = gr.Filebox(label="Select Files to Upload", multiple=True)
            file_type_picker = gr.Radio(
                label="File Type",
                choices=["zip", "pt", "ckpt", "safetensors", "bin","jpg","png"],
                type="index"
            )
            repo_description = gr.Textbox(label="Repository Description")
            user_org_name = gr.Textbox(label="User or Organization Name")
            pr_message = gr.Textbox(label="Pull Request Message")
            # Add more UI components as needed
        return [(ui_component, "Hugging Face Hub Uploader", "hf_hub_uploader_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)