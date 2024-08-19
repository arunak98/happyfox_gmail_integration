import unittest
from unittest.mock import patch, MagicMock
import sqlite3
import pandas as pd
from src.email_fetcher import EmailFetcher  # Replace with the actual module name


class TestEmailFetcher(unittest.TestCase):

    @patch("src.oauth_token_manager.OAuthTokenManager.get_valid_credentials", return_value=MagicMock())
    def test_init(self, mock_get_valid_credentials):
        fetcher = EmailFetcher()
        self.assertIsNotNone(fetcher.creds)

    @patch("googleapiclient.discovery.build")
    @patch("src.email_fetcher.EmailFetcher.save_to_database")
    def test_fetch_emails(self, mock_save_to_database, mock_build):
        # Mock Gmail API response
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.users().messages().list().execute.return_value = {'messages': [{'id': 'msg1'}, {'id': 'msg2'}]}
        mock_service.users().messages().get().execute.return_value = {
            "raw": base64.urlsafe_b64encode(b"Date, 01 Jan 2021 12:00:00 +0000").decode("utf-8"),
            "From": "test@example.com",
            "To": "recipient@example.com",
            "Date": "Date, 01 Jan 2021 12:00:00 +0000",
            "Content-Type": "text/plain",
            "Subject": "Test Subject",
            "labelIds": ["INBOX"]
        }

        fetcher = EmailFetcher()
        fetcher.fetch_emails(max_results=2)
        mock_save_to_database.assert_called_once()

    @patch("sqlite3.connect")
    def test_create_table(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        fetcher = EmailFetcher()
        fetcher.create_table()

        # Check that table creation was attempted
        mock_connection.cursor.return_value.execute.assert_any_call("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='inbox';
        """)
        mock_connection.cursor.return_value.execute.assert_any_call("""
            CREATE TABLE inbox (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE NOT NULL,
                e_from TEXT,
                e_to TEXT,
                e_date TEXT,
                content_type TEXT,
                content TEXT,
                subject TEXT,
                labels TEXT
            )
        """)

    @patch("sqlite3.connect")
    @patch("pandas.DataFrame.to_sql")
    def test_save_to_database(self, mock_to_sql, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        mock_to_sql.return_value = None

        inbox_data = [{
            "message_id": "msg1",
            "e_from": "test@example.com",
            "e_to": "recipient@example.com",
            "e_date": "2021-01-01 12:00",
            "content_type": "text/plain",
            "content": "Hello World",
            "subject": "Test Subject",
            "labels": "INBOX"
        }]

        fetcher = EmailFetcher()
        fetcher.save_to_database(inbox_data)

        mock_to_sql.assert_called_once_with("inbox", con=mock_connection, if_exists='append', index=False)


if __name__ == "__main__":
    unittest.main()
