from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .store import add_entry, default_store_path, ensure_store, iter_entries, resolve_section, search_entries


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="memory-boost", description="Local Markdown memory store for Codex")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create an empty memory store")

    add = subparsers.add_parser("add", help="Add a memory entry")
    add.add_argument("section", help="facts, preferences, decisions, open questions, or summaries")
    add.add_argument("text", help="Memory text")
    add.add_argument("--source", default="user", help="Memory source label")
    add.add_argument("--confidence", default="high", help="Memory confidence label")
    add.add_argument("--status", default="active", help="Memory status label")

    search = subparsers.add_parser("search", help="Search memory entries")
    search.add_argument("query", help="Search text")

    subparsers.add_parser("list", help="List all memory entries")
    return parser


def extract_store(argv: list[str]) -> tuple[Path, list[str]]:
    if "--store" not in argv:
        return default_store_path(), argv
    idx = argv.index("--store")
    try:
        store_value = Path(argv[idx + 1])
    except IndexError as exc:
        raise SystemExit("--store requires a path") from exc
    remaining = argv[:idx] + argv[idx + 2:]
    return store_value, remaining


def cmd_init(store: Path) -> int:
    ensure_store(store)
    print(store)
    return 0


def cmd_add(store: Path, args: argparse.Namespace) -> int:
    entry = add_entry(store, args.section, args.text, source=args.source, confidence=args.confidence, status=args.status)
    print(entry.format())
    return 0


def cmd_search(store: Path, args: argparse.Namespace) -> int:
    results = search_entries(store, args.query)
    for entry in results:
        print(f"[{entry.section}] {entry.format()}")
    return 0


def cmd_list(store: Path) -> int:
    for entry in iter_entries(store):
        print(f"[{entry.section}] {entry.format()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    store, parser_argv = extract_store(raw_argv)
    parser = build_parser()
    args = parser.parse_args(parser_argv)
    if args.command == "init":
        return cmd_init(store)
    if args.command == "add":
        resolve_section(args.section)
        return cmd_add(store, args)
    if args.command == "search":
        return cmd_search(store, args)
    if args.command == "list":
        return cmd_list(store)
    parser.error("unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
