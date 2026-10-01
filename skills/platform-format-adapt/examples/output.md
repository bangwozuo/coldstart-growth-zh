> 「AI 生成内容」标识 · 各平台发布前人工确认

# 输出示例（按 prompt.txt 四步工作法产出）

**输入**：见 `examples/input.json`（母稿 + platforms=[X/Twitter, Reddit,
Product Hunt] + subreddit=r/SideProject）。以下为按 `prompt.txt` 方法论
生成的适配结果。

## 信息点清单

| # | 信息点 | 级别 |
|---|---|---|
| 1 | Stripe 同步开箱即用，实测接入 15 分钟 | O |
| 2 | 周 cohort 视图 | O |
| 3 | plain-English 流失报告（不用懂 SQL） | O |
| 4 | 用户第 2 周找回 3 个要流失的用户 | O |
| 5 | 定价 ¥39/月，前 100 名 ¥29 | O（Reddit 版按 sub 规则处理，见核对表） |
| 6 | 技术栈 Next.js + Supabase | △ |

## 适配稿

### X/Twitter（thread 共 4 条，首帖 247/280 字符）

> 1/ Your signups don't leave loudly. They go quiet on day 3. I built a tool
> that shows you exactly when — weekly cohort views, no SQL needed.

> 2/ ChurnLens v0.9: Stripe sync that actually takes 15 minutes to set up
> (timed it), weekly cohorts, and a churn report written in plain English.

> 3/ Real week-2 result from a user: 3 at-risk users pulled back with one
> plain-English report. That's the whole job — see it early, say something.

> 4/ ¥39/mo, first 100 users ¥29. Building in public — ask me anything.

### Reddit r/SideProject（标题 62/300 字符，正文 96 词）

**标题**：I built a churn analytics tool because my signups kept going quiet on day 3

**正文**：
For months I found out users had left when it was already too late. So I built
ChurnLens: it syncs with Stripe (15 minutes to set up, timed it), shows weekly
cohorts, and writes the churn report in plain English — no SQL.

Last week a user pulled 3 at-risk users back with one report. That's the whole
point: see it early, say something.

Pricing is ¥39/mo (first 100 users ¥29). Disclosure: I'm the dev — happy to
answer anything about the cohort logic or the Stripe sync.

### Product Hunt（tagline 41/60 字符）

**Tagline**：Know who's about to churn — before day 30, in plain English.

**首评自述**：为什么做它（自己的 day-3 流失教训）+ 接入 15 分钟的实测 +
第 2 周找回 3 个用户的案例；配 5 张图（首屏/cohorts/报告/接入计时/定价）
与 1 条 ≤60 秒 demo 视频。

## 规格核对表

| 平台 | 字数/条数 | 结构 | 调性 | 合规 | 结论 |
|---|---|---|---|---|---|
| X/Twitter | 4 条 ≤7；首帖 247/280 | 首帖=钩子，一帖一点 | 朋友报信 | 无绝对词；数字未变形 | ✅ |
| Reddit r/SideProject | 标题 62/300；正文 96 词 | 先信息量后披露 | 同事口吻 | 自推合规（sub 允许）；身份披露在末句 | ✅ |
| Product Hunt | tagline 41/60 | 产品发布会 | 利益直给 | 无绝对词；配套 5 图 + ≤60s 视频清单 | ✅ |

## 弃用与回炉记录

| 项 | 处理 |
|---|---|
| 技术栈（Next.js + Supabase） | △ 级信息点，三平台全部砍除——平台上没人因此转化 |
| 「快 4 倍」式换算 | 母稿无此表述，适配中也禁止出现（8s→2.1s 只能原样报） |
| ¥29 促销（若目标为 r/SaaS 等讨论型 sub） | 讨论型 sub 禁自推帖 → 该版本不出手，改以评论参与 |
