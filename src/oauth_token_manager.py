import os
import yaml
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class OAuthTokenManager:
    def __init__(self, config_file="src/constants.yaml", credentials_file="src/token_keys.json"):
        """
        Initializes the OAuthTokenManager by loading configuration constants from a YAML file.

        Args:
            config_file (str): Path to the YAML configuration file containing OAuth settings.
            credentials_file (str): Path to the file where OAuth tokens are stored.
        """
        self.config_file = config_file
        self.credentials_file = credentials_file
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
            with open(self.credentials_file, "w") as token_file:
                token_file.write(creds.to_json())
        except IOError as error:
            raise RuntimeError(f"Error saving the token to '{self.credentials_file}': {error}")

    def generate_new_token(self):
        """
        Generates a new OAuth token by prompting the user to log in via the browser.

        Returns:
            bool: True if the token was successfully generated and saved, False otherwise.
        """
        try:
            flow = InstalledAppFlow.from_client_secrets_file("client.json", self.constants["SCOPE"])
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
        if not os.path.exists(self.credentials_file):
            if not self.generate_new_token():
                raise RuntimeError("Failed to generate a new OAuth token.")
        try:
            creds = Credentials.from_authorized_user_file(self.credentials_file, self.constants["SCOPE"])
            return creds
        except Exception as error:
            raise RuntimeError(f"Error loading credentials: {error}")

# Usage example:
# oauth_manager = OAuthTokenManager()
# credentials = oauth_manager.get_valid_credentials()
