import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
from src.oauth_token_manager import OAuthTokenManager


class TestOAuthTokenManager(unittest.TestCase):

    def setUp(self):
        self.manager = OAuthTokenManager()
        self.mock_credentials = MagicMock()
        self.mock_scope = ["https://www.googleapis.com/auth/some_scope"]

    @patch('os.path.exists', return_value=True)
    @patch('src.oauth_token_manager.Credentials.from_authorized_user_file')
    def test_get_valid_credentials_existing_token(self, mock_from_authorized_user_file, mock_exists):
        # Arrange
        mock_from_authorized_user_file.return_value = self.mock_credentials
        self.manager.constants["SCOPE"] = self.mock_scope

        # Act
        creds = self.manager.get_valid_credentials()

        # Assert
        mock_exists.assert_called_once_with(self.manager.token_file)
        mock_from_authorized_user_file.assert_called_once_with(self.manager.token_file, self.mock_scope)
        self.assertEqual(creds, self.mock_credentials)

    @patch('os.path.exists', return_value=False)
    @patch('src.oauth_token_manager.OAuthTokenManager.generate_new_token', return_value=True)
    @patch('src.oauth_token_manager.Credentials.from_authorized_user_file')
    def test_get_valid_credentials_generate_new_token(self, mock_from_authorized_user_file, mock_generate_new_token,
                                                      mock_exists):
        # Arrange
        mock_from_authorized_user_file.return_value = self.mock_credentials
        self.manager.constants["SCOPE"] = self.mock_scope

        # Act
        creds = self.manager.get_valid_credentials()

        # Assert
        mock_exists.assert_called_once_with(self.manager.token_file)
        mock_generate_new_token.assert_called_once()
        mock_from_authorized_user_file.assert_called_once_with(self.manager.token_file, self.mock_scope)
        self.assertEqual(creds, self.mock_credentials)

    @patch('os.path.exists', return_value=False)
    @patch('src.oauth_token_manager.OAuthTokenManager.generate_new_token', return_value=False)
    def test_get_valid_credentials_generate_new_token_fail(self, mock_generate_new_token, mock_exists):
        # Arrange
        self.manager.constants["SCOPE"] = self.mock_scope

        # Act & Assert
        with self.assertRaises(RuntimeError) as context:
            self.manager.get_valid_credentials()

        self.assertTrue("Failed to generate a new OAuth token." in str(context.exception))
        mock_exists.assert_called_once_with(self.manager.token_file)
        mock_generate_new_token.assert_called_once()

    @patch('src.oauth_token_manager.InstalledAppFlow.from_client_secrets_file')
    @patch('src.oauth_token_manager.OAuthTokenManager.save_token')
    def test_generate_new_token_success(self, mock_save_token, mock_from_client_secrets_file):
        # Arrange
        mock_flow = MagicMock()
        mock_creds = MagicMock()
        mock_flow.run_local_server.return_value = mock_creds
        mock_from_client_secrets_file.return_value = mock_flow
        self.manager.constants["SCOPE"] = self.mock_scope

        # Act
        result = self.manager.generate_new_token()

        # Assert
        mock_from_client_secrets_file.assert_called_once_with(self.manager.credentials_file, self.mock_scope)
        mock_flow.run_local_server.assert_called_once_with(port=0)
        mock_save_token.assert_called_once_with(mock_creds)
        self.assertTrue(result)

    @patch('src.oauth_token_manager.InstalledAppFlow.from_client_secrets_file')
    def test_generate_new_token_failure(self, mock_from_client_secrets_file):
        # Arrange
        mock_from_client_secrets_file.side_effect = Exception("An error occurred")
        self.manager.constants["SCOPE"] = self.mock_scope

        # Act
        result = self.manager.generate_new_token()

        # Assert
        mock_from_client_secrets_file.assert_called_once_with(self.manager.credentials_file, self.mock_scope)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
