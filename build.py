#!/usr/bin/env python3
"""Validate event records and render the dependency-free Stockholm AI events site."""
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

ROOT = Path(__file__).resolve().parent
EVENTS, OUTPUT, TEMPLATE, STYLESHEET = ROOT / "events", ROOT / "dist", ROOT / "templates" / "index.html", ROOT / "templates" / "style.css"
REQUIRED = ("title", "start", "venue", "url")
ALLOWED = set(REQUIRED) | {"end", "address", "tags", "description"}
KEY = re.compile(r"^([a-z]+):[ ]*(.*)$")


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
        if "description" in fields:
            raise ValueError("use Markdown body or description, not both")
        fields["description"] = body
    return fields


def event_from(path: Path) -> dict[str, object]:
    fields = parse_fields(path.read_text(encoding="utf-8"), path)
    missing = set(REQUIRED) - fields.keys()
    if missing:
        raise ValueError("missing " + ", ".join(sorted(missing)))
    try:
        start = dt.datetime.fromisoformat(fields["start"])
        end = dt.datetime.fromisoformat(fields["end"]) if "end" in fields else None
    except ValueError as exc:
        raise ValueError("start/end must be ISO 8601 date-times") from exc
    if start.tzinfo is None or (end and end.tzinfo is None):
        raise ValueError("start/end must include a UTC offset")
    if end and end <= start:
        raise ValueError("end must be after start")
    expected_path = (f"{start.year:04d}", f"{start.month:02d}", f"{start.day:02d}")
    actual_path = path.relative_to(EVENTS).parts[:3]
    if actual_path != expected_path:
        raise ValueError("path must begin with the start date: " + "/".join(expected_path))
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
    tags = "".join(f"<li>{esc(tag)}</li>" for tag in event["tags_list"])
    description = f"<p>{esc(event['description'])}</p>" if event.get("description") else ""
    return f'''<article><h2><a href="{esc(event['url'])}">{esc(event['title'])}</a></h2>
<p class="when">{when}</p><p>{location}</p>{description}<ul class="tags">{tags}</ul></article>'''


def build(check_only: bool = False) -> None:
    paths = sorted(path for path in [*EVENTS.rglob("*.yaml"), *EVENTS.rglob("*.md")]
                   if path.name.lower() != "readme.md")
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
        raise ValueError(f"could not copy {STYLESHEET.relative_to(ROOT)}: {exc}") from exc
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
