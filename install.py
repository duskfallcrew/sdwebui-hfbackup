import launch

if not launch.is_installed("huggingface_hub"):
    launch.run_pip("install huggingface_hub==4.30.2", "requirements for Hugging Face Hub Uploader")

if not launch.is_installed("glob2"):
    launch.run_pip("install glob2", "requirements for Hugging Face Hub Uploader")

launch.run_pip("install -r requirements.txt")
