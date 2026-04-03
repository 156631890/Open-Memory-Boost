from __future__ import annotations

from .core import (
    MemoryEntry,
    MemoryStore,
    SECTIONS,
    SearchHit,
    StoreStats,
    default_store_path,
    ensure_store,
    format_entry,
    load_store,
    normalize_tags,
    normalize_text,
    now_date,
    render_empty_store,
    resolve_section,
)


def add_entry(*args, **kwargs):
    return load_store(kwargs.pop("store", None)).add(*args, **kwargs)


def iter_entries(store):
    return load_store(store).load()


def search_entries(store, query):
    return load_store(store).search(query)
