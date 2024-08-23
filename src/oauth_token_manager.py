import os
import yaml
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class OAuthTokenManager:
    def __init__(self):
        """
        Initializes the OAuthTokenManager by loading configuration constants from file path.
        """
        base_path = os.path.dirname(__file__)
        self.config_file = os.path.join(base_path, 'constants.yaml')
        self.credentials_file = os.path.join(base_path, 'client.json')
        self.token_file = os.path.join(base_path, 'token.json')
        self.constants = self.load_config()

    def load_config(self):
        """
        Loads the configuration constants from the YAML file.

        Returns:
            dict: A dictionary containing the configuration constants.
        """
        try:
            with open(self.config_file, "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise RuntimeError(f"Configuration file '{self.config_file}' not found.")
        except yaml.YAMLError as error:
            raise RuntimeError(f"Error parsing the YAML configuration file: {error}")

    def save_token(self, creds):
        """
        Saves the OAuth credentials to a JSON file.

        Args:
            creds (Credentials): The OAuth credentials to save.
        """
        try:
            with open(self.token_file, "w+") as token:
                token.write(creds.to_json())
                return
        except IOError as error:
            raise RuntimeError(f"Error saving the token to '{self.token_file}': {error}")

    def generate_new_token(self):
        """
        Generates a new OAuth token by prompting the user to log in via the browser.

        Returns:
            bool: True if the token was successfully generated and saved, False otherwise.
        """
        try:
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.constants["SCOPE"])
            creds = flow.run_local_server(port=0)
            self.save_token(creds)
            return True
        except Exception as error:
            logging.error(f"Error generating a new token: {error}")
            return False

    def get_valid_credentials(self):
        """
        Validates and retrieves the OAuth credentials. Generates a new token if none exist.

        Returns:
            Credentials: The valid OAuth credentials.

        Raises:
            RuntimeError: If the credentials could not be retrieved or validated.
        """
        if not os.path.exists(self.token_file):
            if not self.generate_new_token():
                raise RuntimeError("Failed to generate a new OAuth token.")
        try:
            creds = Credentials.from_authorized_user_file(self.token_file, self.constants["SCOPE"])
            return creds
        except Exception as error:
            raise RuntimeError(f"Error loading credentials: {error}")


