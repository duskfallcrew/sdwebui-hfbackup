import gradio as gr
import os
from modules import shared, script_callbacks
from huggingface_hub import HfApi
import glob

def on_ui_settings():
    section = ('huggingface', "Hugging Face")
    shared.opts.add_option(
        "hf_write_key",
        shared.OptionInfo(
            "",
            "Hugging Face Write API Key",
            gr.Password,  # Changed to Password type for security
            {"interactive": True},
            section=section
        )
    )
    shared.opts.add_option(
        "hf_read_key",
        shared.OptionInfo(
            "",
            "Hugging Face Read API Key",
            gr.Password,  # Changed to Password type for security
            {"interactive": True},
            section=section
        )
    )

script_callbacks.on_ui_settings(on_ui_settings)
