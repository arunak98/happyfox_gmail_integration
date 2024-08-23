import unittest
from unittest.mock import patch, MagicMock, call
from email.parser import Parser
import base64
import re
from datetime import datetime
from src.email_fetcher import EmailFetcher


class TestFetchEmails(unittest.TestCase):

    def setUp(self):
        self.manager = EmailFetcher()
        self.manager.creds = MagicMock()
        self.mock_service = MagicMock()
        self.mock_messages = [
            {"id": "message1"},
        ]
        self.mock_raw_message = {
            "raw": base64.urlsafe_b64encode(
                "From: test@example.com\nTo: recipient@example.com\nDate: Mon, 21 Aug 2023 12:34:56 +0000\nSubject: Test\nContent-Type: text/plain\n\nThis is a test email.".encode(
                    "UTF-8")).decode("UTF-8"),
            "id": "message1",
            "labelIds": ["INBOX"]
        }
        self.mock_parsed_message = Parser().parsestr(
            base64.urlsafe_b64decode(self.mock_raw_message["raw"]).decode("UTF-8")
        )

    @patch('src.email_fetcher.build')
    @patch('src.email_fetcher.EmailFetcher.create_table')
    @patch('src.email_fetcher.EmailFetcher.save_to_database')
    def test_fetch_emails_success(self, mock_save_to_database, mock_create_table, mock_build):
        # Arrange
        mock_build.return_value = self.mock_service
        self.mock_service.users.return_value.messages.return_value.list.return_value.execute.return_value = {
            "messages": self.mock_messages}
        self.mock_service.users.return_value.messages.return_value.get.return_value.execute.return_value = self.mock_raw_message

        with patch('src.email_fetcher.message_from_string', return_value=self.mock_parsed_message):
            # Act
            self.manager.fetch_emails()

            # Assert
            mock_create_table.assert_called_once()
            mock_build.assert_called_once_with('gmail', 'v1', credentials=self.manager.creds)
            self.mock_service.users.return_value.messages.return_value.list.assert_called_once_with(userId='me',
                                                                                                    labelIds=['INBOX'],
                                                                                                    maxResults=50)
            self.mock_service.users.return_value.messages.return_value.get.assert_called_with(userId='me',
                                                                                              id='message1',
                                                                                              format='raw')

            expected_data = [{
                "from_id": "test@example.com",
                "to_id": "recipient@example.com",
                "date": "2023-08-21 12:34",
                "message_id": "message1",
                "content_type": "text/plain",
                "content": "This is a test email.",
                "subject": "Test",
                "labels": "INBOX"
            }]
            mock_save_to_database.assert_called_once_with(expected_data)

    @patch('src.email_fetcher.build')
    @patch('src.email_fetcher.EmailFetcher.create_table')
    @patch('src.email_fetcher.EmailFetcher.save_to_database')
    def test_fetch_emails_no_messages(self, mock_save_to_database, mock_create_table, mock_build):
        # Arrange
        mock_build.return_value = self.mock_service
        self.mock_service.users.return_value.messages.return_value.list.return_value.execute.return_value = {
            "messages": []}

        # Act
        self.manager.fetch_emails()

        # Assert
        mock_create_table.assert_called_once()
        mock_build.assert_called_once_with('gmail', 'v1', credentials=self.manager.creds)
        self.mock_service.users.return_value.messages.return_value.list.assert_called_once_with(userId='me',
                                                                                                labelIds=['INBOX'],
                                                                                                maxResults=50)
        mock_save_to_database.assert_called_once_with([])

    @patch('src.email_fetcher.build')
    @patch('src.email_fetcher.logging.error')
    def test_fetch_emails_exception(self, mock_logging_error, mock_build):
        # Arrange
        mock_build.side_effect = Exception("An error occurred")

        # Act
        self.manager.fetch_emails()

        # Assert
        mock_logging_error.assert_called_once_with("Error fetching emails: An error occurred")


if __name__ == '__main__':
    unittest.main()
