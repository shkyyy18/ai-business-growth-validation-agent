# M1 数据来源：接口口径、费用与权限核对

核对日期：2026-09-14。性质：公开文档调查与顾问方案，不是新API实测、法律意见或采购决定。本轮未登录、注册、安装、充值、发送密钥或新增数据API调用；此前一次固定美食演示请求仍是唯一演示API实测。

## 核心判断

TikHub保留为账号/作品发现的候选，不确认其能包办行业内容库与变现研究。建议分开验证：内容发现及互动数据、原视频与可靠转写、商品/课程/服务及成交证据。客户自己的经营数据另走授权导出或适用官方接口，不用竞品公开数据冒充客户后台。

## 已核对来源与发现

### D01：价格与免费额度
- https://tikhub.io/pricing
- https://tikhub.io/getting-started
- https://tikhub.io/douyin-api

供应商页面列出按次付费，多数接口起价0.001美元，专用Douyin Search系列公开列价0.01美元/次，不默认适用普通接口的批量折扣。入门页称新用户有0.05美元欢迎额度，但部分端点仅收付费余额；不能把“约50次免费请求”解释为50次抖音搜索。价格页称非200失败请求不收费；这仍是供应商说明，不等于实际账单验证。具体端点适用价格、免费余额资格、充值门槛、支付手续费、HTTP200但业务失败/空结果/重试的扣费及账户账单仍待确认。查询时应以具体端点和账户所示适用费用核对，不用起价乘全部工作量。

### D02：演示费用疑问没有解决
- https://docs.tikhub.io/337619230e0
- experiments/m1-data-access-001/network-probes.json

演示文档仍写固定美食、1小时缓存、免费使用；响应示例和此前实际返回都含计费提示。它可能是通用响应文案，但这只是待核实解释。不能靠推测消除费用疑问，本轮没有再次调用演示。

### D03：行业搜索与账号列表的文档参数
- https://docs.tikhub.io/370212780e0
- https://docs.tikhub.io/186826223e0

视频搜索为POST /api/v1/douyin/search/fetch_video_search_v2，关键词、综合/点赞/最新排序、时间筛选可配置。翻页不只看cursor，还须保留上次的search_id与backtrace（按实际响应核对）；business_data中有不同类型，不能把原始条目数当视频数。文档里的desc是视频描述，不是逐字口播稿。

账号作品GET /api/v1/douyin/app/v3/fetch_user_post_videos，以sec_user_id定位、max_cursor翻页，count不超过20，有最新/最热排序和normal/lite渠道。每页上限只是接口约束，不是单账号研究量。文档提醒不同渠道可能有最新作品可见差异；不因翻页两页或has_more结束就宣称全账号/全行业完整。

这些是供应商说明，正式接口仍未实测；不照搬文档示例中的undefined参数或示例账号当行业证据。

### D04：播放量存在不同口径
- https://docs.tikhub.io/186826221e0
- https://docs.tikhub.io/493289600e0

供应商统计接口fetch_video_statistics文档称多数接口不再返回播放量，aweme_ids最多2个；Xingtu V2 get_item_play_count文档标价0.002美元/次，说明watch_cnt包含广告加热、不可取得为null，并将App V3统计接口区分为未投流播放量。

这不是我们已验证的测量准确性。搜索文档即使列有play_count，也不能假定每个响应都有有效播放量。先记录来源端点、原字段、含投流与否、采集时间、缺失状态，再决定可比性；null不置零。不同口径不能直接放到同一账号基线。

### D05：不能认定具备抖音商城成交能力
- https://tikhub.io/douyin-api

本轮保存的FAQ片段明确说没有抖音shop/product端点，电商查询指向的是TikTok Shop。先前“同页营销表述冲突”的概括没有在有限证据摘录中完整保留两侧文字，不作为本轮独立结论；可确认的是该FAQ不能证明抖音成交支持。这里只得出“该供应商抖音成交能力未证实”，不推广为抖音平台不存在电商接口。TikTok Shop不替代抖音小店；星图合作报价/指数也不证明课程成交。

当前不把TikHub作为已验证的变现数据底座。需另核对课程/虚拟商品/服务的覆盖、估算方法、统计时间及导出权限，不只看日用品商品榜。

### D06：官方授权与榜单边界
- https://open.douyin.com/platform/resource/docs/ability/open-data/video-data-solution
- https://open.douyin.com/platform/resource/docs/openapi/video-management/douyin/search-video/video-data/
- https://open.douyin.com/platform/resource/docs/accession-guide/type-and-permission
- https://open.douyin.com/platform/resource/docs/openapi/data-open-service/star-data/star-tops/get-star-author-hot-list

抖音官方视频数据接入方案明确用户授权及权限开通；查询特定视频数据要求video.data与用户令牌。不能把这条路线当成任意竞品后台获取工具。

官方星图热榜说明：需要申请权限但不需要用户授权，且展示须带星图指数/星图达人榜标识。榜单是有其排序规则的市场样本，不覆盖所有老师/顾问/培训师；最后一句是本项目研究边界判断，非行业覆盖率测定。

### D07：商业数据工具的估算标识
- https://yt.feigua.cn/

飞瓜易投公开页列“预估销售额”。只确认该公开页面的字段标识，不声称飞瓜所有产品/字段都是估算。未登录验证导出、套餐、知识付费行业覆盖或API，不作采购推荐。其公开日用品样例不纳入本项目行业样本。

### D08：条款核查仍不完整
- https://user.tikhub.io/terms （本次网页读取无正文）
- https://docs.tikhub.io/5432445m0
- https://docs.tikhub.io/5432446m0

找到的Service Provider Agreement主要针对在市场发布商品/服务的商家，不能拿它代替API买方的完整服务条款；Business Restriction也是商家语境。API购买方适用条款、内容留存、衍生报告及对外交付权限仍待核对。不从开源插件许可或供应商宣传推导平台内容使用授权。

## 方案与下一步

- 试用只验内容检索链路，见 experiments/m1-data-access-001/authorized-pilot-plan.md；未获授权不执行。
- 不为获得公开竞品数据而要求客户提供抖音Cookie；自身经营数据优先由客户授权导出。
- 下一轮无凭据也能继续：核查商业数据来源能否覆盖知识付费课程/虚拟商品、成交统计口径和导出，不把购买API设成推进的唯一前提。没有发现可核验交易来源时，应明确变现缺口，而不是以互动数据代替。

## 本轮取证与限制补记

网页工具未返回可用引用标识，随后通过标准库HTTP读取上述公开文档并保留有限预览/片段，见 experiments/m1-data-access-001/due-diligence-page-probes.json 与 due-diligence-doc-tails.json。导航文字可能命中检索词，接口判断须核对正文而非导航。一次不带浏览器User-Agent的主页复查返回403，未通过该失败读取形成结论；没有绕过登录或调用数据API。以上保存片段不是完整条款存档。
