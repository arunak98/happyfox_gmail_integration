Here's the updated `README.md` with the necessary information on unit tests and refined structure:

---

# Gmail Email Fetching and Processing with OAuth 2.0

This project provides a solution to fetch emails from Gmail using OAuth 2.0 and the Google client API library, store them in a database, and process them based on user-defined rules.

## Prerequisites

1. **Google Cloud Credentials**:
    - Download the credentials file from the Google Cloud Platform (GCP) and rename it to `client.json`.
    - Place this file in the root directory of the project.

2. **Python Version**:
    - Ensure Python 3.8 or higher is installed.

3. **Install Dependencies**:
    - Run `pip install -r requirements.txt` to install the required Python packages.

## Project Structure

This repository contains three primary Python scripts:

1. **`oauth_token_manager.py`**:
    - Manages OAuth authentication and token handling.
    - Responsible for obtaining and refreshing the OAuth token and writing it to a JSON file for subsequent authentication requests.

2. **`email_fetcher.py`**:
    - Fetches emails from the Gmail inbox using the authenticated OAuth credentials.
    - Stores the fetched emails in an SQLite database (`email_db`).

3. **`email_filter.py`**:
    - Applies user-defined rules to the fetched emails.
    - Processes emails by parsing data from the database and applying actions like marking emails as read/unread or moving them to different labels using the Gmail REST API.

## Running the App

To use the application, follow these steps:

1. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2. **Fetch Emails from Gmail**:
    ```bash
    python email_fetcher.py
    ```
    - This script fetches emails from your Gmail inbox and stores them in the SQLite database.

3. **Apply Email Filtering Rules**:
    ```bash
    python email_filter.py
    ```
    - This script parses the stored emails and applies the rules defined in `rules.json` to modify the emails using the Gmail API.

## Testing

To ensure the functionality of the application, unit tests are provided for critical components. Follow these steps to run the tests:

1. **Install Testing Dependencies**:
    ```bash
    pip install -r requirements-test.txt
    ```

2. **Run Unit Tests**:
    ```bash
    python -m unittest discover
    ```
    - This will run all unit tests in the project to validate the functionality of the `OAuthTokenManager`, `EmailFetcher`, and `EmailFilter` classes.

## Unit Tests

### `oauth_token_manager.py`

- **Tests Provided**:
  - `test_load_config`: Verifies that the configuration is loaded correctly.
  - `test_save_token`: Ensures OAuth tokens are saved properly.
  - `test_get_valid_credentials_generate_new_token`: Checks token generation if no credentials exist.
  - `test_get_valid_credentials`: Confirms retrieval of valid credentials.

### `email_fetcher.py`

- **Tests Provided**:
  - `test_init`: Verifies that OAuth credentials are properly initialized.
  - `test_fetch_emails`: Tests fetching and saving emails.
  - `test_create_table`: Ensures the table is created if it does not exist.
  - `test_save_to_database`: Checks that email data is saved to the database.

### `email_filter.py`

- **Tests Provided**:
  - `test_init_success`: Validates successful initialization and rule loading.
  - `test_validate_rules_success`: Ensures rules validation passes with correct rules.
  - `test_validate_rules_invalid_value`: Checks for errors with invalid rule values.
  - `test_search_emails`: Verifies email search functionality.
  - `test_apply_filters`: Ensures the filter application process works as expected.

## Notes

- Ensure that `client.json` and other required files are in the correct directory before running the scripts.
- Modify paths and configuration settings as needed based on your environment.
