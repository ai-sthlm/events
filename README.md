# AI events in Stockholm

A small, public calendar for AI-related events in Stockholm: meetups, talks, workshops, hack nights, courses, and conferences. The repository is the source of truth. Every event is proposed in a pull request, reviewed in plain text, and published as static HTML through GitHub Pages.

## Scope

The calendar covers public AI events held in the Stockholm area, plus online events that are explicitly intended for the Stockholm AI community. It is a continuously maintained best-effort calendar, not an authoritative listing. Organizers remain responsible for the details, registration, and any changes or cancellations.

## What we record

Each listing has a title, local start time, venue, canonical event URL, and—when supplied—an end time, street address, organizer, tags, and a Markdown description. Time is recorded with an ISO 8601 UTC offset so an event remains unambiguous across daylight saving time.

## Directory structure

```
events/YYYY/MM/DD/   # one submitted event per .md file
  README.md           # data format and example
build.py              # standard-library validator and static-site generator
templates/index.html  # trusted page shell; uses the $EVENTS placeholder
templates/style.css   # stylesheet copied unchanged to dist/style.css
dist/                 # generated site, not committed
```

## Contributing

Add one Markdown file per event under [`events/`](events/). It has a constrained metadata header and a Markdown body; see the [event-data guide](events/README.md) for the exact format. The validation step runs on every pull request. A merge to the default branch (`main` or `master`) generates `dist/index.html` and deploys it to GitHub Pages.

Run the same checks locally with only a standard Python installation:

```sh
python3 build.py --check
python3 build.py
```

The second command writes the disposable preview to `dist/index.html`.

## Telegram announcements

After a new event record is merged into `main`, the GitHub Actions workflow posts
one announcement to Telegram. Configure this repository Actions secret before
enabling it:

- `TELEGRAM_BOT_TOKEN`: the token issued by BotFather.

The channel is configured as `@ai_sthlm` in the workflow. The bot must be an
administrator there with permission to post messages. Edits to existing records
do not produce an announcement.

To test an announcement end-to-end, run:

```sh
python3 scripts/create_telegram_test_pr.py
```

It creates a uniquely named branch and disposable test event, validates and
pushes it, then opens GitHub's pre-filled pull-request form in your browser.
Review the form and submit the pull request. Merge it to send the test
announcement; remove the generated test event afterward.

Shared images are maintained and published in [ai-sthlm/assets](https://github.com/ai-sthlm/assets). The stylesheet loads the skyline from its GitHub Pages URL; images are not bundled into this site's build.

For a local preview, run `make serve` and open <http://localhost:8000>. This uses Python’s built-in HTTP server.

## Constraints

- The generator uses Python 3.12 and the standard library only: no packages, JavaScript build step, database, or hosted CMS.
- `templates/index.html` is a trusted site template. The builder replaces its sole `$EVENTS` placeholder with escaped event cards; do not add other `$` placeholders.
- Event files are deliberately a **small flat YAML subset**, not general YAML. This makes dependency-free validation possible. Keep every value on one line and follow the format in `events/README.md`.
- Submit events with a public HTTPS registration/details link and a start time that includes a UTC offset. Use the local Stockholm offset applicable on the event date (`+01:00` or `+02:00`).
- One event per file. Use `events/YYYY/MM/DD/short-event-name.md`, with directories matching the local `start` date, and do not edit unrelated event records.
- Event descriptions are Markdown bodies rendered in the browser with `marked`. Raw HTML is not rendered.
- GitHub Pages must be enabled in repository settings with **GitHub Actions** as its source before deployment can publish.

## Inclusion and verification

1. Add events only after confirming them on the organizer’s official site or registration page.
2. Prefer the organizer’s own URL for details, registration, location, and schedule.
3. Use the announced local time and confirm the relevant Stockholm offset (`+01:00` or `+02:00`).
4. Update or remove an event when the organizer changes its details or cancels it.
5. If a lead cannot yet be verified, do not add it to the published calendar.

The automated check validates format and safety constraints; maintainers verify real-world details and relevance during review.
