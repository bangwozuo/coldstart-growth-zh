> 「AI 生成内容」标识 · 社区使用须披露开发者身份

# 输出示例（按 prompt.txt 配对规则与五种角度产出）

**输入**：见 `examples/input.json`（产品简述 + 3 条社区痛点原话 +
platform=Reddit 评论）。以下为按 `prompt.txt` 方法论生成的配对表、
钩子候选与自检结果。

## 痛点-卖点配对

| # | 痛点（原话/场景） | 对应功能 | 配对判定 |
|---|---|---|---|
| 1 | 「users sign up, never come back after day 3」 | 周 cohort 视图 + plain-English 流失报告 | ✅ 配对：产品就是做流失分析的 |
| 2 | 「turns Stripe invoices into a simple monthly P&L? Would pay」 | 无 | ❌ 错配弃用：产品不做 P&L，硬凑=零转化烧信任 |
| 3 | 「Spent 5 hours debugging webhooks」 | Stripe 同步开箱即用（实测接入 15 分钟） | ✅ 配对：免 webhook 配置正是差异化 |

## 钩子候选（按角度分组，≤90 字符）

| 角度 | 钩子 | 具体细节 | 适用场景 |
|---|---|---|---|
| 痛点瞬间 | Day 3, your signups quietly disappear. A weekly cohort view shows exactly when. | Day 3（痛点原话数字） | 回复 churn 痛点帖 |
| 前后对比 | Spent 5 hours on a webhook? Stripe sync here took 15 minutes, no webhook config. | 5 小时 vs 15 分钟（双方原话/实测数字） | 回复 webhook 痛点帖 |
| 身份共鸣 | Every solo founder has users they never realized they were losing. | — | X thread、devlog 开头 |
| 反共识 | Your churn problem isn't pricing. It's that you find out on day 30, not day 3. | day 30 vs day 3 | 有独特机制支撑时用 |
| 成本账 | 3 users pulled back from churn risk in week 2 — one plain-English report. | 3 个 / 第 2 周（用户实测反馈） | 落地页副标题 |

## 自检结果

| # | 钩子 | 长度 ≤90 | 具体度 | 兑现度 | 合规 |
|---|---|---|---|---|---|
| 1 | Day 3, your signups… | ✅ 84 | ✅ Day 3 | ✅ cohort 视图可兑现 | ✅ |
| 2 | Spent 5 hours on a webhook?… | ✅ 86 | ✅ 5h/15min | ✅ 实测接入 15 分钟 | ✅ |
| 3 | Every solo founder… | ✅ 71 | ⚠ 无数字，靠身份词兜底 | ✅ | ✅ |
| 4 | Your churn problem isn't pricing… | ✅ 88 | ✅ day 30/3 | ✅ 流失报告机制支撑 | ✅ |
| 5 | 3 users pulled back… | ✅ 79 | ✅ 3 个/第 2 周 | ✅ 来自用户反馈原句 | ✅ |

## 弃用钩子与原因

| 钩子 | 原因 |
|---|---|
| 「Turn Stripe chaos into a clean P&L in one click」 | 对应痛点 #2 错配：产品无 P&L 功能，承诺不可兑现 |
| 「Reduce churn by 50% with one dashboard」 | 「50%」无实测依据（输入数据只有找回 3 个用户的案例），降级为不带数字写法 |
| 「The best churn analytics tool for indie hackers」 | 绝对化用语「best」，合规伤 |

> 使用前人工确认：钩子承诺与产品当前版本一致；回复社区帖时披露开发者身份。
