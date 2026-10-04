"""Synthetic structural checks, not real-user or channel validation."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    'industry-content-research', 'benchmark-content-discovery',
    'video-storyboard-analysis', 'storyboard-dialogue-memes',
    'storyboard-editing', 'wechat-article-production',
)

class PublicDocsTests(unittest.TestCase):
    def test_six_guides_and_alias(self):
        for name in SKILLS + ('ai-account-discovery',):
            text = (ROOT / 'skills' / name / 'SKILL.md').read_text(encoding='utf-8')
            self.assertTrue(text.startswith('---\n'))
            self.assertIn('name: ' + name + '\n', text)
            self.assertIn('description:', text)

    def test_guides_disclose_execution_boundary(self):
        for name in SKILLS:
            text = (ROOT / 'skills' / name / 'SKILL.md').read_text(encoding='utf-8')
            self.assertIn('不是自动运行的服务', text)
            self.assertIn('真实任务状态', text)

    def test_markdown_links_resolve_inside_public_tree(self):
        paths = [ROOT / 'README.md', ROOT / 'START-HERE.md']
        for directory in ('docs', 'skills', 'templates'):
            paths.extend((ROOT / directory).rglob('*.md'))
        for path in paths:
            for target in re.findall(r'(?<!!)\[[^\]\n]+\]\(([^)\s]+)\)', path.read_text(encoding='utf-8')):
                if target.startswith(('https://', 'http://', '#', 'mailto:')):
                    continue
                target_path = (path.parent / target.split('#')[0]).resolve()
                self.assertTrue(target_path.is_relative_to(ROOT), (path, target))
                self.assertTrue(target_path.is_file(), (path, target))

    def test_scope_does_not_claim_private_workspace_mirror(self):
        text = (ROOT / 'docs/public-edition.md').read_text(encoding='utf-8')
        self.assertIn('不是个人工作区的逐字镜像', text)
        self.assertIn('未同步个人档案', text)

if __name__ == '__main__':
    unittest.main()
