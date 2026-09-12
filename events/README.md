# Event data

Each file here is one event. Put it at `events/YYYY/MM/DD/slug.md`; the directory date is the event date. Event files use a small metadata header followed by a Markdown body.

Required fields: `title`, `time`, `venue`, and public `https://` `url`. `time` uses Stockholm local time and is either `HH:MM` or a same-day interval such as `18:00–20:30`.

Optional header fields: `end`, `address`, `organizer`, and `tags` (an inline list such as `[meetup, llms]`). `venue` is the physical place name; use `address` for its street address and `organizer` for the hosting organization.

Put metadata between opening and closing `---` lines. The text after the closing line is the event description and supports standard Markdown, including paragraphs, lists, emphasis, links, and inline code. Raw HTML is displayed as text.

```md
---
title: Practical RAG evening
time: 18:00–20:30
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
