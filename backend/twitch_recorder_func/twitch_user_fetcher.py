# twitch_user_fetcher.py

import requests
import logging


def get_users_by_category(headers, CATEGORY_ID, url):
    response = requests.get(
        url,
        headers=headers,
        params={"game_id": CATEGORY_ID, "first": 100},
    )
    data = response.json()
    english_streams = [stream for stream in data["data"] if stream["language"] == "en"]
    usernames = [stream["user_name"] for stream in english_streams]
    logging.info(
        f"First ten currently online users in teamfight tactics category: {usernames[:10]}"
    )
    return usernames[1]
