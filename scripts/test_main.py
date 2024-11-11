import unittest
from unittest.mock import patch, MagicMock
import os
from main import get_directory_list, get_files_in_directory, upload_to_huggingface
from huggingface_hub import HfApi


class TestHFBackup(unittest.TestCase):

    @patch('os.path.exists', return_value=True)
    @patch('os.path.abspath')
    @patch('scripts.hf_backup.scripts.basedir', return_value='/fake/path')
    def test_get_directory_list(self, mock_basedir, mock_abspath, mock_exists):
        """Test that the correct directories are listed and exist."""
        expected_dirs = [
            '/fake/path/models/Stable-diffusion',
            '/fake/path/models/Lora',
            '/fake/path/embeddings',
            '/fake/path/extensions',
            '/fake/path/textual_inversion'
        ]

        mock_abspath.side_effect = lambda x: x  # Return paths as-is
        dirs = get_directory_list()

        self.assertEqual(dirs, sorted(expected_dirs))

    @patch('os.path.exists', return_value=True)
    @patch('os.walk')
    def test_get_files_in_directory(self, mock_walk, mock_exists):
        """Test that the function filters files with relevant extensions."""
        mock_walk.return_value = [
            ('/fake/path', [], ['file1.safetensors', 'file2.ckpt', 'file3.txt', 'file4.pt'])
        ]

        expected_files = [
            {"value": '/fake/path/file1.safetensors', "label": 'file1.safetensors'},
            {"value": '/fake/path/file2.ckpt', "label": 'file2.ckpt'},
            {"value": '/fake/path/file4.pt', "label": 'file4.pt'}
        ]

        files = get_files_in_directory('/fake/path')

        self.assertEqual(files, expected_files)

    @patch('huggingface_hub.HfApi.upload_file')
    @patch('huggingface_hub.HfApi.create_repo')
    @patch('scripts.hf_backup.shared.opts')
    def test_upload_to_huggingface(self, mock_opts, mock_create_repo, mock_upload_file):
        """Test that files are uploaded to Hugging Face."""
        mock_opts.hf_username = "test_user"
        mock_opts.hf_write_token = "fake_token"

        selected_files = ["/fake/path/file1.safetensors", "/fake/path/file2.ckpt"]

        def fake_progress(progress, desc=""):
            pass  # Mock progress function

        result = upload_to_huggingface("test_repo", selected_files, "Backup commit", progress=fake_progress)

        # Ensure the repository was created or accessed
        mock_create_repo.assert_called_once_with("test_user/test_repo", private=True, exist_ok=True)

        # Ensure both files were uploaded
        self.assertEqual(mock_upload_file.call_count, len(selected_files))

        # Check that the result indicates successful uploads
        self.assertIn("✓ Successfully uploaded", result)

    @patch('huggingface_hub.HfApi.upload_file', side_effect=Exception("Upload failed"))
    @patch('huggingface_hub.HfApi.create_repo')
    @patch('scripts.hf_backup.shared.opts')
    def test_upload_to_huggingface_with_error(self, mock_opts, mock_create_repo, mock_upload_file):
        """Test that errors during file upload are handled gracefully."""
        mock_opts.hf_username = "test_user"
        mock_opts.hf_write_token = "fake_token"

        selected_files = ["/fake/path/file1.safetensors"]

        def fake_progress(progress, desc=""):
            pass  # Mock progress function

        result = upload_to_huggingface("test_repo", selected_files, "Backup commit", progress=fake_progress)

        # Ensure the repository was created or accessed
        mock_create_repo.assert_called_once_with("test_user/test_repo", private=True, exist_ok=True)

        # Check that the result includes the error message
        self.assertIn("✗ Error uploading", result)
        self.assertIn("Upload failed", result)

if __name__ == "__main__":
    unittest.main()
