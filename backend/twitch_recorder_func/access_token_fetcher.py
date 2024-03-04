# access_token_fetcher.py

import requests
import logging


def fetch_access_token(token_url):
    try:
        token_response = requests.post(token_url, timeout=15)
        token_response.raise_for_status()
        token = token_response.json()
        return token["access_token"]
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch access_token: {str(e)}")
