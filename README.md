# AI 商业顾问 / Business Growth Validation

本公开版仅包含通用离线工具、空白模板和合成测试，不包含维护者个人背景、履历、收入或收入目标、客户/朋友资料、个性化经营状态、研究活动记录和历史实验快照。

## 从这里开始

- [当前框架 v2](docs/business-consultant-framework-v2.md)：战略选择 → 商业模式 → 运营交付，验证与反馈贯穿全程。
- [任务与 Skill 路由](docs/skill-routing.md)：六项公开方法指南及一个旧名称入口，按具体任务调用。
- [公开版范围](docs/public-edition.md)：同步到 2026-10-05 的通用方法，不是私人工作区镜像。
- [空白实验卡](templates/experiment-card.md)与[空白画布](templates/business-canvas.md)：区分事实、假设、技术验证、采用与付款。

这是文件驱动的顾问工作流，不是自主后台服务；方法指南不能替代人工判断、客户验证或工具环境。

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
