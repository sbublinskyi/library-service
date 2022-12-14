import os

import requests

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
API_URL = "https://api.telegram.org/"


def send_message(message: str) -> None:
    requests.post(
        f"{API_URL}{BOT_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": message},
    )
