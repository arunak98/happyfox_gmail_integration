import sqlite3
import os
import yaml
import json
import logging
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from src.oauth_token_manager import OAuthTokenManager


class EmailFilter:

    def __init__(self):
        # Check and validate credentials
        self.credentials = OAuthTokenManager().validate_credentials()

        # Load constants from YAML file
        with open("src/constants.yaml", "r") as file:
            self.constants = yaml.safe_load(file)

        # Load and validate rules from JSON file
        with open("src/rules/rules.json", "r") as file:
            self.rules = json.load(file)
        self._validate_rules()

    def _validate_rules(self):
        """Validate the rules format and criteria."""
        for rule_name, rule_data in self.rules.items():
            for criterion in rule_data.get("criteria", []):
                predicate = criterion.get("predicate")
                value = criterion.get("value")
                if predicate in ["Greater than", "Less than"] and not value.isdigit():
                    raise TypeError(f"Invalid value for predicate '{predicate}' in rule '{rule_name}'")

    def search_emails(self, predicate, conditions):
        """Search emails in the database based on given criteria."""
        query_conditions = self._form_query_conditions(predicate, conditions)

        # Establish SQLite connection and execute query
        connection = sqlite3.connect("db_storage/email_db.sqlite3")
        cursor = connection.cursor()
        cursor.execute(f"SELECT message_id FROM inbox WHERE {query_conditions}")
        emails = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

        connection.close()
        return emails

    def _form_query_conditions(self, predicate, conditions):
        """Formulate SQL query conditions based on provided criteria."""
        query_parts = []

        for condition in conditions:
            field_name = self.constants['Fields_References'].get(condition['field_name'])
            predicate_symbol = self.constants['CONDITION_SYMBOL'].get(condition['predicate'])

            if condition['field_name'] == "Date Received":
                date_range = self._get_date_range(condition['predicate'], int(condition['value']))
                query_parts.append(f"{field_name} BETWEEN '{date_range[0]}' AND '{date_range[1]}'")
            else:
                condition_value = condition['value']
                if predicate_symbol == 'like':
                    query_parts.append(f"{field_name} {predicate_symbol} '%{condition_value}%'")
                else:
                    query_parts.append(f"{field_name} {predicate_symbol} '{condition_value}'")

        return " AND ".join(query_parts) if predicate == "All" else " OR ".join(query_parts)

    @staticmethod
    def _get_date_range(predicate, value):
        """Calculate date range based on the predicate and value."""
        current_date = datetime.now()
        if predicate == "Greater than":
            return current_date.strftime("%Y-%m-%d"), (current_date + timedelta(days=value)).strftime("%Y-%m-%d")
        else:
            return (current_date - timedelta(days=value)).strftime("%Y-%m-%d"), current_date.strftime("%Y-%m-%d")

    def apply_filters(self):
        """Apply the defined filters to the emails and modify them based on actions."""
        service = build('gmail', 'v1', credentials=self.credentials)

        for rule_name, rule_data in self.rules.items():
            filtered_emails = self.search_emails(rule_data.get("predicates"), rule_data.get("criteria"))

            # Apply actions to filtered emails
            for email in filtered_emails:
                for action in rule_data.get("actions", []):
                    try:
                        service.users().messages().modify(
                            userId='me',
                            id=email["message_id"],
                            body={"addLabelIds": action.get('addLabelIds', []), "removeLabelIds": action.get("removeLabelIds", [])}
                        ).execute()
                    except Exception as error:
                        logging.error(f"Error modifying email with ID {email['message_id']}: {error}")

        return True


if __name__ == "__main__":
    EmailFilter().apply_filters()
