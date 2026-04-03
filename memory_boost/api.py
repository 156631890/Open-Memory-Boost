from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .core import MemoryStore, SearchHit, StoreStats, default_store_path, format_entry, load_store


class MemoryAPI:
    """Programmatic API for local memory operations."""

    def __init__(self, store: Path | None = None):
        self.store = load_store(store)

    def add(self, section: str, text: str, **kwargs):
        return self.store.add(section, text, **kwargs)

    def search(self, query: str, **kwargs):
        return self.store.search(query, **kwargs)

    def list(self, **kwargs):
        return self.store.list_entries(**kwargs)

    def update(self, target: str, **kwargs):
        return self.store.update(target, **kwargs)

    def forget(self, target: str):
        return self.store.forget(target)

    def compact(self):
        return self.store.compact()

    def stats(self) -> StoreStats:
        return self.store.stats()

    def summarize(self, **kwargs) -> str:
        return self.store.summarize(**kwargs)

    def export_json(self, path: Path | None = None) -> Path:
        return self.store.export_json(path)

    def import_json(self, path: Path, *, merge: bool = True) -> int:
        return self.store.import_json(path, merge=merge)
