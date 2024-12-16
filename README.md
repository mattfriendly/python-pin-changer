# Cisco Unity Connection PIN Changer

A Python-based utility script for bulk updating voicemail PINs in Cisco Unity Connection (CUC). This tool reads a CSV file of user aliases and new PINs, and then updates each user's PIN using the Cisco Unity Connection Provisioning Interface (CUPI) REST API.

**Key Features:**

- **Bulk PIN Updates:** Easily change PINs for multiple users in one run.
- **CSV Input:** Uses a simple CSV file (`users.csv`) containing `alias` and `new_pin` columns.
- **Transaction Logging:** Outputs a `processed_users.csv` file logging success/failure status for each user, enabling you to resume or audit changes.
- **Debug Logging:** Detailed logs (`pin_change.log`) are generated with adjustable verbosity (DEBUG/INFO).
- **Niceness Mechanism:** Inserts a short pause between API calls to avoid rate-limiting or performance issues on the CUC server.
- **Error Handling:** Gracefully handles HTTP errors and logs them, continuing to process remaining users.

## Prerequisites

- Python 3.5+ (Tested on Python 3.5 and newer)
- Access to Cisco Unity Connection environment with API credentials
- `requests` and `python-dotenv` libraries
- Valid `.env` file configured with:
  - `CUC_HOSTNAME`: IP/Hostname of the Cisco Unity Connection server
  - `APP_USER`: Administrator username for CUC
  - `APP_PASSWORD`: Administrator password for CUC
  - `DEBUG`: `True` or `False` for detailed logging
  - Optionally: `CUC_CERT` path if using a custom SSL certificate

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/cuc-pin-changer.git
    cd cuc-pin-changer
    ```

2. Set up a virtual environment (recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Create and configure your `.env` file:
    ```bash
    cp .env.example .env
    # Edit .env to set CUC_HOSTNAME, APP_USER, APP_PASSWORD, DEBUG, and optionally CUC_CERT.
    ```

## CSV File Format

The script reads `users.csv` in the following format:

```csv
alias,new_pin
user01,123456
user02,654321
user1,999999
```

- **alias:** The user's alias in CUC (as confirmed in the CUC admin GUI)
- **new_pin:** The new PIN to be set for that user

## Usage

1. Ensure your `.env` file is properly configured and `users.csv` is in the project directory.
2. Run the script:
    ```bash
    python3 ppc.py
    ```
3. The script will:
   - Load environment variables.
   - Read `users.csv` and attempt to update each user's PIN via the CUC API.
   - Write results to `processed_users.csv`, logging success or failure.
   - Generate `pin_change.log` for debugging and audit purposes.

## Logging & Debugging

- The console will show INFO-level logs.
- `pin_change.log` will contain DEBUG-level logs, including request/response details if `DEBUG=True` in `.env`.
- If a user is not found or the PIN update fails, the error is logged, and processing continues for the remaining users.

## Resuming & Auditing

- After the script finishes, check `processed_users.csv` to see which users succeeded or failed.
- To retry failures:
  - Adjust the input CSV or correct environment issues.
  - Rerun the script. You can remove processed (successful) users from the `users.csv` file if desired, or leave them in and they will simply be updated again.

## Security Considerations

- The script uses Basic Auth over HTTPS. Ensure you have a secure connection to the CUC server.
- If using a self-signed certificate, you can disable SSL verification or provide a trusted `.pem` via `CUC_CERT`.
- Handle `.env` and log files carefully, as they may contain sensitive information.

## Contributing

Contributions are welcome. Please open issues or submit pull requests to suggest improvements, fix bugs, or add new features.

