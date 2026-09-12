# Event data

Each file here is one event. Put it at `events/YYYY/MM/DD/slug.md`, using the local date of its `start` time. Event files use a small metadata header followed by a Markdown body.

Required fields: `title`, `start` (an ISO 8601 date/time with offset, e.g. `2026-10-15T18:00:00+02:00`), `venue`, and public `https://` `url`.

Optional header fields: `end`, `address`, `organizer`, and `tags` (an inline list such as `[meetup, llms]`). `venue` is the physical place name; use `address` for its street address and `organizer` for the hosting organization.

Put metadata between opening and closing `---` lines. The text after the closing line is the event description and supports standard Markdown, including paragraphs, lists, emphasis, links, and inline code. Raw HTML is displayed as text.

```md
---
title: Practical RAG evening
start: 2026-11-04T18:00:00+01:00
venue: Tekniska museet
address: Museivägen 7, Stockholm
organizer: Stockholm AI community
url: https://events.example.org/rag
tags: [rag, community]
---

Talks, food, and networking.

- Bring your questions.
- [Register now](https://events.example.org/rag).
```

Header values must occupy one line. Quotes, nested mappings, block scalars, comments, and arbitrary YAML features are intentionally unsupported.
