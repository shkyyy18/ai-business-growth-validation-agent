import argparse
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("workbench_privacy", ROOT / "tools/ai_business_consultant.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ValidatePrivacyTests(unittest.TestCase):
    def run_manifest(self, names):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "private").mkdir()
            (root / "private/broken.json").write_bytes(b"\xff\xfe")
            (root / "reviewed.json").write_text("{}", encoding="utf-8")
            (root / ".publication-manifest.json").write_text(json.dumps({"schema_version": 1, "files": {n: "0" * 64 for n in names}}), encoding="utf-8")
            with patch.object(module, "ROOT", root), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                return module.cmd_validate(argparse.Namespace())

    def test_private_non_utf8_ignored(self):
        self.assertEqual(self.run_manifest(["reviewed.json"]), 0)

    def test_private_entry_rejected(self):
        self.assertEqual(self.run_manifest(["private/broken.json"]), 1)

    def test_traversal_rejected(self):
        self.assertEqual(self.run_manifest(["../outside.json"]), 1)

    def test_missing_reviewed_file_rejected(self):
        self.assertEqual(self.run_manifest(["missing.json"]), 1)
