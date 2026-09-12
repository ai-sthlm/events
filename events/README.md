# Event data

Each file here is one event. Put it at `events/YYYY/MM/DD/slug.yaml` (or `.md`), using the local date of its `start` time. The builder accepts only a small, documented YAML subset so it can use Python's standard library.

Required fields: `title`, `start` (an ISO 8601 date/time with offset, e.g. `2026-10-15T18:00:00+02:00`), `venue`, and public `https://` `url`.

Optional fields: `end`, `address`, `tags` (an inline list such as `[meetup, llms]`), and `description`.

For Markdown, put fields between opening and closing `---` lines. Text after the closing line is the description; do not also set `description`.

```md
---
title: Practical RAG evening
start: 2026-11-04T18:00:00+01:00
venue: Tekniska museet
url: https://events.example.org/rag
tags: [rag, community]
---

Talks, food, and networking.
```

Values must occupy one line. Quotes, nested mappings, block scalars, comments, and arbitrary YAML features are intentionally unsupported.
