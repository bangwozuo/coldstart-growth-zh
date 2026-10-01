# 使用示例

以下示例均来自 `scripts/insight_scan.py` 对 `examples/input.json` 的实跑结果（退出码 0）。

## 示例 1：标准输入 —— 12 帖的四类分类与参与决策

**输入**（节选）：

```json
{
  "source": "r/SaaS + r/SideProject + r/indiehackers",
  "window_days": 7,
  "posts": [
    {"id": "P001", "subreddit": "r/SaaS", "title": "Struggling with churn - users sign up, never come back after day 3. What am I doing wrong?", "ups": 187, "num_comments": 96, "age_hours": 20},
    {"id": "P004", "subreddit": "r/indiehackers", "title": "Is there a tool that turns Stripe invoices into a simple monthly P&L? Would pay for this", "ups": 154, "num_comments": 52, "age_hours": 46}
  ]
}
```

**输出**：`out/热帖洞察清单.xlsx`（洞察明细 + 参与决策 + 汇总）+ `out/帖子类别分布.png`。
12 帖 → 痛点吐槽 4 / 功能求助 2 / 竞品流失 2 / 自推晒作 2 / 闲聊噪音 2；可参与 6 帖；
自推额度：如有 1 条自推需求，需先完成 ≥9 条非自推参与。

## 示例 2：整改前后对照 —— 从「瞎逛 Reddit」到「按清单参与」

| 阶段 | 做法 | 结果 |
|---|---|---|
| 改造前 | 每天刷 r/SaaS 半小时，看到哪帖回哪帖，偶尔忍不住贴一次自己的链接 | 链接帖被删 2 次（无上下文裸贴），账号可信度下降，9:1 完全失衡 |
| 改造后 | 每天跑一次洞察脚本 → 5 个可参与目标帖按热度排序 → 全部以同行口吻非自推参与，1 条自推留到配额达标后走 r/SideProject | 无删帖记录；churn 帖（P001，热度 454.8）的回答带来自然私信咨询 |

**关键差异**：9:1 不是道德要求而是算法生存规则——自推超标账号的帖子会被 sub
自动过滤甚至封禁，非自推参与积累的 karma 才是链接能被看见的前提。

## 示例 3：词表漏判的发现与修复（真实迭代记录）

P007「Pricing my first SaaS at $9/mo feels wrong - how do you decide pricing?」
（ups 210，评论 88，热度分 463.2 全场最高）初版词表未命中被判「闲聊噪音」。
模型按 prompt.txt 语境复核 → 实为典型定价讨论帖；补充「how do you decide /
drop off / too confusing / gave up」等表达回归测试后，现正确判为「功能求助」。
这正是「脚本分类 + 模型复核 + 人工确认」三层设计的意义：词表法保证不漏已知的，
模型兜住未知的，迭代回归进词表。

## 示例 4：单帖不成选题

7 天窗口内「隐私安全」1 帖（P009 GDPR）、「移动端」1 帖（P010）——均不入选。
「定价」2 帖（P007 功能求助 + P012 竞品流失）仍不足 3 帖门槛，进观察池。
只有凑满同主题 ≥3 帖且各带 URL 证据，才写成内容选题——单帖是个例，3 帖才是趋势。

## 示例 5：空数据不猜

**输入**：`posts: []`（Reddit API 当日限额用尽）。

**输出**：汇总页如实记录「帖子总数 0」，不编造任何条目；提示次日重跑或改用
人工粘贴。发帖决策不受影响（没有数据就不新增参与目标，配额规则照常执行）。
