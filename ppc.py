import os
import csv
import time
import json
import logging
import sys
from requests import Session
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import urllib3
from urllib.parse import quote

########################################
# Load environment variables
########################################
load_dotenv(override=True)

CUC_HOSTNAME = os.getenv('CUC_HOSTNAME')
APP_USER = os.getenv('APP_USER')
APP_PASSWORD = os.getenv('APP_PASSWORD')
CUC_CERT = os.getenv('CUC_CERT', '')  # Path to cert or empty
DEBUG = os.getenv('DEBUG', 'False') == 'True'

if not CUC_HOSTNAME or not APP_USER or not APP_PASSWORD:
    print("CUC_HOSTNAME, APP_USER, and APP_PASSWORD must be set in the .env file.")
    sys.exit(1)

########################################
# Configure Logging
########################################
# We'll log INFO and DEBUG level messages to a file, and INFO messages to stdout.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Console Handler (info level)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

# File Handler (debug level)
fh = logging.FileHandler('pin_change.log')
fh.setLevel(logging.DEBUG)
fh_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s')
fh.setFormatter(fh_formatter)
logger.addHandler(fh)

logger.debug("Logger initialized. DEBUG mode is: {}".format(DEBUG))

########################################
# Requests Session Setup
########################################
if CUC_CERT:
    certVerify = CUC_CERT
else:
    certVerify = False

admin_session = Session()
admin_session.verify = certVerify
admin_session.auth = HTTPBasicAuth(APP_USER, APP_PASSWORD)

# Disable SubjectAltNameWarning if present
#urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings()

########################################
# Helper Functions
########################################

def log_http_response(response):
    """If DEBUG enabled, log raw request/response."""
    if DEBUG:
        logger.debug("----- HTTP Request/Response -----")
        logger.debug("Request URL: {}".format(response.request.url))
        logger.debug("Request Headers:\n{}".format(response.request.headers))
        if response.request.body:
            logger.debug("Request Body:\n{}".format(response.request.body))
        logger.debug("Response Status: {}".format(response.status_code))
        logger.debug("Response Headers:\n{}".format(response.headers))
        logger.debug("Response Body:\n{}".format(response.text))
        logger.debug("---------------------------------")

def get_user_objectid(alias):
    raw_query = '(alias is {})'.format(alias)
    encoded_query = quote(raw_query, safe='()')

    url = "https://{}/vmrest/users".format(CUC_HOSTNAME)
    full_url = url + '?query=' + encoded_query

    try:
        resp = admin_session.get(full_url, headers={'Accept': 'application/json'})
        log_http_response(resp)
        resp.raise_for_status()
    except HTTPError as err:
        logger.error("Error retrieving user {}: HTTP {} - {}".format(alias, err.response.status_code, err.response.text))
        return None

    data = resp.json()

    # Now, look directly for 'User' in data
    if 'User' not in data:
        logger.info("No user found for alias {}".format(alias))
        return None

    user = data['User']

    # If there's a chance that multiple users are returned (in a list), handle that:
    if isinstance(user, list):
        user = user[0]

    # 'ObjectId' should be present in the user dictionary
    return user.get('ObjectId')

def update_user_pin(user_objectid, new_pin):
    url = "https://{}/vmrest/users/{}/credential/pin".format(CUC_HOSTNAME, user_objectid)

    payload = {
        "Credentials": new_pin,
    }

    headers = {'Content-Type': 'application/json'}

    try:
        resp = admin_session.put(url, headers=headers, json=payload)
        log_http_response(resp)
        resp.raise_for_status()
        # Expecting 204 on success
        if resp.status_code == 204:
            return True
        else:
            logger.error("Unexpected status code {} returned.".format(resp.status_code))
            return False
    except HTTPError as err:
        logger.error("Failed to update PIN for user {}: HTTP {} - {}".format(
            user_objectid, err.response.status_code, err.response.text))
        return False

########################################
# Main Execution Flow
########################################

def main():
    # Input CSV file
    input_file = 'users.csv'  # Adjust as needed
    processed_file = 'processed_users.csv'  # We'll store processed results

    # Check if processed_users.csv exists; if not, create it with headers
    if not os.path.exists(processed_file):
        with open(processed_file, 'w', newline='') as pf:
            writer = csv.writer(pf)
            writer.writerow(['alias', 'new_pin', 'status', 'message'])

    logger.info("Starting PIN update process...")
    logger.info("Reading from: {}".format(input_file))

    with open(input_file, 'r') as f, open(processed_file, 'a', newline='') as pf:
        reader = csv.DictReader(f)
        p_writer = csv.writer(pf)

        for row in reader:
            alias = row.get('alias')
            new_pin = row.get('new_pin')

            if not alias or not new_pin:
                logger.warning("Skipping row due to missing alias or new_pin: {}".format(row))
                p_writer.writerow([alias, new_pin, 'skipped', 'Missing data'])
                continue

            logger.info("Processing user alias: {}".format(alias))

            # 1. Find user's objectId
            objectid = get_user_objectid(alias)
            if not objectid:
                logger.error("User not found for alias {}. Skipping.".format(alias))
                p_writer.writerow([alias, new_pin, 'failed', 'User not found'])
                continue

            # 2. Update PIN
            success = update_user_pin(objectid, new_pin)
            if success:
                logger.info("Successfully updated PIN for user alias: {}".format(alias))
                p_writer.writerow([alias, new_pin, 'success', 'PIN updated'])
            else:
                logger.error("Failed to update PIN for user alias: {}".format(alias))
                p_writer.writerow([alias, new_pin, 'failed', 'Failed to update PIN'])

            # Niceness mechanism: sleep or handle rate limiting if needed.
            # For example, sleep 1 second between requests:
            time.sleep(1)

    logger.info("PIN update process completed.")


if __name__ == '__main__':
    main()
