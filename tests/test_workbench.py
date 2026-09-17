import json
import os
import uuid
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "ai_business_consultant.py"


class WorkbenchSmokeTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=ROOT, text=True, encoding="utf-8", capture_output=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})

    def test_status(self):
        result = self.run_cli("status")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("v0.1", result.stdout)

    def test_validate(self):
        result = self.run_cli("validate")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_canvas_generation(self):
        title = "smoke-" + uuid.uuid4().hex
        output = ROOT / "workspace" / "outputs" / f"canvas-{title}.md"
        self.addCleanup(output.unlink, missing_ok=True)
        result = self.run_cli("card", "canvas", "--title", title)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(output.exists())
        self.assertIn("商业画布", output.read_text(encoding="utf-8"))
        output.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
