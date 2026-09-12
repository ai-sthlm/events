#!/usr/bin/env python3
"""Announce event records added between two Git revisions on Telegram."""

from __future__ import annotations

import html
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from build import event_from


CHAT_ID = "@ai_sthlm"


def added_event_paths(before: str, after: str) -> list[Path]:
    """Return event records newly added between the two revisions."""
    files = subprocess.check_output(
        ["git", "diff", "--name-only", "--diff-filter=A", before, after, "--", "events"],
        text=True,
    ).splitlines()
    return [
        Path(filename).resolve()
        for filename in files
        if Path(filename).suffix == ".md"
        and len(Path(filename).relative_to("events").parent.parts) == 3
    ]


def event_message(event: dict[str, object]) -> str:
    """Format a concise Telegram announcement from a validated event record."""
    start = event["start_dt"]
    when = start.strftime("%A %-d %B %Y, %H:%M")
    end = event["end_dt"]
    if end is not None:
        when += "–" + end.strftime("%H:%M")
    return "<b>" + html.escape(str(event["title"])) + "</b>\n\n" + "\n".join(
        html.escape(value) for value in (when, str(event["venue"]), str(event["url"]))
    )


def send_message(token: str, message: str) -> None:
    """Post one plain-text message to the configured Telegram channel."""
    request = Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps({"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=15) as response:
            result = json.load(response)
    except (HTTPError, URLError) as error:
        raise RuntimeError(f"Telegram request failed: {error}") from error
    if not result.get("ok"):
        raise RuntimeError(f"Telegram rejected the request: {result}")


def main() -> int:
    if len(sys.argv) != 3:
        print(f"Usage: {Path(sys.argv[0]).name} BEFORE_SHA AFTER_SHA", file=sys.stderr)
        return 2
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Set TELEGRAM_BOT_TOKEN before running this script.", file=sys.stderr)
        return 2

    for path in added_event_paths(sys.argv[1], sys.argv[2]):
        event = event_from(path)
        send_message(token, event_message(event))
        print(f"Announced {path.relative_to(Path.cwd())}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
