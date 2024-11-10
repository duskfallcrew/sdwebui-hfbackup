# scripts/settings.py
from modules import shared, script_callbacks
import gradio as gr

def on_ui_settings():
    section = ('huggingface', "Hugging Face Settings")
    
    shared.opts.add_option(
        "hf_write_key",
        shared.OptionInfo(
            default="",
            label="Hugging Face Write API Key",
            component=gr.Password,
            component_args={"interactive": True, "type": "password"},
            section=section
        )
    )
    
    shared.opts.add_option(
        "hf_default_username",
        shared.OptionInfo(
            default="",
            label="Default Hugging Face Username",
            component=gr.Textbox,
            component_args={"interactive": True},
            section=section
        )
    )
    
    shared.opts.add_option(
        "hf_default_repo",
        shared.OptionInfo(
            default="sd-models-backup",
            label="Default Repository Name",
            component=gr.Textbox,
            component_args={"interactive": True},
            section=section
        )
    )

script_callbacks.on_ui_settings(on_ui_settings)
