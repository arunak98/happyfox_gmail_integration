import base64
import os
import re
import sqlite3
import logging
from datetime import datetime
from email import message_from_string

import pandas as pd
from googleapiclient.discovery import build

from src.oauth_token_manager import OAuthTokenManager


class EmailFetcher:
    def __init__(self):
        """
        Initializes the InboxFetcher by checking OAuth credentials.
        """
        base_path = os.path.dirname(__file__)
        self.db_path = os.path.join(base_path, 'email_db.db')
        self.creds = OAuthTokenManager().get_valid_credentials()

    def fetch_emails(self, max_results=50):
        """
        Fetches emails from the Gmail inbox and stores them in a SQLite database.

        Args:
            max_results (int): The maximum number of emails to fetch.
        """
        try:
            # Create the table if it doesn't exist (only when starting the application)
            self.create_table()

            service = build('gmail', 'v1', credentials=self.creds)
            message_data = service.users().messages().list(userId='me', labelIds=['INBOX'],
                                                           maxResults=max_results).execute()
            messages = message_data.get('messages', [])

            inbox_data = []

            for message in messages:
                content_data = {}
                raw_message = service.users().messages().get(userId='me', id=message["id"], format="raw").execute()
                parsed_message = message_from_string(base64.urlsafe_b64decode(raw_message.get("raw")).decode("UTF-8"))

                if isinstance(parsed_message.get_payload(), list):
                    # Skipping this part as some emails have multiple payloads.
                    pass
                else:
                    date_match = re.findall(r",(.*)\+", parsed_message.get("Date"))
                    if date_match:
                        date = date_match[0].strip()
                        content_data = {
                            "from_id": parsed_message.get("From"),
                            "to_id": parsed_message.get("To"),
                            "date": datetime.strptime(date, "%d %b %Y %H:%M:%S").strftime("%Y-%m-%d %H:%M"),
                            "message_id": raw_message.get("id"),
                            "content_type": parsed_message.get("Content-Type"),
                            "content": parsed_message.get_payload(),
                            "subject": parsed_message.get("Subject"),
                            "labels": ",".join(raw_message.get("labelIds"))
                        }
                        inbox_data.append(content_data)
                    else:
                        continue

            self.save_to_database(inbox_data)

        except Exception as error:
            logging.error(f"Error fetching emails: {error}")

    def create_table(self):
        """
        Creates the inbox table in the SQLite database if it doesn't exist.
        """
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()

                # Check if the table exists
                cursor.execute("""
                           SELECT name FROM sqlite_master 
                           WHERE type='table' AND name='inbox';
                       """)
                if cursor.fetchone() is None:
                    cursor.execute("""
                               CREATE TABLE inbox (
                                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                                   message_id TEXT,
                                   from_id TEXT,
                                   to_id TEXT,
                                   date TEXT,
                                   content_type TEXT,
                                   content TEXT,
                                   subject TEXT,
                                   labels TEXT
                               )
                           """)
                    connection.commit()
                cursor.close()

        except Exception as error:
            logging.error(f"Error creating table: {error}")

    def save_to_database(self, inbox_data):
        """
        Saves the fetched email data to the SQLite database.

        Args:
            inbox_data (list): List of dictionaries containing email data.
        """
        try:
            connection = sqlite3.connect(self.db_path)
            email_df = pd.DataFrame.from_records(inbox_data)
            email_df.to_sql("inbox", con=connection, if_exists='append', index=False)
        except Exception as error:
            logging.error(f"Error saving data to the database: {error}")
        finally:
            connection.close()


# Usage example:
if __name__ == "__main__":
    fetcher = EmailFetcher()
    fetcher.fetch_emails()
