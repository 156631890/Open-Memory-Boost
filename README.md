# Open Memory Boost

[![CI](https://github.com/156631890/Open-Memory-Boost/actions/workflows/ci.yml/badge.svg)](https://github.com/156631890/Open-Memory-Boost/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Open Memory Boost is a local-first memory engine and Codex skill.

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
- compacting, exporting, and importing memory stores

### 2. A Local Markdown Memory Runtime

A small command-line tool and Python API for working with plain Markdown memory files.

It supports:

- `init` - create a new memory store
- `add` - add a memory entry
- `search` - search existing memory
- `list` - list all stored memory
- `update` - edit an existing entry
- `forget` - mark an entry as deleted
- `compact` - deduplicate near-identical entries
- `stats` - inspect store health
- `export` - write JSON backups
- `import` - restore JSON backups
- `summary` - print a compact review

## Quick start

```powershell
git clone git@github.com:156631890/Open-Memory-Boost.git
cd Open-Memory-Boost
open-memory-boost init
open-memory-boost add facts "User prefers concise answers" --tag tone --priority high
open-memory-boost search concise
open-memory-boost stats
open-memory-boost summary
```

## Memory types

Open Memory Boost organizes information into a few simple buckets:

- `Facts`
- `Preferences`
- `Decisions`
- `Open Questions`
- `Session Summaries`

## Key features

- Local-first and offline-friendly
- No external API required
- Human-readable Markdown storage
- Simple CLI for adding, searching, updating, and forgetting memory
- Python API for developer integrations
- JSON export/import for backups and tooling
- Fuzzy compaction for near-duplicate memory entries
- Designed for stable, reusable context rather than raw chat logs
- Easy to audit, backup, and version with Git

## Developer API

Use `memory_boost.api.MemoryAPI` from Python when you want to integrate memory into another tool or agent.

```python
from memory_boost.api import MemoryAPI

api = MemoryAPI()
entry = api.add("facts", "User prefers concise answers", tags=["tone"], priority="high")
hits = api.search("concise")
summary = api.summarize()
```

## Project structure

```text
open-memory-boost/
├─ skill/
├─ memory_boost/
├─ tests/
├─ examples/
├─ README.md
├─ README.zh-CN.md
├─ CHANGELOG.md
├─ LICENSE
└─ pyproject.toml
```

## Installation

For the CLI, install with Python 3.10+ and run:

```powershell
open-memory-boost init
```

## Release

This repository follows a simple release flow:

- update the changelog
- tag the commit
- create a GitHub release from the tag

## License

MIT
