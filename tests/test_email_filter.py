import unittest
from unittest.mock import patch, MagicMock, call
import sqlite3
from src.email_filter import EmailFilter


class TestEmailFilter(unittest.TestCase):

    def setUp(self):
        self.filter_manager = EmailFilter()
        self.filter_manager.db_path = 'file:testdb?mode=memory&cache=shared'
        self.filter_manager.rules = {
            "rule1": {
                "criteria": [{"predicate": "Greater than", "value": "10"}],
                "action": [{"addLabelIds": ["Label1"], "removeLabelIds": ["Label2"]}]
            }
        }

        self.connection = sqlite3.connect(self.filter_manager.db_path)
        self.cursor = self.connection.cursor()

        self.cursor.execute("DROP TABLE IF EXISTS inbox")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS inbox (message_id TEXT)")
        self.cursor.execute("INSERT INTO inbox (message_id) VALUES ('msg1'), ('msg2')")
        self.connection.commit()
        self.addCleanup(self.connection.close)

    @patch('src.email_filter.build')
    def test_apply_filters_success(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock the search_emails method
        with patch.object(self.filter_manager, 'search_emails', return_value=[{"message_id": "msg1"}]):
            result = self.filter_manager.apply_filters()

            self.assertTrue(result)
            mock_build.assert_called_once_with('gmail', 'v1', credentials=self.filter_manager.credentials)
            mock_service.users().messages().modify.assert_called_once_with(
                userId='me',
                id='msg1',
                body={"addLabelIds": ["Label1"], "removeLabelIds": ["Label2"]}
            )

    @patch('src.email_filter.build')
    def test_apply_filters_exception_handling(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock the search_emails method
        with patch.object(self.filter_manager, 'search_emails', return_value=[{"message_id": "msg1"}]):
            mock_service.users().messages().modify.side_effect = Exception("Modification error")
            result = self.filter_manager.apply_filters()

            self.assertTrue(result)
            mock_build.assert_called_once_with('gmail', 'v1', credentials=self.filter_manager.credentials)
            mock_service.users().messages().modify.assert_called_once_with(
                userId='me',
                id='msg1',
                body={"addLabelIds": ["Label1"], "removeLabelIds": ["Label2"]}
            )

    def test_search_emails(self):
        query_conditions = "message_id = 'msg1'"
        with patch.object(self.filter_manager, '_form_query_conditions', return_value=query_conditions):
            result = self.filter_manager.search_emails(predicate="Equals", conditions={"message_id": "msg1"})

            self.assertEqual(result, [{'message_id': 'msg1'}])

    def test_validate_rules_success(self):
        # No exceptions should be raised for valid rules
        self.filter_manager._validate_rules()

    def test_validate_rules_invalid_value(self):
        # Modify the rule to include an invalid value
        self.filter_manager.rules["rule1"]["criteria"][0]["value"] = "Not a number"

        with self.assertRaises(TypeError) as context:
            self.filter_manager._validate_rules()

        self.assertEqual(
            str(context.exception),
            "Invalid value for predicate 'Greater than' in rule 'rule1'"
        )


if __name__ == '__main__':
    unittest.main()
