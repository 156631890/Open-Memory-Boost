from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
import re

SECTIONS = ["Facts", "Preferences", "Decisions", "Open Questions", "Session Summaries"]
SECTION_ALIASES = {
    "fact": "Facts",
    "facts": "Facts",
    "preference": "Preferences",
    "preferences": "Preferences",
    "decision": "Decisions",
    "decisions": "Decisions",
    "question": "Open Questions",
    "open_question": "Open Questions",
    "open questions": "Open Questions",
    "summary": "Session Summaries",
    "summaries": "Session Summaries",
    "session summaries": "Session Summaries",
}
ENTRY_RE = re.compile(r"^- (?P<meta>(?:\[[^\]]+\]\s*)+)(?P<text>.*)$")
META_RE = re.compile(r"\[([^=\]]+)=([^\]]*)\]")


@dataclass
class MemoryEntry:
    section: str
    text: str
    timestamp: str
    source: str = "user"
    confidence: str = "high"
    status: str = "active"

    def format(self) -> str:
        meta = f"[date={self.timestamp}] [source={self.source}] [confidence={self.confidence}] [status={self.status}]"
        return f"- {meta} {self.text}"


def resolve_section(section: str) -> str:
    key = section.strip().lower()
    if key not in SECTION_ALIASES:
        raise ValueError(f"Unknown section: {section}. Use one of: {', '.join(SECTIONS)}")
    return SECTION_ALIASES[key]


def default_store_path(root: Path | None = None) -> Path:
    root = root or Path.cwd()
    return root / ".open-memory-boost" / "memory.md"


def ensure_store(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(render_empty_store(), encoding="utf-8")


def render_empty_store() -> str:
    lines = ["# Open Memory Boost Store", ""]
    for section in SECTIONS:
        lines.extend([f"## {section}", ""])
    return "\n".join(lines).rstrip() + "\n"


def current_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _section_block_lines(content: str, section: str) -> list[str]:
    lines = content.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip() == f"## {section}":
            start = idx
            break
    if start is None:
        return []
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("## "):
            end = idx
            break
    return lines[start:end]


def add_entry(store: Path, section: str, text: str, source: str = "user", confidence: str = "high", status: str = "active") -> MemoryEntry:
    ensure_store(store)
    section = resolve_section(section)
    entry = MemoryEntry(section=section, text=text.strip(), timestamp=current_timestamp(), source=source, confidence=confidence, status=status)
    content = store.read_text(encoding="utf-8")
    if f"## {section}" not in content:
        content = content.rstrip() + f"\n\n## {section}\n"
    block = _section_block_lines(content, section)
    if not block:
        lines = content.rstrip().splitlines()
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend([f"## {section}", entry.format(), ""])
        store.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return entry

    insert_at = block[-1:] and len(block) or 0
    updated = []
    in_section = False
    inserted = False
    for line in content.splitlines():
        if line.strip() == f"## {section}":
            in_section = True
            updated.append(line)
            continue
        if in_section and line.startswith("## ") and not inserted:
            updated.append(entry.format())
            updated.append("")
            inserted = True
            in_section = False
        updated.append(line)
    if in_section and not inserted:
        updated.append(entry.format())
        inserted = True
    if not inserted:
        updated.extend([entry.format(), ""])
    normalized = []
    prev_blank = False
    for line in updated:
        blank = line.strip() == ""
        if blank and prev_blank:
            continue
        normalized.append(line)
        prev_blank = blank
    store.write_text("\n".join(normalized).rstrip() + "\n", encoding="utf-8")
    return entry


def iter_entries(store: Path) -> Iterable[MemoryEntry]:
    if not store.exists():
        return []
    section = None
    for raw_line in store.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if not line.startswith("- ") or section is None:
            continue
        match = ENTRY_RE.match(line)
        if not match:
            continue
        meta_text = match.group("meta")
        text = match.group("text").strip()
        fields = {"date": "", "source": "user", "confidence": "high", "status": "active"}
        for key, value in META_RE.findall(meta_text):
            fields[key] = value
        yield MemoryEntry(section=section, text=text, timestamp=fields.get("date", ""), source=fields.get("source", "user"), confidence=fields.get("confidence", "high"), status=fields.get("status", "active"))


def search_entries(store: Path, query: str) -> list[MemoryEntry]:
    query_l = query.lower().strip()
    if not query_l:
        return list(iter_entries(store))
    matches = []
    for entry in iter_entries(store):
        haystack = " ".join([entry.section, entry.text, entry.source, entry.confidence, entry.status]).lower()
        if query_l in haystack:
            matches.append(entry)
    return matches
