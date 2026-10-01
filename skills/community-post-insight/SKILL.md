---
name: community-post-insight
description: 社区热帖洞察分析。把 Reddit 等开发者社区的帖子按痛点吐槽/功能求助/竞品流失/自推晒作四类判定，按点赞+2×评论数并做 24/72 小时新鲜度加权的热度分分档，核算 9:1 自推参与额度，输出可参与目标帖清单与选题候选（同主题 ≥3 帖才入选）。带 Python 脚本可产出 Excel 洞察清单与类别分布图。当用户需要 Reddit 选帖、社区痛点挖掘、选题挖掘、参与额度核算时使用。
---

# 社区热帖洞察

把开发者社区的热帖变成两类可执行产出：**值得参与的目标帖清单**（附参与方式与 9:1
额度核算）和**值得写成内容的痛点选题候选**（附证据链）。只做筛选与决策建议：
不写正文、不发帖。

## 元信息

| 字段 | 值 |
|------|-----|
| ID | `de_dev_01_sk01` |
| 类型 | **`atomic`（原子技能）** |
| 所属员工 | 出海增长官 |
| 能力族 | 信息采集型 · 社区洞察 |
| 复杂度 | `M` |
| 阶段 | `P0` |
| 复用度 | 高（选题挖掘、竞品监控场景通用） |
| 资产形态 | 深度提示词 + Python 脚本（无模型调用、无 API Key） |

## 能力描述

1. **四类判定**（规则树短路）：自推晒作 → 痛点吐槽 → 功能求助 → 竞品流失 → 闲聊噪音
2. **热度分级**：热度分 = 点赞 + 2×评论数，≤24h ×1.2 / ≤72h ×1.0 / 更早 ×0.8；
   ≥200 🔥 热 / 50–200 🌤 温 / <50 ❄ 冷；评论点赞比 >0.3 标「讨论型」
3. **9:1 参与额度核算**：按 Reddit 板规给出今日可自推 / 需先参与多少条非自推的结论
4. **痛点主题聚类**：定价/上手门槛/集成导出/性能/隐私安全/移动端/协作七主题归堆，
   同主题 7 天窗口 ≥3 帖才列为选题候选（单帖不成选题）

## 输入规格

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `source` | string | ✅ | 数据来源（subreddit 名单 / 关键词，用于标注） |
| `window_days` | number | ⬜ | 时间窗口，默认 7 天 |
| `posts` | array | ✅ | 帖子列表，每条含 `id/subreddit/title/ups/num_comments/age_hours/url`；数据来自 Reddit 官方 API 或人工粘贴 |

## 输出规格

- `summary`：帖子总数 / 四类计数 / 可参与目标帖数 / 自推额度结论 / 高频痛点主题
- `items`：逐帖明细（类别 / 热度分 / 热度档 / 痛点主题 / 参与建议）
- 产物文件：`out/热帖洞察清单.xlsx`、`out/帖子类别分布.png`、`out/insight.json`

## 使用步骤

### 方式一：纯提示词（最快）

1. 打开你的 AI 工具，把 `prompt.txt` 全部内容粘贴为系统提示词
2. 粘贴帖子数据（标题 + 点赞 + 评论数 + 帖龄）
3. 得到四类分类、热度分档与 9:1 参与决策清单

### 方式二：带脚本（词表精确分类 + 产出 Excel/PNG）

```bash
python3 <SKILL_DIR>/scripts/insight_scan.py --input input.json --outdir out
python3 <SKILL_DIR>/scripts/insight_scan.py --demo     # 无输入也能看效果
```

**分工**：脚本做词表分类与热度计算（不漏不猜）；模型做语境复核（反讽、黑话）与
跟帖话术建议。两者结果交叉核对后，由人工决定是否参与。

## 边界（不做的事）

- ❌ 不编造帖子或热度数据；来源拿不到就列缺失清单让用户补
- ❌ 不建议刷 upvote、买假用户、小号互推、伪装用户口吻（须披露开发者身份）
- ❌ 不写爬虫绕过平台风控，只用官方 API / 人工粘贴数据
- ❌ 不生成对外发言正文，发帖动作保留人工确认
- ❌ 数值以脚本输出为准，不要自己算

## 调用示例

**输入**（`examples/input.json`，节选）：

```json
{
  "source": "r/SaaS + r/SideProject + r/indiehackers",
  "window_days": 7,
  "posts": [
    {"id": "P001", "subreddit": "r/SaaS", "title": "Struggling with churn - users sign up, never come back after day 3. What am I doing wrong?", "ups": 187, "num_comments": 96, "age_hours": 20, "url": "reddit.com/r/SaaS/comments/aa1"},
    {"id": "P004", "subreddit": "r/indiehackers", "title": "Is there a tool that turns Stripe invoices into a simple monthly P&L? Would pay for this", "ups": 154, "num_comments": 52, "age_hours": 46, "url": "reddit.com/r/indiehackers/comments/aa4"}
  ]
}
```

**输出**（脚本实跑，12 帖）：痛点吐槽 4 / 功能求助 2 / 竞品流失 2 / 自推晒作 2 /
闲聊噪音 2；P001 热度分 454.8 判 🔥 热·讨论型；可参与 6 帖。详见 `examples/output.md`。

## 所属工作流

- `daily-topic-mine-flow`（每日选题挖掘）

## 合规声明

- 本技能输出为 **AI 辅助分析结果**，发帖/评论前必须经人工复核 sub 当前版规
- 所有对外发言须披露开发者身份，按平台要求标注 AI 生成内容
- 不刷 upvote、不买假用户、不伪装用户口吻——违规即社区永久拉黑
- 帖子数据仅限本账号运营分析使用，不对外转售

---

*本技能遵循 [bangwozuo 数字员工资产规范](https://github.com/bangwozuo/digital-employee-spec) v3.0*
