# Open Memory Boost

Open Memory Boost is a local-first memory layer for Codex.

It helps an AI assistant remember stable facts, user preferences, project decisions, and session summaries across conversations, without depending on external memory services.

## Why this exists

LLMs are strong at reasoning, but weak at durable continuity.

Open Memory Boost solves that by giving Codex a lightweight, auditable memory workflow:

- remember what matters
- ignore one-off noise
- compress long conversations into reusable context
- retrieve only the memory relevant to the current task

## What it does

Open Memory Boost provides two pieces:

### 1. A Codex Skill

Defines the workflow for:

- capturing stable information
- classifying memory into categories
- compressing duplicate or low-signal entries
- recalling relevant memory before answering
- updating memory when the user corrects or changes something

### 2. A Local Markdown Memory Runtime

A small command-line tool that stores memory in plain Markdown files.

It supports:

- `init` - create a new memory store
- `add` - add a memory entry
- `search` - search existing memory
- `list` - list all stored memory

## Memory types

Open Memory Boost organizes information into a few simple buckets:

- `Facts`
- `Preferences`
- `Decisions`
- `Open Questions`
- `Session Summaries`

This keeps memory structured, readable, and easy to review by both humans and agents.

## Key features

- Local-first and offline-friendly
- No external API required
- Human-readable Markdown storage
- Simple CLI for adding and searching memory
- Designed for stable, reusable context rather than raw chat logs
- Easy to audit, backup, and version with Git

## How it works

1. The assistant detects stable information in the conversation.
2. It converts that information into a compact memory entry.
3. The entry is stored in a local Markdown file.
4. On later requests, the assistant searches for relevant memory.
5. The retrieved context is used to improve continuity and consistency.

## Example

```powershell
open-memory-boost init
open-memory-boost add facts "User prefers concise answers"
open-memory-boost add preferences "User prefers Chinese responses for local work"
open-memory-boost search concise
open-memory-boost list
```

## Project structure

```text
open-memory-boost/
?? skill/
?  ?? SKILL.md
?  ?? agents/openai.yaml
?  ?? references/
?? memory_boost/
?  ?? cli.py
?  ?? store.py
?  ?? __main__.py
?? examples/
?? README.md
?? README.zh-CN.md
?? LICENSE
?? pyproject.toml
```

## Design principles

### Keep memory stable
Only store information that is likely to remain useful later.

### Keep memory compact
Prefer short structured entries over long transcripts.

### Keep memory explicit
Do not infer weak signals into permanent memory.

### Keep memory auditable
Use plain text so the memory layer is easy to inspect, edit, and version.

### Keep memory local
Do not require a cloud backend just to remember simple facts.

## Use cases

Open Memory Boost is useful when you want an assistant to:

- remember your tone and formatting preferences
- preserve project decisions across sessions
- keep track of ongoing work
- summarize completed sessions
- retrieve relevant context before answering
- maintain continuity without external dependencies

## Installation

Clone the repository, then use the `skill/` folder as a Codex skill installation source.

For the CLI, install with Python 3.10+ and run:

```powershell
open-memory-boost init
```

## License

MIT
