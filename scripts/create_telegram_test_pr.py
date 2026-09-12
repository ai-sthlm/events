#!/usr/bin/env python3
"""Create and open a PR for a disposable Telegram-announcement test event.

Requires an authenticated GitHub CLI (``gh auth login``), a clean working tree,
and permission to push branches to the ``origin`` repository.
"""

from __future__ import annotations

import datetime as dt
import subprocess
import sys
import webbrowser
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent.parent
STOCKHOLM = ZoneInfo("Europe/Stockholm")


def run(*args: str, capture_output: bool = False) -> str:
    """Run a required command from the repository root."""
    result = subprocess.run(
        args,
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=capture_output,
    )
    if result.returncode:
        if capture_output and result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        raise RuntimeError(f"Command failed: {' '.join(args)}")
    return result.stdout.strip() if capture_output else ""


def ensure_clean_worktree() -> None:
    """Avoid mixing a generated event with unrelated local work."""
    status = run("git", "status", "--porcelain", capture_output=True)
    if status:
        raise RuntimeError("Working tree is not clean; commit or stash changes before running this script.")


def main() -> int:
    try:
        ensure_clean_worktree()
        run("gh", "auth", "status")
        run("git", "switch", "main")
        run("git", "pull", "--ff-only", "origin", "main")

        now = dt.datetime.now(STOCKHOLM)
        start = (now + dt.timedelta(days=21)).replace(hour=18, minute=0, second=0, microsecond=0)
        slug = f"telegram-announcement-test-{now:%Y%m%d-%H%M%S}"
        branch = f"codex/{slug}"
        event_path = ROOT / "events" / f"{start:%Y}" / f"{start:%m}" / f"{start:%d}" / f"{slug}.yaml"
        title = f"Telegram announcement test event ({now:%Y-%m-%d})"

        run("git", "switch", "-c", branch)
        event_path.parent.mkdir(parents=True, exist_ok=True)
        event_path.write_text(
            "\n".join(
                (
                    f"title: {title}",
                    f"start: {start.isoformat()}",
                    "venue: Stockholm (test listing)",
                    f"url: https://example.com/{slug}",
                    "tags: [test]",
                    "description: Disposable test event for the Telegram announcement workflow.",
                    "",
                )
            ),
            encoding="utf-8",
        )

        run("python3", "build.py", "--check")
        run("git", "add", str(event_path.relative_to(ROOT)))
        run("git", "commit", "-m", "Add Telegram announcement test event")
        run("git", "push", "--set-upstream", "origin", branch)
        pr_url = run(
            "gh",
            "pr",
            "create",
            "--base",
            "main",
            "--head",
            branch,
            "--title",
            "Test Telegram event announcement",
            "--body",
            "Merge this disposable event to verify the Telegram announcement workflow. Remove the event afterward.",
            capture_output=True,
        )
    except (OSError, RuntimeError) as error:
        print(f"Could not create test PR: {error}", file=sys.stderr)
        return 1

    print(f"Created pull request: {pr_url}")
    if not webbrowser.open(pr_url):
        print("Could not open a browser automatically; open the URL above.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
