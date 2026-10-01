---
name: hashtag-optimize
description: 话题标签优化。按平台硬上限（X≤3/小红书≤10/PH 用 topic）与三层配比法（大:中:小=3:5:4，按周发帖量分层）给内容配标签组合，适配分=70%单帖互动归一+30%竞争度衰减，零相关标签重罚排除防 tag stuffing。带 Python 脚本产出 Excel 组合清单与分数分布图。当用户需要配标签、hashtag 推荐、话题组合、标签分层时使用。
---

# 话题标签优化

为一篇内容在指定平台配一组**分层均衡、与内容强相关**的标签组合，每个标签注明
层级与承担角色（借曝光 / 做性价比 / 保精准）。

## 元信息

| 字段 | 值 |
|------|-----|
| ID | `de_dev_01_sk05` |
| 类型 | **`atomic`（原子技能）** |
| 所属员工 | 出海增长官 |
| 能力族 | 优化调整型 · 标签策略 |
| 复杂度 | `S` |
| 阶段 | `P1` |
| 复用度 | 高（多平台发布场景通用） |
| 资产形态 | 深度提示词 + Python 脚本（无模型调用、无 API Key） |

## 能力描述

1. **平台硬规则**：X ≤3 / TikTok 3-6 / 小红书 ≤10 / Instagram 3-5 / PH 用 topic /
   Reddit 用 flair 不用 #
2. **三层配比法**：按周发帖量分层（大 ≥5000 / 中 500-5000 / 小 <500 帖/周），
   满配 12 = 大3:中5:小4；上限受限时 3 个 = 大1:中1:小1，任何一层数量为 0 都是坏组合
3. **适配分**（脚本口径）= 0.7×单帖均互动归一分 + 0.3×竞争度分（1/(1+周发帖量/1000)）；
   相关度 0 的标签适配分 ×0.3 并排除
4. **防 tag stuffing**：零相关热标签（如发 SaaS 内容配 #coffee）直接排除并说明原因

## 输入规格

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `platform` | string | ✅ | X/Twitter / TikTok / 小红书 / Instagram / Product Hunt / 通用 |
| `content` | string | ✅ | 待发布的文案（用于相关度计算） |
| `tag_pool` | array | ✅ | 候选标签，每条含 `tag/posts_per_week/avg_engagement`；数据来自平台标签页或第三方工具导出快照 |

## 输出规格

- `combo`：推荐标签组合（按层配比，附层级与角色）
- `evals`：逐标签评估（层级 / 相关度 / 适配分 / 判定）
- 产物文件：`out/标签组合清单.xlsx`、`out/标签分数分布.png`、`out/tags.json`

## 使用步骤

### 方式一：纯提示词（最快）

1. 把 `prompt.txt` 全部内容粘贴为系统提示词
2. 提供文案 + 平台 + 候选标签及其热度数据
3. 得到分层组合与排除原因；无热度数据时它列清单让你补，不虚构

### 方式二：带脚本（精确计算 + 产出 Excel/PNG）

```bash
python3 <SKILL_DIR>/scripts/tag_score.py --input input.json --outdir out
python3 <SKILL_DIR>/scripts/tag_score.py --demo     # 无输入也能看效果
```

**分工**：脚本做分层、打分与配比（不漏不猜）；模型做语义相关复核与角色标注。
标签热度周级过时，发布前用平台标签页现值复核，相差 2 倍以上重算层级。

## 边界（不做的事）

- ❌ 不虚构热度数据；缺数据列清单让用户补，不填默认值
- ❌ 不推荐无关热门标签蹭流量（tag stuffing 判垃圾行为）
- ❌ 不承诺「配了必爆」——标签只影响分发池，不决定内容质量
- ❌ 数值以脚本输出为准，不要自己算

## 调用示例

**输入**（`examples/input.json`，节选）：

```json
{
  "platform": "X/Twitter",
  "content": "Shipping v2 of my churn analytics SaaS today. Weekly cohort view, Stripe sync, and a plain-English churn report for solo founders building in public.",
  "tag_pool": [
    {"tag": "#buildinpublic", "posts_per_week": 8200, "avg_engagement": 96},
    {"tag": "#SaaS", "posts_per_week": 42000, "avg_engagement": 51},
    {"tag": "#churn", "posts_per_week": 380, "avg_engagement": 130},
    {"tag": "#coffee", "posts_per_week": 480000, "avg_engagement": 210}
  ]
}
```

**输出**（脚本实跑，12 候选）：推荐组合 `#buildinpublic #microsaas #churn`
（大1:中1:小1）；#coffee 与内容零相关被排除（适配分重罚 ×0.3）；#indiehacker、
#devtools 词面无关排除。详见 `examples/output.md`。

## 所属工作流

- `one-draft-multi-platform-flow`（一稿多平台适配）

## 合规声明

- 本技能输出为 **AI 辅助建议**，发布动作保留人工确认，按平台要求标注 AI 生成内容
- 不买标签流量、不用无关热标签蹭流量、不参与标签机器人互推
- 标签热度以发布当日平台现值为准，本结果仅为快照分析

---

*本技能遵循 [bangwozuo 数字员工资产规范](https://github.com/bangwozuo/digital-employee-spec) v3.0*
