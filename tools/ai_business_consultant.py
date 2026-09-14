"""AI商业顾问个人验证工作台 v0.1.

标准库实现，刻意保持单用户、文件优先、人工确认，不自动调用模型或外部平台。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "workspace"
IMPORTS = WORKSPACE / "imports"
OUTPUTS = WORKSPACE / "outputs"
STATE = ROOT / "business" / "STATE.md"
FOUNDER = ROOT / "business" / "founder-profile.md"


def now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def slug(value: str) -> str:
    safe = "".join(c.lower() if c.isalnum() else "-" for c in value).strip("-")
    return safe or "item"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def cmd_status(_: argparse.Namespace) -> int:
    print("AI商业顾问个人验证工作台 v0.1")
    print(f"项目目录: {ROOT}")
    print(f"状态文件: {'已找到' if STATE.exists() else '缺失'}")
    print(f"发起人档案: {'已找到' if FOUNDER.exists() else '缺失'}")
    print(f"导入资料: {len(list(IMPORTS.glob('*'))) if IMPORTS.exists() else 0} 个")
    print(f"工作台输出: {len(list(OUTPUTS.glob('*'))) if OUTPUTS.exists() else 0} 个")
    print("当前边界: 文件优先 + 人工确认；不自动发布、私信、直播回复或做商业决策。")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    source = Path(args.source).expanduser().resolve()
    if not source.is_file():
        print(f"错误：找不到文件 {source}", file=sys.stderr)
        return 2
    IMPORTS.mkdir(parents=True, exist_ok=True)
    target = IMPORTS / source.name
    if target.exists() and not args.force:
        print(f"目标已存在：{target}；如确认覆盖请加 --force", file=sys.stderr)
        return 2
    shutil.copy2(source, target)
    manifest = OUTPUTS / "import-manifest.json"
    records = json.loads(read(manifest)) if manifest.exists() else []
    records.append({"source": str(source), "stored_as": str(target.relative_to(ROOT)), "sha256_prefix": digest(target), "imported_at": now()})
    write(manifest, json.dumps(records, ensure_ascii=False, indent=2) + "\n")
    print(f"已导入：{target.relative_to(ROOT)}")
    print(f"来源指纹：{digest(target)}")
    return 0


def source_block(path: Path) -> str:
    return f"- {path.relative_to(ROOT)}（来源指纹：{digest(path) if path.exists() else '待生成'}）"


def cmd_capability(args: argparse.Namespace) -> int:
    title = args.title or "未命名能力"
    sources = [Path(s).expanduser().resolve() for s in args.source]
    missing = [str(p) for p in sources if not p.exists()]
    if missing:
        print("错误：以下来源不存在：" + ", ".join(missing), file=sys.stderr)
        return 2
    out = OUTPUTS / f"capability-{slug(title)}.md"
    text = f"""# 能力卡：{title}\n\n状态：待人工确认\n生成时间：{now()}\n\n## 能力名称\n{title}\n\n## 能力来源\n{chr(10).join(source_block(p) for p in sources) or '- 待补充'}\n\n## 服务对象\n- 待确认：\n\n## 客户问题\n- 待确认：\n\n## 典型场景\n- 待确认：\n\n## 输入资料\n- 待确认：\n\n## 实际动作\n- 待确认：\n\n## 关键判断点\n- 待确认：\n\n## 交付物\n- 待确认：\n\n## 结果证据\n- 事实：\n- 缺少证据：\n\n## 当前可复现程度\n- 待确认：\n\n## AI可辅助部分\n- 整理、比较、初稿、检查遗漏（待实际验证）\n\n## 必须人工负责部分\n- 事实核验、业务取舍、客户沟通、最终承诺与验收\n\n## 证据边界\n- 事实：来源文件中明确记载的内容。\n- 假设：尚未由客户交付或结果验证的内容。\n- 本卡生成内容不得直接视为商业成功证据。\n\n## 人工确认记录\n- [ ] 已核对来源\n- [ ] 已区分事实与假设\n- [ ] 已补充可验收结果\n"""
    write(out, text)
    print(f"已生成待确认能力卡：{out.relative_to(ROOT)}")
    return 0


def cmd_card(args: argparse.Namespace) -> int:
    kind = args.kind
    title = args.title
    templates = {
        "canvas": f"""# 商业画布：{title}\n\n状态：草案\n生成时间：{now()}\n\n| 要素 | 内容 | 证据或待验证问题 |\n|---|---|---|\n| 客户细分 | 待确认 | 谁使用、谁付款、谁决策？ |\n| 价值主张 | 待确认 | 解决什么任务，改善什么结果？ |\n| 渠道 | 待确认 | 如何接触和交付？ |\n| 客户关系 | 待确认 | 如何建立信任和支持？ |\n| 收入来源 | 待确认 | 为什么付款、如何计费？ |\n| 关键资源 | 待确认 | 能力、时间、资料、工具？ |\n| 关键活动 | 待确认 | 研究、销售、交付、复盘？ |\n| 关键合作 | 待确认 | 有哪些依赖？ |\n| 成本结构 | 待确认 | 工时、工具、获客、交付？ |\n\n## 验证附页\n- 当前做法与替代方案：\n- 问题频率、损失与客户原话：\n- AI改善步骤及不用AI的对照：\n- 交付边界与验收：\n- 最关键未验证假设：\n- 最小实验与观察期限：\n- 支持证据 / 反证：\n- 继续、调整、停止条件：\n""",
        "hypothesis": f"""# 商业假设卡：{title}\n\n状态：待验证\n生成时间：{now()}\n\n## 假设\n如果【客户】在【场景】中使用【交付】，就会改善【结果】，并愿意采取【行为】。\n\n## 当前依据\n- 事实：\n- 推断：\n- 尚无证据：\n\n## 最小实验\n- 输入：\n- 交付：\n- 期限：\n- 成功标准：\n- 成本上限：\n\n## 结果记录\n- 客户是否采用：\n- 是否执行：\n- 可观察结果：\n- 是否愿意继续/付费：\n\n## 决策\n- [ ] 继续\n- [ ] 调整\n- [ ] 暂停/停止\n""",
    }
    if kind not in templates:
        print("错误：kind 只能是 canvas 或 hypothesis", file=sys.stderr)
        return 2
    out = OUTPUTS / f"{kind}-{slug(title)}.md"
    write(out, templates[kind])
    print(f"已生成：{out.relative_to(ROOT)}")
    return 0


def cmd_validate(_: argparse.Namespace) -> int:
    errors = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8-sig"))
            except Exception as exc:
                errors.append(f"{path.relative_to(ROOT)}: {exc}")
    if errors:
        print("校验失败：\n" + "\n".join(errors), file=sys.stderr)
        return 1
    print("项目记录校验通过。")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="AI商业顾问个人验证工作台")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="读取工作台状态").set_defaults(func=cmd_status)
    imp = sub.add_parser("import", help="导入一份资料并记录来源")
    imp.add_argument("source"); imp.add_argument("--force", action="store_true"); imp.set_defaults(func=cmd_import)
    cap = sub.add_parser("capability", help="生成待人工确认的能力卡")
    cap.add_argument("--title", required=True); cap.add_argument("--source", action="append", default=[]); cap.set_defaults(func=cmd_capability)
    card = sub.add_parser("card", help="生成画布或假设卡")
    card.add_argument("kind", choices=["canvas", "hypothesis"]); card.add_argument("--title", required=True); card.set_defaults(func=cmd_card)
    sub.add_parser("validate", help="校验项目 JSON 记录").set_defaults(func=cmd_validate)
    run = sub.add_parser("run-case", help="真实部分输入的N0—N11证据检查与交接，不等于业务验收")
    run.add_argument("case")
    run.add_argument("--output", default=str(ROOT / "private" / "workbench" / "latest-case"))
    run.add_argument("--force", action="store_true")
    from consultant_case import cmd_run_case
    run.set_defaults(func=cmd_run_case)
    live = sub.add_parser("live-metrics", help="按明确口径离线计算直播指标，不自动映射平台字段")
    live.add_argument("source")
    live.add_argument("--output")
    from business_metrics import cmd_live_metrics
    live.set_defaults(func=cmd_live_metrics)
    return p


if __name__ == "__main__":
    parsed = parser().parse_args()
    raise SystemExit(parsed.func(parsed))
