import unittest
from unittest.mock import patch, mock_open, MagicMock
from google.oauth2.credentials import Credentials
from src.oauth_token_manager import OAuthTokenManager


class TestOAuthTokenManager(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="scope: ['test_scope']")
    def test_load_config(self, mock_file):
        manager = OAuthTokenManager()
        self.assertEqual(manager.constants["scope"], ['test_scope'])

    @patch("builtins.open", new_callable=mock_open)
    def test_save_token(self, mock_file):
        manager = OAuthTokenManager()
        mock_creds = MagicMock(spec=Credentials)
        mock_creds.to_json.return_value = '{"token": "mock_token"}'
        manager.save_token(mock_creds)
        mock_file().write.assert_called_once_with('{"token": "mock_token"}')

    @patch("os.path.exists", return_value=False)
    @patch("your_module.OAuthTokenManager.generate_new_token", return_value=True)
    def test_get_valid_credentials_generate_new_token(self, mock_generate_new_token, mock_exists):
        manager = OAuthTokenManager()
        manager.get_valid_credentials()
        mock_generate_new_token.assert_called_once()

    @patch("os.path.exists", return_value=True)
    @patch("your_module.Credentials.from_authorized_user_file", return_value=MagicMock())
    def test_get_valid_credentials(self, mock_from_file, mock_exists):
        manager = OAuthTokenManager()
        creds = manager.get_valid_credentials()
        self.assertIsNotNone(creds)


if __name__ == "__main__":
    unittest.main()
