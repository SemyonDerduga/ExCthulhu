import os
import sys
import json
import urllib.request
import urllib.parse

BOT_TOKEN = os.environ["BOT_TOKEN"]
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


def api_call(method: str, params: dict | None = None) -> dict:
    url = f"{API_BASE}/{method}"
    data = None
    if params:
        data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(url, data=data) as resp:
        return json.load(resp)


def get_chat_ids() -> set[str]:
    result = api_call("getUpdates").get("result", [])
    chat_ids = set()
    for update in result:
        message = update.get("message") or update.get("edited_message")
        if message:
            chat_ids.add(str(message["chat"]["id"]))
    return chat_ids


MAX_MESSAGE_LEN = 4096


def send_message(chat_id: str, text: str) -> None:
    """Send message to Telegram splitting it into chunks if needed."""
    for i in range(0, len(text), MAX_MESSAGE_LEN):
        api_call("sendMessage", {"chat_id": chat_id, "text": text[i : i + MAX_MESSAGE_LEN]})


def main():
    message = sys.stdin.read().strip()
    for chat_id in get_chat_ids():
        send_message(chat_id, message)


if __name__ == "__main__":
    main()
