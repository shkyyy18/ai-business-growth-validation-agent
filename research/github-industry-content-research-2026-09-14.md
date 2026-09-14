# GitHub 行业内容研究组件与 Skill 借鉴调研

日期：2026-09-14
任务：寻找能够扩大真实账号/内容研究规模、支持动态采样与内容库建设的组件，而非寻找写稿提示词。
状态：文档、许可证及部分源码/目录只读审查；未安装、未接账号、未调用商业数据 API，未完成端到端验证。不能认定任一项目已经满足本项目的成熟度要求。

## 用户本轮确认

- 行业不同，账号样本数量与单账号阅读量应在调研后决定，不是预先固定门槛。
- 高赞、常态、低数据值得研究内容的纳入方法，用户没有现成建议；过去靠大量阅读积累判断。
- 深拆数量取决于实际发现多少值得拆的内容及行业情况。
- 人工筛选最多做到约100个账号、200条内容；是历史能力边界，不是最低配额、均分公式或 AI 上限。尚未细分总阅读、入库和深拆口径。
- 用户希望 AI 介入规模研究，并允许制作 Skill 或调查 GitHub 借鉴项目。

## 查询与证据层级

搜索方向：行业/竞品研究 Skill、抖音账号与作品发现、相对表现分析、批量采集与研究素材管理。没有做全 GitHub 穷尽调查。

读取仓库原始 README、关键 SKILL.md、许可证；通过 GitHub API核对主分支 SHA、归档状态与最后提交时间；另读取 TikHub/ScrapeCreators 目录树及 F2 抖音 crawler.py 的函数定义片段。未运行任何第三方仓库代码。

2026-09-14 API 快照（全部未归档；最后提交不等于发行日期，也不能单独证明维护质量）：

| 仓库 | 主分支 SHA | 最后提交 UTC | GitHub 许可证识别 |
|---|---|---|---|
| TikHub/tikhub-plugin | 755a540afa53dbc31993cb7567376db0ea0fca4f | 2026-06-16 | MIT |
| ScrapeCreators/social-media-research-skills | 64ba7b4dea71e130d2712ffb6c1c1024b3b7c4b2 | 2026-08-26 | MIT |
| NanmiCoder/MediaCrawler | d6f7c5bb906b6dac40ddf343ef9e26438a3de092 | 2026-08-14 | NOASSERTION；以实际 LICENSE 为准 |
| Johnserf-Seed/f2 | 7dab3e2ffffaa2535834d28fca99dbc2e89fa9d3 | 2025-10-12 | Apache-2.0 |

额外初筛 kenneth-liao/ai-launchpad-marketplace，仅核对仓库元数据，不作为本次研究方法或成熟度依据。

## 1. TikHub/tikhub-plugin：优先研究的数据接入与流程候选

原始文件：
- https://github.com/TikHub/tikhub-plugin
- https://raw.githubusercontent.com/TikHub/tikhub-plugin/755a540afa53dbc31993cb7567376db0ea0fca4f/skills/douyin/SKILL.md
- https://raw.githubusercontent.com/TikHub/tikhub-plugin/755a540afa53dbc31993cb7567376db0ea0fca4f/skills/competitor-analysis/SKILL.md

文档描述抖音用户/作品检索、资料与作品列表、分页获取，并将任务路由到竞品分析等 Skill；需要 TikHub API key，分页产生计费。这里确认的是文档入口存在，不是接口当前可用、字段完整或可获取完整市场。

值得借鉴：发现与分析分开、账号解析、保留可比窗口、批量调用前估算成本。

不能照搬：竞品 Skill以给定账号名单为起点，并让账号采用相同采样上限；这不等同于行业发现与动态深读。保留横向比较的可比性，但不把研究量锁死。

选择：优先做数据路线可用性核查，尚未选购或接入。目录树主要呈现 Skill 与索引/验证脚本，不能把提示词集合认定成已验证的行业研究引擎。

## 2. ScrapeCreators/social-media-research-skills：优先借鉴相对表现方法

来源：
- https://github.com/ScrapeCreators/social-media-research-skills
- https://raw.githubusercontent.com/ScrapeCreators/social-media-research-skills/64ba7b4dea71e130d2712ffb6c1c1024b3b7c4b2/skills/outlier-post-finder/SKILL.md

该 Skill将作品表现与账号自己的基线比较，保留来源，再补细节或转写；这是比全行业直接按最高播放排序更相关的方法参考。其列出的数据平台包含 TikTok 等，未列抖音，不据 TikTok 支持推导抖音支持。

不照搬：预设阅读数量、固定异常倍数，以及偏向仅补充高表现作品的筛选路径。本项目还需保留普通对照、低数据但有具体研究价值的内容及反例。原文件“为何奏效”的解释不能升级为因果证明。

选择：借鉴方法，重写为本项目规则；不复制整个插件或购买服务。是否能提供抖音原内容与所需字段未验证。

## 3. Johnserf-Seed/f2：素材与接口处理候选，不是行业研究成品

来源：
- https://github.com/Johnserf-Seed/f2
- https://raw.githubusercontent.com/Johnserf-Seed/f2/7dab3e2ffffaa2535834d28fca99dbc2e89fa9d3/f2/apps/douyin/crawler.py
- https://raw.githubusercontent.com/Johnserf-Seed/f2/7dab3e2ffffaa2535834d28fca99dbc2e89fa9d3/LICENSE

README定位多平台作品下载和接口数据处理，列有抖音资料及主页作品功能。关键限制：当前 README功能表将抖音视频/用户搜索列为未来实现；不能仅凭“支持抖音”认定可发现行业账号。

可作为已知账号素材获取路线的后续候选；不负责本项目的动态采样、研究价值判断和行业结论。未运行现网接口，实际访问、权限和维护成本仍未知。源码许可不代表平台数据或内容使用授权。

## 4. NanmiCoder/MediaCrawler：本次不选作商业数据底座

来源：
- https://github.com/NanmiCoder/MediaCrawler
- https://raw.githubusercontent.com/NanmiCoder/MediaCrawler/d6f7c5bb906b6dac40ddf343ef9e26438a3de092/LICENSE

LICENSE限定非商业学习用途，限制大规模爬取，并要求商业用途另得书面同意。本项目目标与这些限制存在直接选型冲突；不因仓库公开或热度高就选用、复制或运行。这里只记录许可文本和本项目选择，不作全面法律意见。

## 综合判断

本轮找到可借鉴的具体部件，没有验证一个可直接完成“行业发现→大规模真实阅读→动态判断→内容库→深拆”的成熟成品。建议组合方向，而非确认技术栈：

- 可访问且获授权的数据来源（待验证）承担发现、列表和原内容；
- 项目自编 industry-content-research Skill承担研究计划、动态扩展、对照、证据边界与交付；
- 有来源的内容库与用户对真实样本的反馈承担方法校准。

AI扩大覆盖、降低人工筛选负担是待测价值，不因写成 Skill 就实现。无限数据访问、全行业穷尽、准确“网感”与超越人工的效果均未证实。

## 已落地与下一步

新增项目内草案（未全局安装）：
- skills/industry-content-research/SKILL.md
- skills/industry-content-research/references/adaptive-research.md
- skills/industry-content-research/references/evidence-and-delivery.md

没有照搬第三方完整技能或执行其安装命令。草案的动态采样和暂收口规则是顾问方案，未作为用户既有方法。

下一步优先核实真实数据可得性：用户/作品搜索、账号列表分页、原内容/转写、字段口径、窗口深度、重复与失败、授权与调用成本。可先用公开可读资料或已有授权导出；如需商业 API或账号访问，再明确操作与预算并取得授权，不要求用户把密钥写入聊天。

首次数据链路小测只验收来源与字段是否可用，不等于行业样本充分或研究完成。拿到可持续数据路线后，沿用个人 IP／知识付费案例展开动态行业扫描；由新发现、反例和覆盖缺口调整研究量。


### 草案检查结果

系统 quick_validate.py 因缺少PyYAML未完成；未安装依赖。标准库进行的有限前置结构、命名、UTF-8与本地引用检查通过。对现有三条线索做了桌面适用性检查，没有批量研究或数据接口实测。详见 experiments/m1-pilot-001/research-skill-check-v0.1.md。

## 后续实测补充（2026-09-14，覆盖此前“无接口实测”的现状描述）

已向TikHub公开固定“美食”演示端点发送一次无密钥请求，HTTP/JSON成功，返回19个原始列表条目；不是知识付费行业样本，未验证正式搜索、分页或内容字段。演示文档称免费而返回提示计费，停止进一步API调用待澄清。正式认证接口仍仅查文档。见 experiments/m1-data-access-001/report.md 及请求元数据。
