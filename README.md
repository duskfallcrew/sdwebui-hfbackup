# Hugging Face Backup Extension for Stable Diffusion WebUI

Welcome to our unique extension, designed to help you easily back up your valuable Stable Diffusion WebUI files to the Hugging Face Hub! This project is brought to you by the Duskfall Portal Crew, a diverse DID system passionate about creativity and AI.

<img width="1283" alt="Screenshot 2024-11-10 at 15 02 44" src="https://github.com/user-attachments/assets/79c32865-cf54-4a7b-aa9d-32e971210926">

## About This Extension

This extension provides a simple way to back up your Stable Diffusion WebUI models, embeddings, and other important files to a repository on the Hugging Face Hub. We prioritize ease of use and reliability, helping you safeguard your valuable work.

## Key Features

*   **Easy Backup:** Back up your model files, VAEs, embeddings, and LoRAs directly from your Stable Diffusion WebUI.
*   **Hugging Face Integration:** Seamlessly upload your files to your Hugging Face Hub repository.
*   **Automatic Backup (Manual Start):** Backups are performed automatically in the background, after you manually start them using the UI.
*   **Granular Status Updates:** Clear progress information provided during the backup process.
*   **Credential Store:** The extension uses the git credential store for secure authentication, and you can opt-out by using an environment variable.

## Getting Started

1.  **Install:** Install this extension by placing it in the `extensions` folder of your Stable Diffusion WebUI.
2.  **Configure:**
    *   In the Stable Diffusion WebUI settings, go to the `Hugging Face` section and set your write access token.
    *   In the extension's UI tab, configure your Hugging Face username, repository name, paths to back up, and the SD Webui folder.
3. **Start Backup:** Click the "Start Backup" button to begin backing up your files.

## Requirements

*   Stable Diffusion WebUI (Automatic1111)
*   Hugging Face Hub account and a write access token.
*   Python 3.7 or later.

## How it Works

1. **Configuration:** When you start the extension, it will load the required settings.
2.  **Cloning or Creation:** The extension will clone the provided Hugging Face repository, or create it if it doesn't exist.
3.  **Copy Files:** The files in the specified paths will be copied to the cloned repository.
4.  **Pushing:** The changes will be pushed to your repository in the Hugging Face Hub.
5. **Scheduled backups** By default, backups are done when the user triggers them, and then after a specified interval, you can configure that interval by modifying the  `BACKUP_INTERVAL` constant in your `hfbackup_script.py` file, or by implementing a scheduler.

## Settings

### Hugging Face Settings
*  **Hugging Face Write API Key:** Required to upload to your Hugging Face Repository.
* **Use Git Credential Store:** By default the extension will try to use your system's git credentials, but you can disable this behavior by turning this toggle off, and use the environment variable `HF_TOKEN` to provide the token.

### Extension settings
* **Huggingface Token**: Your Huggingface token.
* **Huggingface Username:** Your Huggingface username or organization name.
* **SD Webui Path:** The folder where Stable Diffusion Webui is installed.
*   **Backup Paths:** The paths to your models, embeddings, etc. that you wish to back up (one path per line), it must be relative to the root folder where Stable Diffusion is installed.

## License

This extension is licensed under the MIT License.

## Acknowledgments

This extension is built with the help of the Automatic1111 and Hugging Face communities. We are grateful for their efforts in creating such amazing and useful projects.

## Support

If you encounter any issues or have questions about this extension, please open an issue in our GitHub repository.

## Known Issues

*   No "BACK END" settings file: Settings are saved in the script and are loaded directly by A1111.
*   Currently, the backup occurs only when the user clicks the "Start Backup" button, and then on a timer, until the extension stops.

## Changelog

*   **Initial release:** *June 8 2024*
*   **Pre Alpha:** *June 8 2024* - "NOT OFFICIALLY A RELEASE"
*   **Rejig:** *November 1 2024* - Rejigged the code via Claude, will test asap and add feature logs.
*   **Semi Working:** *November 10 2024* - Tested it on A1111, it's SEMI working

## About & Links

### About Us

We are the Duskfall Portal Crew, a DID system with over 300 alters, navigating life with DID, ADHD, Autism, and CPTSD. We believe in AI’s potential to break down barriers and enhance mental health.

#### Join Our Community

*   **Website:** [End Media](https://end-media.org/) (WEBSITE UNDER CONSTRUCTION)
*   **Discord:** [Join our Discord](https://discord.gg/5t2kYxt7An)
*   **Hugging Face:** [Hugging Face](https://huggingface.co/EarthnDusk)
*  **Support Us:** [Send a Pizza](https://ko-fi.com/duskfallcrew/)
*  **Coffee:** [BuyMeSomeMochas!](https://www.buymeacoffee.com/duskfallxcrew)
*  **Patreon:** [Our Barely Used Patreon](https://www.patreon.com/earthndusk)

#### Community Groups

*  **Subreddit:** [Reddit](https://www.reddit.com/r/earthndusk/)
