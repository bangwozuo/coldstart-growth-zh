> 「AI 生成内容」标识

# 输出示例（脚本实跑）

> 由 `scripts/insight_scan.py` 处理 `examples/input.json` 真实产出，非手写。

## 洞察结论（out/insight.json 摘要）

| 项 | 内容 |
|---|---|
| 数据来源 | r/SaaS + r/SideProject + r/indiehackers |
| 时间窗口 | 近 7 天 |
| 帖子总数 | 12 |
| 痛点吐槽 / 功能求助 | 4 / 2 |
| 竞品流失 / 自推晒作 / 闲聊噪音 | 2 / 2 / 2 |
| 可参与目标帖 | 6 |
| 今日自推额度 | 今日如有 1 条自推需求，需先完成 ≥9 条非自推参与（9:1 规则） |
| 高频痛点主题 | 上手门槛、定价、性能、移动端、隐私安全、集成导出 |

## 洞察明细（按参与优先级排序，全部 12 帖）

| # | 类别 | 帖子（标题截断） | 热度分 | 热度档 | 痛点主题 | 参与建议 |
|---|---|---|---|---|---|---|
| 1 | 痛点吐槽 | Struggling with churn - users sign up, never come back after day 3… | 454.8 | 🔥 热 · 讨论型 | — | 以「同行+同样遇到」口吻参与，本条不贴链接 |
| 2 | 功能求助 | Pricing my first SaaS at $9/mo feels wrong - how do you decide pricing? | 463.2 | 🔥 热 · 讨论型 | 定价 | 给真实定价思路（成本/价值/竞品三法），不贴链接 |
| 3 | 功能求助 | Is there a tool that turns Stripe invoices into a simple monthly P&L? Would pay… | 258.0 | 🔥 热 · 讨论型 | — | 先给真实方案；若提及产品必须披露开发者身份 |
| 4 | 痛点吐槽 | Why is GDPR compliance so painful for a one-person EU startup? | 247.0 | 🔥 热 · 讨论型 | 隐私安全 | 分享真实合规清单，不贴链接 |
| 5 | 痛点吐槽 | Anyone else hate configuring webhooks? Spent 5 hours debugging one today | 172.0 | 🌤 温 · 讨论型 | — | 同行口吻参与，计入非自推配额 |
| 6 | 竞品流失 | Just cancelled my Calendly subscription, moved away from seat-based pricing tools | 129.0 | 🌤 温 · 讨论型 | 定价 | 记录流失原因进竞品档案，不参与不攻击 |
| 7 | 竞品流失 | Switched from Intercom to a cheaper helpdesk - onboarding docs were the real cost | 120.0 | 🌤 温 · 讨论型 | 上手门槛 | 同上，只记录不参与 |
| 8 | 自推晒作 | I built a churn analytics tool and just launched on Product Hunt today | 76.8 | 🌤 温 | — | 仅 r/SideProject 等允许自推的 sub 可发；r/SaaS 跳过 |
| 9 | 自推晒作 | Just shipped v2 of my side project, roast my landing page | 73.2 | 🌤 温 · 讨论型 | — | 同上 |
| 10 | 痛点吐槽 | My app is slow on mobile, anyone dealt with this? Lag on every scroll | 64.0 | 🌤 温 · 讨论型 | 性能、移动端 | 可分享性能排查经验（非自推） |
| 11 | 闲聊噪音 | PSA: export your data before your tool shuts down (again) | 87.2 | 🌤 温 · 讨论型 | 集成导出 | 不参与 |
| 12 | 闲聊噪音 | What's your Sunday routine as a solo founder? (casual) | 16.0 | ❄ 冷 · 讨论型 | — | 不参与 |

## 参与决策（Excel「参与决策」sheet 摘要）

| 项 | 规则 |
|---|---|
| 9:1 参与比 | 近 10 条发帖/评论中自推 ≤1 条；未达标前只做非自推参与 |
| Sub 差异 | r/SideProject 允许自推；r/SaaS 须先参与讨论再提及产品；多数 sub 禁直接广告 |
| 删帖高频原因 | 无上下文裸贴链接 = 最高频删帖原因；链接必须挂在有价值回答之后 |
| 今日额度 | 如有 1 条自推需求，需先完成 ≥9 条非自推参与 |

## 词表迭代记录（开发期实况）

- P007「Pricing my first SaaS at $9/mo feels wrong」初版词表未命中被判「闲聊噪音」，
  但语境是典型定价讨论帖（热度分 463.2 全场最高）。按 prompt.txt「脚本分类 +
  模型语境复核」流程发现漏判后，向词表补充「how do you decide / drop off /
  too confusing / gave up」等表达并回归测试——现正确判为「功能求助」。
  这条链路本身就是三层设计（脚本 → 模型 → 人工）价值的实证。

---

*本结果由 AI 生成；发帖/评论前人工核对 sub 当前版规。*
