import gradio as gr
from modules import shared, script_callbacks

def on_ui_settings():
    section = ('huggingface', "Hugging Face")
    shared.opts.add_option(
        "hf_write_key",
        shared.OptionInfo(
            "",
            "Hugging Face Write API Key",
            gr.Textbox,
            {"interactive": True, "type": "password", "lines": 1},
            section=section
        )
    )

script_callbacks.on_ui_settings(on_ui_settings)
