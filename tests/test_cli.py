from __future__ import annotations

import contextlib
import io
import tempfile
from pathlib import Path
import unittest

from memory_boost.cli import main


class CLITests(unittest.TestCase):
    def run_cli(self, *args: str) -> str:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(list(args))
        self.assertEqual(code, 0)
        return buf.getvalue().strip()

    def test_cli_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "memory.md"
            out = self.run_cli("--store", str(store), "init")
            self.assertIn("memory.md", out)

            add_out = self.run_cli("--store", str(store), "add", "facts", "User prefers concise answers", "--tag", "tone", "--priority", "high")
            self.assertIn("User prefers concise answers", add_out)

            search_out = self.run_cli("--store", str(store), "search", "concise")
            self.assertIn("score=", search_out)

            stats_out = self.run_cli("--store", str(store), "stats")
            self.assertIn("total=", stats_out)

            summary_out = self.run_cli("--store", str(store), "summary")
            self.assertIn("Memory summary", summary_out)


if __name__ == "__main__":
    unittest.main()
