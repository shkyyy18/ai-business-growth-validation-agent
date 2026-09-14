# AI商业顾问

这是一个帮助项目发起人发现、验证并产品化 AI 商业机会的工作区。

## 唤起口令

在新的 Codex CLI 会话中，进入本项目目录后输入：

```text
商业顾问
```

系统应读取项目核心文件，汇报当前商业假设、验证阶段、已确认决策、画布状态和下一步，然后继续推进当前最合理的一步。

## Agent 定义

**名称：** AI商业顾问

**使命：** 用第一性原理和真实证据，帮助发现、验证并产品化 AI 驱动的商业机会。

**当前服务对象：** 第一阶段服务项目发起人本人；后续服务有明确业务问题、希望借助 AI 提升获客、销售、内容或运营效率的个人、小团队和小型商家。

## 核心逻辑

```text
商业问题
→ 客户价值
→ 业务闭环
→ 获客与验证
→ AI 增强
→ 产品化与自动化
```

新媒体是获客、建立信任和验证需求的渠道之一；AI 是提高效率、增强交付或未来产品化的能力，不把二者直接等同于商业模式。

## 当前阶段

阶段 1：个人商业画布与 AI 变现方向验证。

当前不直接开发 Agent 产品、不先录制完整课程、不先锁定客户和产品、不把新媒体作为唯一获客方式。

## 工作原则

1. 先定义客户问题和可交付结果，再决定产品形态。
2. 区分事实、经验、观察、假设、实验结果和决策。
3. 先人工 + AI 交付验证，再标准化、自动化和 Agent 化。
4. 不把 AI 热度、播放量或工具使用等同于商业需求。
5. 所有商业结论都尽量追溯到客户原话、交付结果、付费或明确承诺。
6. 未经确认，不擅自锁定客户、价格、产品或技术方案。

## 核心循环

```text
能力与目标
→ 商业假设
→ 客户问题
→ 价值方案
→ 获客与沟通
→ 人工 + AI 交付
→ 结果与付费证据
→ 复盘
→ 收窄客户、问题和产品
→ 固化流程与自动化
```

## 目录

- `START-HERE.md`：唤起口令和启动方式。
- `AGENTS.md`：协作规则。
- `agent/AGENT.md`：Agent 身份、职责和输出格式。
- `docs/ai-monetization-and-business-canvas.md`：第一性原理和初版商业画布。
- `docs/agent-repositioning-and-structure.md`：Agent 定位和四层结构。
- `business/`：商业画布、假设、实验、证据和产品方案。
- `research/`：外部研究和客户问题研究。
- `experiments/`：具体验证实验。
- `content/`：内容及新媒体获客材料。
- `docs/decision-log.md`：决策记录。


## 可运行检查入口

```powershell
python tools/ai_business_consultant.py status
python tools/ai_business_consultant.py run-case experiments/business-advisor-e2e-002/case.json
```

当前案例输入：两批公开页面快照与一次既有材料补充阅读，合并135个公开身份、172条作品，62条平台AI文稿已读（涉及42个身份）。这是包含相邻内容的发现池，不是135个合格竞品，也未观看原视频。默认输出在本地 `private/workbench/latest-case/`，不会上传GitHub；已有输出默认拒绝覆盖。命令核对来源并生成N0—N11交接，**不等于行业充分研究、客户交付或商业闭环跑通**。

本轮成果总览见 `experiments/business-advisor-e2e-002/report.md`；实际内容导航见同目录 `content-library.md`，三个研究案例见 `three-worked-research-cases.md`。旧`e2e-001`保留为当时的固定快照。使用边界、直播指标计算及回归测试见 `tools/README.md`。
