import launch

if not launch.is_installed("huggingface_hub"):
    launch.run_pip("install huggingface_hub", "requirements for Hugging Face Hub Uploader")

if not launch.is_installed("glob"):
    launch.run_pip("install glob", "requirements for Hugging Face Hub Uploader")
