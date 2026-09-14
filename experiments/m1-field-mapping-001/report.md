# M1-FIELD-MAPPING-001：离线字段映射实测

日期：2026-09-14。目标：采集原始响应能否转换为本项目的账号/作品证据卡。结果：本次限定夹具及自编测试通过，真实采集能力仍未验证。

## 输入与操作

读取Evil0ctal/Douyin_TikTok_Download_API固定提交a40370473991321dd4771ee3eb25789db8340cce中的4份合成测试夹具：正常作品页、验证码业务错误、私密作品、删除作品。正常页明示 Synthetic Creator / Not a real person，且CDN地址使用.invalid域。它们不是真实客户或行业素材，禁止计入行业库。

通过普通HTTP从GitHub下载测试文件，保留来源、读取时间、SHA256及上游Apache-2.0许可证。映射/测试脚本均为本项目新写的Python标准库脚本，未运行第三方代码。没有访问抖音、安装依赖、下载视频、登录、充值或调用付费API。来源见fixtures/provenance.json。

## 实际产物

- map_fixture.py：仅适配该固定夹具格式的离线实验，不是生产适配器，也不是多源统一SDK。
- mapped-fixture.json：1个测试账号、2条测试作品（包含视频及图文原类型字段）。真实行业样本0、有效内容阅读0、深拆0。
- test_mapping.py / test-result.json：14个unittest测试方法全部通过；包含多个子场景，不另放大成检查数量。不宣称覆盖所有输入格式、所有接口或全部异常。

## 字段映射

| 输入字段 | 卡片字段 | 约束 |
|---|---|---|
| author.sec_uid / uid | account_id / uid_raw | 用稳定ID归并，不用昵称作为主键；未知ID拒收 |
| aweme_id / author.sec_uid | work_id / account_id | 与预期主页作者核对，推荐作品作者不符则排除 |
| statistics.aweme_id | 指标归属核对 | 与作品ID不符整条排除，不把别作数据拼入 |
| follower_count / total_favorited | followers_raw / account_total_likes_raw | 账号量与单条作品指标分开 |
| digg/comment/collect/share_count | likes/comments/saves/shares | 保留原字段和原值；负数、布尔值、单位字符串不擅自转换 |
| statistics.play_count | plays.raw_value | 夹具给0，但定义与投流口径未知，不作分母或推断没人看 |
| desc | description | 不当逐字稿，不计原视频阅读 |
| share_url | original_url_raw | 仅保留原值，不访问或标记已核验；测试ID链接不能当真实素材 |
| create_time | published_epoch_raw | 保留原时间戳；夹具下载时间不是平台指标采集时间 |
| max_cursor / has_more / total | pagination原值 | 不推导全账号覆盖率，更不推导行业研究已饱和 |
| status_code / status | issues或排除 | 验证码业务错误、私密、删除、受限或未知可见性不进入可分析作品 |

转写、视频观看、爆款标签、变现、账号常态基线全部保持未知/未完成，不能为了填满卡片生成内容结论。

## 本次测试覆盖

归属与指标对应；零播放量不参与分母；缺字段不置零；非法数值不强转；描述不计阅读；作者错配；统计ID错配；完全重复去重；冲突重复隔离；游标停滞不认定完成；验证码/私密/删除排除；错误结构拒收；更名仍同账号；缺作品ID拒收。

限制：只检查当前页重复和当前请求游标，没有实现跨批次数据库去重、连续分页、崩溃恢复、真实账单、转写准确度或批量性能。14项通过只证明这些离线行为按预期执行，不证明采集器可用或行业判断正确。

## 对上一轮调查的重要纠正

上轮报告把源码里存在搜索URL常量概括成了搜索采集能力，这是过度推断。endpoints.py开头明确说明仅ENDPOINTS中的项已接入；该提交的抖音表注册了账号资料、作品列表、详情、评论等，但没有注册搜索。它可以保留为已知账号读取候选，不能当作行业关键词发现已就绪。仅限此提交和检查范围，不推断项目其他版本或所有模块均无搜索。

来源：https://raw.githubusercontent.com/Evil0ctal/Douyin_TikTok_Download_API/a40370473991321dd4771ee3eb25789db8340cce/src/dtk/platforms/douyin/endpoints.py

## 下一步

离线字段小测已经完成，不再扩写字段模板或继续堆测试数量。下一里程碑是一个真实行业账号的输入链路：连续作品、可核对原内容和带标签指标，仍不用于证明行业样本充分。

尚未安装采集器，也没有已确认的客户授权资料或正式API凭据。实际安装/登录/付费需先明确操作范围；不自动开启身份池、读取浏览器Cookie或绕过验证码。TikHub继续只是可选输入来源，前述演示费用矛盾未消除。优先使用可公开读取或用户已授权导出的真实材料，无法读取就报告具体缺口，不把测试夹具替代成真实内容。
