import launch

if not launch.is_installed("apscheduler"):
    launch.run_pip("install apscheduler", "requirements for Hugging Face Backup")

if not launch.is_installed("huggingface_hub"):
    launch.run_pip("install huggingface_hub", "requirements for Hugging Face Backup")
