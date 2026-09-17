# AI Business Growth Validation — code and templates

公开候选版本仅包含通用离线工具、空白模板和合成测试，不包含维护者个人背景、履历、收入或收入目标、客户/朋友资料、个性化经营状态、研究活动记录和历史实验快照。

## Included
- `tools/ai_business_consultant.py`: a file-first offline workbench for blank canvas/hypothesis cards and user-controlled local imports.
- `tools/business_metrics.py`: explicitly defined metric calculations; no automatic platform data collection.
- `tools/consultant_case.py`: evidence-file integrity and structured handoff helpers; not market validation.
- `tools/research_corpus.py`: validation/retrieval helpers for separately supplied, authorized materials. No research corpus is bundled.
- `templates/business-canvas.md`: a blank business canvas.
- Synthetic tests for calculations, transport-frame parsing and the workbench.

## Offline smoke checks
```console
python -m unittest discover -s tests -v
python tools/ai_business_consultant.py status
python tools/ai_business_consultant.py card canvas --title synthetic-demo
python tools/ai_business_consultant.py validate
python scripts/check_publication.py --history
```

`business/`, `private/` and `workspace/` are local-only. A fresh clone has no personal business state; do not reconstruct a maintainer profile from old versions. Generated cards are drafts, not customer evidence or revenue claims.

## Scope
This is a deliberately smaller code distribution. Personal A/B tests, real-account research datasets, populated canvases, source snapshots and personal decisions are not published. Original-case/research-corpus replay tests are not included because their inputs are not part of this distribution. Passing synthetic tests is not proof of actual customer delivery, autonomous operation, successful business validation or investment/health outcomes.

See `docs/privacy-and-publishing.md` before adding any content. The content manifest is a review boundary, not an automatic detector of all personal information.
