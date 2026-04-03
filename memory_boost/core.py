from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import uuid
from typing import Iterable, Sequence

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
    id: str
    section: str
    text: str
    timestamp: str
    updated_at: str
    source: str = "user"
    confidence: str = "high"
    status: str = "active"
    priority: str = "medium"
    tags: list[str] = field(default_factory=list)
    supersedes: str = ""

    def meta(self) -> dict[str, str]:
        data = {
            "id": self.id,
            "date": self.timestamp,
            "updated": self.updated_at,
            "source": self.source,
            "confidence": self.confidence,
            "status": self.status,
            "priority": self.priority,
            "tags": ",".join(self.tags),
        }
        if self.supersedes:
            data["supersedes"] = self.supersedes
        return data

    def format_line(self) -> str:
        parts = [f"[{key}={value}]" for key, value in self.meta().items() if value]
        return f"- {' '.join(parts)} {self.text}".rstrip()

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class SearchHit:
    entry: MemoryEntry
    score: int


@dataclass
class StoreStats:
    total: int
    active: int
    deleted: int
    superseded: int
    by_section: dict[str, int]
    by_priority: dict[str, int]

    def to_dict(self) -> dict[str, object]:
        return {
            "total": self.total,
            "active": self.active,
            "deleted": self.deleted,
            "superseded": self.superseded,
            "by_section": self.by_section,
            "by_priority": self.by_priority,
        }


def resolve_section(section: str) -> str:
    key = section.strip().lower()
    if key not in SECTION_ALIASES:
        raise ValueError(f"Unknown section: {section}. Use one of: {', '.join(SECTIONS)}")
    return SECTION_ALIASES[key]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def tokenize_text(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", normalize_text(text)) if token]


def text_similarity(left: str, right: str) -> float:
    left_tokens = set(tokenize_text(left))
    right_tokens = set(tokenize_text(right))
    if not left_tokens or not right_tokens:
        return 0.0
    shared = len(left_tokens & right_tokens)
    return shared / max(len(left_tokens), len(right_tokens))


def normalize_tags(tags: Sequence[str] | None) -> list[str]:
    if not tags:
        return []
    out: list[str] = []
    for tag in tags:
        for piece in re.split(r"[, ]+", tag.strip()):
            if not piece:
                continue
            cleaned = piece.strip().lower()
            if cleaned and cleaned not in out:
                out.append(cleaned)
    return out


def now_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


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


def _stable_legacy_id(section: str, text: str, timestamp: str) -> str:
    digest = hashlib.sha1(f"{section}|{text}|{timestamp}".encode("utf-8")).hexdigest()[:12]
    return f"legacy-{digest}"


def _parse_record(section: str, line: str) -> MemoryEntry | None:
    match = ENTRY_RE.match(line.strip())
    if not match:
        return None
    meta_text = match.group("meta")
    text = match.group("text").strip()
    fields = {
        "id": "",
        "date": "",
        "updated": "",
        "source": "user",
        "confidence": "high",
        "status": "active",
        "priority": "medium",
        "tags": "",
        "supersedes": "",
    }
    for key, value in META_RE.findall(meta_text):
        fields[key] = value
    timestamp = fields["date"] or now_date()
    updated_at = fields["updated"] or timestamp
    entry_id = fields["id"] or _stable_legacy_id(section, text, timestamp)
    tags = normalize_tags([fields["tags"]])
    return MemoryEntry(
        id=entry_id,
        section=section,
        text=text,
        timestamp=timestamp,
        updated_at=updated_at,
        source=fields["source"],
        confidence=fields["confidence"],
        status=fields["status"],
        priority=fields["priority"],
        tags=tags,
        supersedes=fields["supersedes"],
    )


class MemoryStore:
    def __init__(self, path: Path):
        self.path = path

    @classmethod
    def open(cls, path: Path | None = None) -> "MemoryStore":
        return cls(path or default_store_path())

    def ensure(self) -> None:
        ensure_store(self.path)

    def load(self) -> list[MemoryEntry]:
        if not self.path.exists():
            return []
        content = self.path.read_text(encoding="utf-8")
        section = None
        entries: list[MemoryEntry] = []
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if line.startswith("## "):
                section = line[3:].strip()
                continue
            if not line.startswith("- ") or section is None:
                continue
            entry = _parse_record(section, line)
            if entry is not None:
                entries.append(entry)
        return entries

    def save(self, entries: Sequence[MemoryEntry]) -> None:
        self.ensure()
        by_section: dict[str, list[MemoryEntry]] = {section: [] for section in SECTIONS}
        extras: dict[str, list[MemoryEntry]] = {}
        for entry in entries:
            by_section.setdefault(entry.section, extras.setdefault(entry.section, [])).append(entry)
        lines = ["# Open Memory Boost Store", ""]
        for section in SECTIONS + [s for s in by_section if s not in SECTIONS]:
            lines.append(f"## {section}")
            section_entries = by_section.get(section, [])
            if not section_entries:
                lines.append("")
                continue
            for entry in section_entries:
                lines.append(entry.format_line())
            lines.append("")
        self.path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    def add(
        self,
        section: str,
        text: str,
        *,
        source: str = "user",
        confidence: str = "high",
        status: str = "active",
        priority: str = "medium",
        tags: Sequence[str] | None = None,
        id: str | None = None,
    ) -> MemoryEntry:
        entries = self.load()
        section_name = resolve_section(section)
        entry = MemoryEntry(
            id=id or uuid.uuid4().hex[:12],
            section=section_name,
            text=text.strip(),
            timestamp=now_date(),
            updated_at=now_date(),
            source=source,
            confidence=confidence,
            status=status,
            priority=priority,
            tags=normalize_tags(tags),
        )
        entries.append(entry)
        self.save(entries)
        return entry

    def get(self, target: str) -> MemoryEntry | None:
        for entry in self.load():
            if entry.id == target:
                return entry
        return None

    def resolve(self, target: str, *, section: str | None = None, include_deleted: bool = False) -> list[MemoryEntry]:
        entries = self.load()
        if not include_deleted:
            entries = [entry for entry in entries if entry.status != "deleted"]
        if section:
            section_name = resolve_section(section)
            entries = [entry for entry in entries if entry.section == section_name]
        exact = [entry for entry in entries if entry.id == target]
        if exact:
            return exact
        exact_text = [entry for entry in entries if normalize_text(entry.text) == normalize_text(target)]
        if exact_text:
            return exact_text
        query = normalize_text(target)
        return [entry for entry in entries if query in normalize_text(entry.text) or query in normalize_text(entry.section) or query in ",".join(entry.tags)]

    def update(
        self,
        target: str,
        *,
        text: str | None = None,
        section: str | None = None,
        source: str | None = None,
        confidence: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        tags: Sequence[str] | None = None,
        supersedes: str | None = None,
    ) -> MemoryEntry:
        entries = self.load()
        updated = None
        resolved_section = resolve_section(section) if section else None
        for entry in entries:
            if entry.id != target:
                continue
            if text is not None:
                entry.text = text.strip()
            if resolved_section is not None:
                entry.section = resolved_section
            if source is not None:
                entry.source = source
            if confidence is not None:
                entry.confidence = confidence
            if status is not None:
                entry.status = status
            if priority is not None:
                entry.priority = priority
            if tags is not None:
                entry.tags = normalize_tags(tags)
            if supersedes is not None:
                entry.supersedes = supersedes
            entry.updated_at = now_date()
            updated = entry
            break
        if updated is None:
            raise ValueError(f"No entry found with id: {target}")
        self.save(entries)
        return updated

    def forget(self, target: str) -> MemoryEntry:
        return self.update(target, status="deleted")

    def search(
        self,
        query: str,
        *,
        section: str | None = None,
        tags: Sequence[str] | None = None,
        include_deleted: bool = False,
        limit: int | None = None,
    ) -> list[SearchHit]:
        query_norm = normalize_text(query)
        query_tokens = [token for token in re.split(r"\s+", query_norm) if token]
        tag_filter = set(normalize_tags(tags))
        entries = self.load()
        hits: list[SearchHit] = []
        for entry in entries:
            if not include_deleted and entry.status == "deleted":
                continue
            if section and entry.section != resolve_section(section):
                continue
            if tag_filter and not tag_filter.issubset(set(entry.tags)):
                continue
            haystack = normalize_text(" ".join([entry.section, entry.text, entry.source, entry.confidence, entry.status, entry.priority, ",".join(entry.tags), entry.id]))
            score = 0
            if query_norm and query_norm in haystack:
                score += 8
            for token in query_tokens:
                if token in haystack:
                    score += 2
            if entry.priority == "high":
                score += 1
            if entry.status == "active":
                score += 1
            if query_norm and entry.text.lower().startswith(query_norm):
                score += 2
            if score > 0 or not query_norm:
                hits.append(SearchHit(entry=entry, score=score))
        hits.sort(key=lambda hit: (-hit.score, -_date_sort_key(hit.entry.updated_at), -_date_sort_key(hit.entry.timestamp), hit.entry.section, hit.entry.text.lower()))
        return hits[:limit] if limit else hits

    def list_entries(
        self,
        *,
        section: str | None = None,
        status: str | None = None,
        include_deleted: bool = True,
    ) -> list[MemoryEntry]:
        entries = self.load()
        if section:
            entries = [entry for entry in entries if entry.section == resolve_section(section)]
        if status:
            entries = [entry for entry in entries if entry.status == status]
        if not include_deleted:
            entries = [entry for entry in entries if entry.status != "deleted"]
        return entries

    def compact(self) -> dict[str, int]:
        entries = self.load()
        seen: dict[tuple[str, str], MemoryEntry] = {}
        removed = 0
        for entry in entries:
            if entry.status != "active":
                continue
            primary = None
            for candidate in seen.values():
                if candidate.section != entry.section:
                    continue
                if normalize_text(candidate.text) == normalize_text(entry.text) or text_similarity(candidate.text, entry.text) >= 0.8:
                    primary = candidate
                    break
            if primary is None:
                seen[entry.id] = entry
                continue
            merged_tags = list(dict.fromkeys(primary.tags + entry.tags))
            primary.tags = merged_tags
            if entry.priority == "high":
                primary.priority = "high"
            if len(entry.text) > len(primary.text):
                primary.text = entry.text
            entry.status = "superseded"
            entry.supersedes = primary.id
            entry.updated_at = now_date()
            removed += 1
        self.save(entries)
        return {"superseded": removed, "active": sum(1 for entry in entries if entry.status == "active")}

    def stats(self) -> StoreStats:
        entries = self.load()
        by_section = {section: 0 for section in SECTIONS}
        by_priority = {"high": 0, "medium": 0, "low": 0}
        active = deleted = superseded = 0
        for entry in entries:
            by_section[entry.section] = by_section.get(entry.section, 0) + 1
            by_priority[entry.priority] = by_priority.get(entry.priority, 0) + 1
            if entry.status == "active":
                active += 1
            elif entry.status == "deleted":
                deleted += 1
            elif entry.status == "superseded":
                superseded += 1
        return StoreStats(total=len(entries), active=active, deleted=deleted, superseded=superseded, by_section=by_section, by_priority=by_priority)

    def summarize(self, *, section: str | None = None, limit: int = 5) -> str:
        entries = self.list_entries(section=section, include_deleted=False)
        if not entries:
            return "No active memory entries."
        counts = self.stats().by_section
        lines = ["Memory summary:"]
        for sec in SECTIONS:
            if counts.get(sec, 0):
                lines.append(f"- {sec}: {counts[sec]} entries")
        lines.append("")
        lines.append("Recent active entries:")
        for entry in entries[-limit:]:
            lines.append(f"- [{entry.section}] {entry.text}")
        return "\n".join(lines).rstrip()

    def export_json(self, path: Path | None = None) -> Path:
        path = path or self.path.with_suffix(".json")
        payload = [entry.to_dict() for entry in self.load()]
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def import_json(self, path: Path, *, merge: bool = True) -> int:
        data = json.loads(path.read_text(encoding="utf-8"))
        imported: list[MemoryEntry] = []
        for item in data:
            imported.append(MemoryEntry(
                id=item.get("id") or uuid.uuid4().hex[:12],
                section=resolve_section(item.get("section", "Facts")),
                text=str(item.get("text", "")).strip(),
                timestamp=item.get("timestamp") or now_date(),
                updated_at=item.get("updated_at") or item.get("timestamp") or now_date(),
                source=item.get("source", "user"),
                confidence=item.get("confidence", "high"),
                status=item.get("status", "active"),
                priority=item.get("priority", "medium"),
                tags=normalize_tags(item.get("tags", [])),
                supersedes=item.get("supersedes", ""),
            ))
        if merge:
            entries = self.load() + imported
        else:
            entries = imported
        self.save(entries)
        return len(imported)


def _date_sort_key(value: str) -> int:
    try:
        return int(value.replace("-", ""))
    except ValueError:
        return 0


def format_entry(entry: MemoryEntry) -> str:
    tags = f" tags={','.join(entry.tags)}" if entry.tags else ""
    return f"[{entry.section}] {entry.format_line()}" if entry else ""


def load_store(path: Path | None = None) -> MemoryStore:
    return MemoryStore.open(path)
