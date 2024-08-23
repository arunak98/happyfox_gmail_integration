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
    - Fetch emails from the Gmail inbox using the authenticated OAuth credentials.
    - Stores the fetched emails in an SQLite database (`email_db`).

3. **`email_filter.py`**:
    - Applies user-defined rules to the fetched emails.
    - Process emails by parsing data from the database and applying actions like marking emails as read/unread or moving them to different labels using the Gmail REST API.

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
    pip install -r requirements.txt
    ```

2. **Run Unit Tests**:
    ```bash
    python -m unittest discover
    ```
    - This will run all unit tests in the project to validate the functionality of the `OAuthTokenManager`, `EmailFetcher`, and `EmailFilter` classes.

## Notes

- Ensure that `client.json` and other required files are in the correct directory before running the scripts.
- Modify paths and configuration settings as needed based on your environment.
