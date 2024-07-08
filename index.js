const uploadComponent = {
  template: `
    <div>
      <input type="text" id="hf-username" placeholder="Hugging Face Username">
      <input type="text" id="hf-repo" placeholder="Hugging Face Repository">
      <input type="text" id="write-key" placeholder="Hugging Face Write Key">
      <input type="file" id="ckpt-files" multiple>
      <button id="upload-btn">Upload to Hugging Face Hub</button>
    </div>
  `,
  script: () => {
    const hfUsernameInput = document.getElementById('hf-username');
    const hfRepoInput = document.getElementById('hf-repo');
    const writeKeyInput = document.getElementById('write-key');
    const ckptFilesInput = document.getElementById('ckpt-files');
    const uploadBtn = document.getElementById('upload-btn');

    uploadBtn.addEventListener('click', async () => {
      const hfUsername = hfUsernameInput.value;
      const hfRepo = hfRepoInput.value;
      const writeKey = writeKeyInput.value;
      const ckptFiles = ckptFilesInput.files;

      try {
        const response = await api.uploadToHuggingFaceHub(hfUsername, hfRepo, writeKey, ckptFiles);
        console.log(response);
      } catch (error) {
        console.error(error);
      }
    });
  }
};
