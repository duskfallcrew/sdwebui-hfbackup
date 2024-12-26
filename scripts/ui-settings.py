import gradio as gr
from modules import shared, script_callbacks

def on_ui_settings():
    section = ('huggingface', "Hugging Face")
    shared.opts.add_option(
        "hf_write_key",
        shared.OptionInfo(
            "",
            "Hugging Face Write API Key",
            gr.Password,
            {"interactive": True},
            section=section
        )
    )
    shared.opts.add_option(
        "hf_read_key",
        shared.OptionInfo(
            "",
            "Hugging Face Read API Key",
            gr.Password,
            {"interactive": True},
            section=section
        )
    )
    shared.opts.add_option(
        "git_credential_store",
        shared.OptionInfo(
            True,
            "Use Git Credential Store",
            gr.Checkbox,
            {"interactive": True},
            section=section
        )
    )

script_callbacks.on_ui_settings(on_ui_settings)
