---
name: open-memory-boost
description: "Local persistent memory workflow for Codex. Use when the user asks to remember facts, preferences, decisions, projects, or task state; to summarize prior context; to retrieve relevant long-term memory before answering; or to maintain a lightweight memory store without external services."
---

# Open Memory Boost

Use this skill to maintain a durable local memory that helps Codex stay consistent across sessions.

## When to use

- A user asks to remember, forget, or update a stable fact.
- A user preference, decision, or project constraint should persist.
- You need to retrieve prior context before answering.
- You are building or maintaining a memory layer for another agent.

## Core rules

- Store only stable, reusable information.
- Separate facts, preferences, decisions, open questions, and session summaries.
- Prefer short, structured entries over raw chat logs.
- Record provenance for anything important: who said it, when, and why it matters.
- Treat transient, emotional, or one-off details as non-memory unless the user explicitly wants them saved.
- Do not store secrets, credentials, or sensitive personal data unless the user explicitly asks and the surrounding system allows it.

## Workflow

1. Capture
   - Extract candidate memory items from the current request and conversation.
   - Normalize names, dates, product names, and project identifiers.
   - Split multiple ideas into separate entries.

2. Classify
   - `fact`: stable user or project fact.
   - `preference`: style, format, or choice preference.
   - `decision`: an agreed project choice.
   - `open_question`: unresolved item that should be revisited.
   - `summary`: compact session recap.

3. Compress
   - Merge duplicates.
   - Keep the newest confirmed version.
   - Drop low-signal details.
   - Preserve source timestamps when they help disambiguate.

4. Recall
   - Search by entity, topic, time, and task relevance.
   - Prefer direct user statements over inferred memory.
   - Use only memory that is still relevant to the current request.

5. Update
   - Write back changed memory items immediately after a confirmed user correction or decision.
   - Mark outdated items as superseded instead of silently deleting them when history matters.

## Output discipline

- When answering a user, surface only the memory that materially changes the answer.
- Do not expose internal memory files or storage mechanics unless the user asks.
- If memory is uncertain, say so and ask a targeted question.

## References

- See [references/memory-format.md](references/memory-format.md) for the recommended local memory schema.
- See [references/memory-workflow.md](references/memory-workflow.md) for capture, recall, and update rules.
