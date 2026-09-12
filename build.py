#!/usr/bin/env python3
"""Validate Markdown event records and render the Stockholm AI events site."""
from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import shutil
import sys
from pathlib import Path
from string import Template
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
EVENTS, OUTPUT, TEMPLATE, STYLESHEET = ROOT / "events", ROOT / "dist", ROOT / "templates" / "index.html", ROOT / "templates" / "style.css"
REQUIRED = ("title", "time", "venue", "url")
ALLOWED = set(REQUIRED) | {"address", "organizer", "tags"}
KEY = re.compile(r"^([a-z]+):[ ]*(.*)$")
TIME_INTERVAL = re.compile(r"^(\d{2}:\d{2})(?:\s*[–-]\s*(\d{2}:\d{2}))?$")
STOCKHOLM = ZoneInfo("Europe/Stockholm")


def parse_fields(text: str, path: Path) -> dict[str, str]:
    """Parse the intentionally small, flat YAML subset used by event records."""
    lines, body = text.splitlines(), ""
    if path.suffix == ".md":
        if not lines or lines[0] != "---":
            raise ValueError("Markdown records must start with ---")
        try:
            close = lines.index("---", 1)
        except ValueError as exc:
            raise ValueError("Markdown front matter needs a closing ---") from exc
        lines, body = lines[1:close], "\n".join(lines[close + 1:]).strip()
    fields: dict[str, str] = {}
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        match = KEY.fullmatch(line)
        if not match:
            raise ValueError(f"line {number}: expected `key: value`")
        key, value = match.groups()
        if key not in ALLOWED:
            raise ValueError(f"line {number}: unsupported field `{key}`")
        if key in fields or not value:
            raise ValueError(f"line {number}: duplicate or empty `{key}`")
        fields[key] = value
    if body:
        fields["description"] = body
    return fields


def event_from(path: Path) -> dict[str, object]:
    fields = parse_fields(path.read_text(encoding="utf-8"), path)
    missing = set(REQUIRED) - fields.keys()
    if missing:
        raise ValueError("missing " + ", ".join(sorted(missing)))
    actual_path = path.relative_to(EVENTS).parts[:3]
    if len(actual_path) != 3:
        raise ValueError("path must begin with a date: YYYY/MM/DD")
    try:
        date = dt.date.fromisoformat("-".join(actual_path))
    except ValueError as exc:
        raise ValueError("path must begin with a valid date: YYYY/MM/DD") from exc
    match = TIME_INTERVAL.fullmatch(fields["time"])
    if not match:
        raise ValueError("time must be HH:MM or HH:MM–HH:MM")
    try:
        start = dt.datetime.combine(date, dt.time.fromisoformat(match.group(1)), tzinfo=STOCKHOLM)
        end = (dt.datetime.combine(date, dt.time.fromisoformat(match.group(2)), tzinfo=STOCKHOLM)
               if match.group(2) else None)
    except ValueError as exc:
        raise ValueError("time must use valid 24-hour values") from exc
    if end and end <= start:
        raise ValueError("the end time must be after the start time")
    parsed = urlparse(fields["url"])
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("url must be an absolute https URL")
    tags = fields.get("tags", "[]")
    if not (tags.startswith("[") and tags.endswith("]")):
        raise ValueError("tags must be an inline list, e.g. [meetup, llms]")
    return {**fields, "start_dt": start, "end_dt": end,
            "tags_list": [tag.strip() for tag in tags[1:-1].split(",") if tag.strip()]}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_event(event: dict[str, object]) -> str:
    start = event["start_dt"]
    assert isinstance(start, dt.datetime)
    when = start.strftime("%A %-d %B %Y, %H:%M")
    end = event["end_dt"]
    if isinstance(end, dt.datetime):
        when += "–" + end.strftime("%H:%M")
    location = esc(event["venue"])
    if event.get("address"):
        location += ", " + esc(event["address"])
    organizer = f'<p class="organizer">Organized by {esc(event["organizer"])}</p>' if event.get("organizer") else ""
    tags = "".join(f"<li>{esc(tag)}</li>" for tag in event["tags_list"])
    # Markdown remains escaped text in the generated HTML. marked renders it
    # in the browser after page load, so event content cannot alter the shell.
    description = (f'<div class="event-description markdown-source">{esc(event["description"])}</div>'
                   if event.get("description") else "")
    return f'''<article class="event"><div class="date-tile" aria-hidden="true"><span>{start.strftime('%b')}</span><strong>{start.day:02d}</strong><span>{start.year}</span></div>
<div class="event-details"><p class="when">{when}</p><h3><a href="{esc(event['url'])}">{esc(event['title'])} <span aria-hidden="true">↗</span></a></h3>
<p>{location}</p>{organizer}{description}<ul class="tags">{tags}</ul></div></article>'''


def build(check_only: bool = False) -> None:
    paths = sorted(path for path in EVENTS.rglob("*.md") if path.name.lower() != "readme.md")
    events, errors = [], []
    for path in paths:
        try:
            events.append(event_from(path))
        except ValueError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
    if errors:
        raise ValueError("\n".join(errors))
    if check_only:
        print(f"Validated {len(events)} event(s).")
        return
    events.sort(key=lambda event: event["start_dt"])
    cards = "\n".join(render_event(event) for event in events) or "<p>No events announced yet.</p>"
    try:
        page = Template(TEMPLATE.read_text(encoding="utf-8")).substitute(EVENTS=cards)
    except (OSError, ValueError) as exc:
        raise ValueError(f"could not render {TEMPLATE.relative_to(ROOT)}: {exc}") from exc
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "index.html").write_text(page, encoding="utf-8")
    try:
        shutil.copyfile(STYLESHEET, OUTPUT / "style.css")
    except OSError as exc:
        raise ValueError(f"could not copy a site asset: {exc}") from exc
    print(f"Built {OUTPUT / 'index.html'} from {len(events)} event(s).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate records without writing output")
    args = parser.parse_args()
    try:
        build(args.check)
    except ValueError as error:
        print(f"Validation failed:\n{error}", file=sys.stderr)
        sys.exit(1)
