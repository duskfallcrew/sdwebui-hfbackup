from modules import script_callbacks, shared

def on_ui_settings():
    section = ("huggingface", "🤗 Hugging Face Credentials")
    
    if not hasattr(shared.opts, "hf_username"):
        shared.opts.add_option(
            "hf_username",
            shared.OptionInfo(
                "",
                "Hugging Face Username",
                section=section
            )
        )
    
    if not hasattr(shared.opts, "hf_write_token"):
        shared.opts.add_option(
            "hf_write_token",
            shared.OptionInfo(
                "",
                "Hugging Face Write Token",
                section=section
            )
        )

script_callbacks.on_ui_settings(on_ui_settings)
