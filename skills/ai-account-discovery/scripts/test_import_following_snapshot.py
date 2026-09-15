import importlib.util
import unittest
import json
import subprocess
import sys
import tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location('importer', Path(__file__).with_name('import_following_snapshot.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ImportTests(unittest.TestCase):
    def test_names_never_classify(self):
        data = module.parse_snapshot('- list [ref=a]:\n  - listitem [ref=b]:\n    - generic [ref=c]: AI老师\n', 'test')
        self.assertEqual(data['accounts'][0]['content_status'], 'unreviewed')
        self.assertFalse(data['list_complete'])

    def test_same_name_not_merged(self):
        text = '- list:\n  - listitem [ref=a]:\n    - generic [ref=b]: 同名\n  - listitem [ref=c]:\n    - generic [ref=d]: 同名\n'
        result = module.parse_snapshot(text, 'test')
        self.assertEqual(result['observed_records'], 2)
        self.assertEqual(result['distinct_nicknames'], 1)
        self.assertNotEqual(*[a['record_id'] for a in result['accounts']])

    def test_nested_avatar_not_account(self):
        text = '- list:\n  - listitem [ref=a]:\n    - listitem [ref=b]:\n      - img "头像"\n    - generic [ref=c]: 作者\n'
        result = module.parse_snapshot(text, 'test')
        self.assertEqual(result['observed_records'], 1)
        self.assertEqual(result['accounts'][0]['nickname'], '作者')

    def test_text_name_and_badge(self):
        text = '- list:\n  - listitem [ref=a]:\n    - generic [ref=b]: 认证徽章\n    - text: 作者\n    - img "☀️"\n'
        result = module.parse_snapshot(text, 'test')
        self.assertEqual(result['accounts'][0]['nickname'], '作者')
        self.assertEqual(result['accounts'][0]['visible_image_labels'], ['☀️'])

    def test_missing_name_fails(self):
        with self.assertRaises(ValueError):
            module.parse_snapshot('- list:\n  - listitem [ref=a]:\n    - img "未知"\n', 'test')

    def test_wrong_snapshot_fails(self):
        with self.assertRaises(ValueError):
            module.parse_snapshot('- generic: Welcome', 'test')


    def run_cli(self, snapshot, output):
        return subprocess.run(
            [sys.executable, '-X', 'utf8', str(Path(__file__).with_name('import_following_snapshot.py')),
             '--snapshot', str(snapshot), '--output', str(output)],
            capture_output=True, text=True, encoding='utf-8')

    def test_cli_bom_unicode_and_unverified_output(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot = Path(folder) / 'synthetic.yaml'
            output = Path(folder) / 'queue.json'
            snapshot.write_text('- list:\n  - listitem [ref=a]:\n    - generic [ref=b]: 创作样例号\n', encoding='utf-8-sig')
            result = self.run_cli(snapshot, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(data['accounts'][0]['nickname'], '创作样例号')
            self.assertIsNone(data['accounts'][0]['profile_url'])
            self.assertEqual(data['accounts'][0]['content_status'], 'unreviewed')
            self.assertFalse(data['identity_deduplicated'])
            self.assertFalse(data['list_complete'])

    def test_cli_never_overwrites_checkpoint(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot = Path(folder) / 'synthetic.yaml'
            output = Path(folder) / 'queue.json'
            snapshot.write_text('- list:\n  - listitem [ref=a]:\n    - generic [ref=b]: 示例号\n', encoding='utf-8')
            original = b'{"existing_evidence": true}\n'
            output.write_bytes(original)
            result = self.run_cli(snapshot, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_bytes(), original)

    def test_cli_invalid_snapshot_creates_no_output(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot = Path(folder) / 'welcome.yaml'
            output = Path(folder) / 'queue.json'
            snapshot.write_text('- generic: Welcome', encoding='utf-8')
            result = self.run_cli(snapshot, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())

    def test_cli_requires_verified_existing_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshot = Path(folder) / 'synthetic.yaml'
            output = Path(folder) / 'not-created' / 'queue.json'
            snapshot.write_text('- list:\n  - listitem [ref=a]:\n    - generic [ref=b]: 示例号\n', encoding='utf-8')
            result = self.run_cli(snapshot, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.parent.exists())

if __name__ == '__main__':
    unittest.main()
