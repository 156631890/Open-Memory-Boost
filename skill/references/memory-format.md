# Memory Format

Use a small set of Markdown files or sections with stable headings.

## Recommended sections

```md
# Facts
- [2026-04-01] user prefers concise answers

# Preferences
- [2026-04-01] user prefers Chinese responses for local work

# Decisions
- [2026-04-01] use local Markdown memory instead of external services

# Open Questions
- [2026-04-01] should memory be project-local or global?

# Session Summaries
- [2026-04-01] created open-memory-boost skill for durable local memory
```

## Entry fields

- `date`: when the item was confirmed.
- `source`: user, system, or inferred.
- `confidence`: high, medium, or low.
- `status`: active, superseded, or resolved.

## Good entry shape

- One idea per line.
- Short, factual phrasing.
- Include enough context to make the entry useful later.
- Keep older conflicting entries, but mark them superseded.
