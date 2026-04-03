from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest

from memory_boost.api import MemoryAPI
from memory_boost.core import MemoryStore


class MemoryStoreTests(unittest.TestCase):
    def test_add_search_update_forget_compact_export_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store_path = Path(tmp) / "memory.md"
            store = MemoryStore.open(store_path)

            a = store.add("facts", "User prefers concise answers", tags=["tone", "style"], priority="high")
            b = store.add("preferences", "User prefers Chinese responses for local work", tags=["lang"])
            c = store.add("facts", "User prefers concise answers", tags=["tone"])

            self.assertNotEqual(a.id, b.id)
            self.assertTrue(a.id)
            self.assertEqual(store.search("concise")[0].entry.id, a.id)
            self.assertGreaterEqual(len(store.search("user prefers")), 2)

            updated = store.update(a.id, text="User prefers concise, direct answers", tags=["tone", "direct"])
            self.assertEqual(updated.text, "User prefers concise, direct answers")
            self.assertIn("direct", updated.tags)

            forgotten = store.forget(b.id)
            self.assertEqual(forgotten.status, "deleted")

            compacted = store.compact()
            self.assertGreaterEqual(compacted["superseded"], 1)

            stats = store.stats()
            self.assertGreaterEqual(stats.total, 3)
            self.assertGreaterEqual(stats.deleted, 1)

            export_path = store.export_json(Path(tmp) / "memory.json")
            self.assertTrue(export_path.exists())
            payload = json.loads(export_path.read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(payload), 3)

            imported_store = MemoryStore.open(Path(tmp) / "imported.md")
            count = imported_store.import_json(export_path, merge=False)
            self.assertEqual(count, len(payload))
            self.assertGreaterEqual(len(imported_store.load()), len(payload))

    def test_summary_and_api(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store_path = Path(tmp) / "memory.md"
            api = MemoryAPI(store_path)
            api.add("facts", "User likes concise answers")
            api.add("decisions", "Use open-memory-boost as the project name")
            summary = api.summarize()
            self.assertIn("Memory summary", summary)
            self.assertIn("Facts", summary)
            self.assertIn("Recent active entries", summary)
            self.assertGreaterEqual(api.stats().active, 2)


if __name__ == "__main__":
    unittest.main()
