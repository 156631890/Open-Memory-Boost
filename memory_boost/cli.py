from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import MemoryStore, default_store_path, load_store, normalize_tags, resolve_section


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="open-memory-boost", description="Local Markdown memory store for Codex")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create an empty memory store")

    add = subparsers.add_parser("add", help="Add a memory entry")
    add.add_argument("section", help="facts, preferences, decisions, open questions, or summaries")
    add.add_argument("text", help="Memory text")
    add.add_argument("--source", default="user", help="Memory source label")
    add.add_argument("--confidence", default="high", help="Memory confidence label")
    add.add_argument("--status", default="active", help="Memory status label")
    add.add_argument("--priority", default="medium", choices=["high", "medium", "low"], help="Memory priority")
    add.add_argument("--tag", action="append", default=[], help="Tag to attach to the entry")
    add.add_argument("--id", dest="entry_id", help="Explicit entry id")

    search = subparsers.add_parser("search", help="Search memory entries")
    search.add_argument("query", help="Search text")
    search.add_argument("--section", help="Restrict to a section")
    search.add_argument("--tag", action="append", default=[], help="Require tag match")
    search.add_argument("--limit", type=int, default=20, help="Maximum results")
    search.add_argument("--json", action="store_true", help="Emit JSON")
    search.add_argument("--include-deleted", action="store_true", help="Include deleted entries")

    list_cmd = subparsers.add_parser("list", help="List all memory entries")
    list_cmd.add_argument("--section", help="Restrict to a section")
    list_cmd.add_argument("--status", choices=["active", "deleted", "superseded"], help="Restrict by status")
    list_cmd.add_argument("--json", action="store_true", help="Emit JSON")
    list_cmd.add_argument("--include-deleted", action="store_true", help="Include deleted entries")

    update = subparsers.add_parser("update", help="Update a memory entry by id")
    update.add_argument("target", help="Entry id")
    update.add_argument("--text", help="New memory text")
    update.add_argument("--section", help="Move to another section")
    update.add_argument("--source", help="Memory source label")
    update.add_argument("--confidence", help="Memory confidence label")
    update.add_argument("--status", choices=["active", "deleted", "superseded"], help="Memory status label")
    update.add_argument("--priority", choices=["high", "medium", "low"], help="Memory priority")
    update.add_argument("--tag", action="append", default=None, help="Replace tags with these values")
    update.add_argument("--supersedes", help="Mark an older entry as superseded")

    forget = subparsers.add_parser("forget", help="Mark an entry as deleted")
    forget.add_argument("target", help="Entry id")

    compact = subparsers.add_parser("compact", help="Deduplicate and compact active memory")
    compact.add_argument("--json", action="store_true", help="Emit JSON summary")

    stats = subparsers.add_parser("stats", help="Show store statistics")
    stats.add_argument("--json", action="store_true", help="Emit JSON")

    export_cmd = subparsers.add_parser("export", help="Export memory as JSON")
    export_cmd.add_argument("--path", type=Path, help="Export destination")

    import_cmd = subparsers.add_parser("import", help="Import memory from JSON")
    import_cmd.add_argument("path", type=Path, help="JSON file to import")
    import_cmd.add_argument("--replace", action="store_true", help="Replace existing entries instead of merging")

    summary = subparsers.add_parser("summary", help="Produce a compact memory summary")
    summary.add_argument("--section", help="Restrict summary to a section")
    summary.add_argument("--limit", type=int, default=5, help="Max recent entries to include")

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


def emit(entries, as_json: bool) -> None:
    if as_json:
        print(json.dumps([entry.to_dict() if hasattr(entry, "to_dict") else entry for entry in entries], ensure_ascii=False, indent=2))
        return
    for entry in entries:
        print(f"[{entry.section}] {entry.format_line()}")


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    store_path, parser_argv = extract_store(raw_argv)
    parser = build_parser()
    args = parser.parse_args(parser_argv)
    store = load_store(store_path)

    if args.command == "init":
        store.ensure()
        print(store.path)
        return 0

    if args.command == "add":
        entry = store.add(
            args.section,
            args.text,
            source=args.source,
            confidence=args.confidence,
            status=args.status,
            priority=args.priority,
            tags=normalize_tags(args.tag),
            id=args.entry_id,
        )
        print(f"[{entry.section}] {entry.format_line()}")
        return 0

    if args.command == "search":
        hits = store.search(args.query, section=args.section, tags=args.tag, include_deleted=args.include_deleted, limit=args.limit)
        if args.json:
            print(json.dumps([{ "score": hit.score, **hit.entry.to_dict() } for hit in hits], ensure_ascii=False, indent=2))
        else:
            for hit in hits:
                print(f"[{hit.entry.section}] score={hit.score} {hit.entry.format_line()}")
        return 0

    if args.command == "list":
        entries = store.list_entries(section=args.section, status=args.status, include_deleted=args.include_deleted)
        if args.json:
            print(json.dumps([entry.to_dict() for entry in entries], ensure_ascii=False, indent=2))
        else:
            emit(entries, False)
        return 0

    if args.command == "update":
        updated = store.update(
            args.target,
            text=args.text,
            section=args.section,
            source=args.source,
            confidence=args.confidence,
            status=args.status,
            priority=args.priority,
            tags=args.tag,
            supersedes=args.supersedes,
        )
        print(f"[{updated.section}] {updated.format_line()}")
        return 0

    if args.command == "forget":
        forgotten = store.forget(args.target)
        print(f"[{forgotten.section}] {forgotten.format_line()}")
        return 0

    if args.command == "compact":
        result = store.compact()
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"superseded={result['superseded']} active={result['active']}")
        return 0

    if args.command == "stats":
        stats = store.stats()
        if args.json:
            print(json.dumps(stats.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"total={stats.total} active={stats.active} deleted={stats.deleted} superseded={stats.superseded}")
            for section, count in stats.by_section.items():
                print(f"{section}={count}")
        return 0

    if args.command == "export":
        path = store.export_json(args.path)
        print(path)
        return 0

    if args.command == "import":
        imported = store.import_json(args.path, merge=not args.replace)
        print(imported)
        return 0

    if args.command == "summary":
        print(store.summarize(section=args.section, limit=args.limit))
        return 0

    parser.error("unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
