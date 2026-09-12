#!/usr/bin/env python3
"""Send a test message to a Telegram channel using only the standard library."""

from __future__ import annotations

import json
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_ROOT = "https://api.telegram.org"

# Fill these in before running the script. Keep this file uncommitted if it
# contains a real bot token.
BOT_TOKEN = "PASTE_BOT_TOKEN_HERE"
CHAT_ID = "@ai_sthlm"
MESSAGE = "Telegram credentials verified. ✅"


def telegram_request(token: str, method: str, data: dict[str, str] | None = None) -> dict[str, Any]:
    """Call a Telegram Bot API endpoint and return its decoded response."""
    body = urlencode(data).encode() if data else None
    request = Request(f"{API_ROOT}/bot{token}/{method}", data=body, method="POST" if body else "GET")
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.load(response)
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram returned HTTP {error.code}: {detail}") from error
    except URLError as error:
        raise RuntimeError(f"Could not reach Telegram: {error.reason}") from error

    if not payload.get("ok"):
        raise RuntimeError(f"Telegram rejected the request: {payload.get('description', payload)}")
    return payload


def main() -> int:
    if BOT_TOKEN == "PASTE_BOT_TOKEN_HERE":
        print("Set BOT_TOKEN at the top of this script before running it.", file=sys.stderr)
        return 2

    try:
        bot = telegram_request(BOT_TOKEN, "getMe")["result"]
        print(f"Bot token is valid: @{bot.get('username', '<no username>')} (ID {bot['id']})")
        response = telegram_request(BOT_TOKEN, "sendMessage", {"chat_id": CHAT_ID, "text": MESSAGE})
        print(f"Test message sent to {CHAT_ID} (message ID {response['result']['message_id']}).")
    except RuntimeError as error:
        print(f"Telegram credential test failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
