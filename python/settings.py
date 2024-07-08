import modules.scripts as scripts
import gradio as gr
import os

from modules import shared
from modules import script_callbacks

def on_ui_settings():
    section = ('huggingface', "Hugging Face")
    shared.opts.add_option(
        "hf_write_key",
        shared.OptionInfo(
            "",
            "Hugging Face Write API Key",
            gr.Textbox,
            {"interactive": True},
            section=section)
    )
    shared.opts.add_option(
        "hf_read_key",
        shared.OptionInfo(
            "",
            "Hugging Face Read API Key",
            gr.Textbox,
            {"interactive": True},
            section=section)
    )

script_callbacks.on_ui_settings(on_ui_settings)