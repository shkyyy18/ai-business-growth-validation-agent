# 工作台命令说明

这是 AI 商业顾问的第一个可运行切片：单用户、文件优先、人工确认。

## 快速开始

在项目根目录运行：

```powershell
python tools/ai_business_consultant.py status
python tools/ai_business_consultant.py validate
```

## 常用命令

```powershell
# 导入一份资料，复制到 workspace/imports 并记录来源指纹
python tools/ai_business_consultant.py import "D:\资料\我的课程.md"

# 基于资料生成能力卡（只生成草稿，不自动认定事实）
python tools/ai_business_consultant.py capability --title "个人IP课程设计与交付" --source "workspace/imports/我的课程.md"

# 生成商业画布或商业假设卡
python tools/ai_business_consultant.py card canvas --title "课程型专业人士的内容价值诊断"
python tools/ai_business_consultant.py card hypothesis --title "7天内容研究与生产交付"
```

所有输出在 `workspace/outputs/`，生成后必须人工核对并补充事实、客户原话、结果和证据。当前命令不会调用模型、不会访问互联网，也不会自动发送任何内容。


## 真实部分输入的端到端检查（2026-09-14新增）

```powershell
python tools/ai_business_consultant.py run-case experiments/business-advisor-e2e-001/case.json
```

默认写入被git忽略的 `private/workbench/latest-case/`。重复运行默认拒绝覆盖；核对后可加 `--force`。公开演示输入只有同作者两条公开作品的必要元数据，不包含原文稿和客户信息。项目内显式 `--output` 可指定检查输出目录；客户输出仍应放private。

生成账号卡、作品卡、输入指纹核验、N0—N11交接及M1—M5缺口。**这是离线来源完整性/交接检查，不是自动完成顾问推理、行业充分研究或客户商业验证。** case.json中的业务摘要由顾问写入并标明来源，代码不会独立判定原话真实或授权有效。

源文件变化时命令会拒绝沿用旧指纹。应先核对变化及其对原结论的影响，再更新案例引用；不要盲目刷新hash绕过检查。新客户案例不能直接把本文的public研究对象改成客户。

## 直播指标计算

```powershell
python tools/ai_business_consultant.py live-metrics private/live-input.json --output private/live-metrics.json
```

输入需明确 `source_ref`、`currency`、带时区的 `window_start/window_end`、`definitions_confirmed=true` 和 `values`。支持字段/公式见 `tools/business_metrics.py`；不能直接把不同平台导出的“ROI”“进入率”名称猜配成这些字段。

- 区分PV事件/UV用户、平均进入速度/实时流入曲线、GMV ROAS/利润ROI。
- 缺失分子/分母和分母0输出null；真实零分子才输出0。
- 不反推不可见成交、利润、留存或行业基准；不提供自动上播/投放决策。
- 当前只有明确标注为合成的算术单元测试，**没有真实直播数据验收**。

## 回归测试（不联网）

```powershell
python -m unittest discover -s tests -v
python -m unittest discover -s experiments/m1-field-mapping-001 -p test_mapping.py -v
```

`experiments/m1-real-account-001/inspect_public.py` 是有限公开页面诊断，执行会联网，不属于自动测试，也不是稳定采集器。没有安装/运行第三方抓取器。

项目文本来源指纹采用 `sha256-utf8-sig-lf-v1`（去UTF-8 BOM、CRLF规范到LF后计算），避免Windows/Linux检出差异。网络原始响应的source_sha256仍是原始字节指纹，两者不混用。
