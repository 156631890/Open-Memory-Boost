# Open Memory Boost

[![CI](https://github.com/156631890/Open-Memory-Boost/actions/workflows/ci.yml/badge.svg)](https://github.com/156631890/Open-Memory-Boost/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

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

## Quick start

```powershell
git clone git@github.com:156631890/Open-Memory-Boost.git
cd Open-Memory-Boost
open-memory-boost init
open-memory-boost add facts "User prefers concise answers"
open-memory-boost search concise
```

## Memory types

Open Memory Boost organizes information into a few simple buckets:

- `Facts`
- `Preferences`
- `Decisions`
- `Open Questions`
- `Session Summaries`

## Project structure

```text
open-memory-boost/
├─ skill/
├─ memory_boost/
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
