# Memory Boost

Memory Boost is a small open-source Codex skill and local Markdown memory runtime.

It helps an agent:

- record stable facts, preferences, decisions, and open questions
- retrieve relevant memory before answering
- keep memory compact and auditable
- avoid depending on external memory services

## What is included

- `skill/` - the Codex skill definition
- `memory_boost/` - a tiny Python CLI for local Markdown memory
- `examples/` - sample memory output

## Quick start

1. Install the skill by copying `skill/` into your Codex skills directory.
2. Initialize a local store:

```powershell
python -m memory_boost init
```

3. Add memory:

```powershell
python -m memory_boost add facts "User prefers concise answers"
python -m memory_boost add preferences "User prefers Chinese responses for local work"
```

4. Search memory:

```powershell
python -m memory_boost search concise
```

## Default storage

The CLI stores memory in `.memory-boost/memory.md` in the current working directory unless you pass `--store`.

## Project philosophy

- Keep memory stable and useful.
- Prefer explicit user-confirmed facts over inference.
- Mark outdated items as superseded instead of silently deleting them.

## License

MIT
