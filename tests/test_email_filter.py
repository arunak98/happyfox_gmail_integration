import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import yaml
from src.email_filter import EmailFilter


class TestEmailFilter(unittest.TestCase):

    @patch("src.oauth_token_manager.OAuthTokenManager.validate_credentials", return_value=MagicMock())
    @patch("builtins.open", new_callable=mock_open,
           read_data="Fields_References: {field1: 'field1_value'}\nCONDITION_SYMBOL: {predicate1: '>'}")
    def test_init_success(self, mock_open, mock_validate_credentials):
        # Mock the rules JSON file
        with patch("builtins.open", mock_open(read_data=json.dumps({
            "rule1": {"criteria": [{"field_name": "field1", "predicate": "predicate1", "value": "10"}]}
        }))):
            filter_instance = EmailFilter()
            self.assertIsNotNone(filter_instance.credentials)
            self.assertIn('Fields_References', filter_instance.constants)
            self.assertIn('CONDITION_SYMBOL', filter_instance.constants)
            self.assertIn('rule1', filter_instance.rules)

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
        "rule1": {"criteria": [{"field_name": "field1", "predicate": "Greater than", "value": "10"}]}
    }))
    def test_validate_rules_success(self, mock_open):
        with patch("src.oauth_token_manager.OAuthTokenManager.validate_credentials", return_value=MagicMock()):
            filter_instance = EmailFilter()
            # If there are no exceptions raised, the rules are valid
            self.assertTrue(True)

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
        "rule1": {"criteria": [{"field_name": "field1", "predicate": "Greater than", "value": "invalid"}]}
    }))
    def test_validate_rules_invalid_value(self, mock_open):
        with patch("src.oauth_token_manager.OAuthTokenManager.validate_credentials", return_value=MagicMock()):
            with self.assertRaises(TypeError):
                EmailFilter()

    @patch("sqlite3.connect")
    def test_search_emails(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1,), (2,)]
        mock_connect.return_value.cursor.return_value = mock_cursor

        filter_instance = EmailFilter()
        emails = filter_instance.search_emails("All", [{"field_name": "field1", "predicate": ">", "value": "10"}])

        self.assertEqual(len(emails), 2)
        self.assertEqual(emails[0]['message_id'], 1)
        self.assertEqual(emails[1]['message_id'], 2)

    @patch("src.email_filter.EmailFilter.search_emails", return_value=[{'message_id': '123'}])
    @patch("googleapiclient.discovery.build")
    def test_apply_filters(self, mock_build, mock_search_emails):
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        filter_instance = EmailFilter()
        result = filter_instance.apply_filters()

        self.assertTrue(result)
        mock_search_emails.assert_called_once()
        mock_service.users().messages().modify().execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()
