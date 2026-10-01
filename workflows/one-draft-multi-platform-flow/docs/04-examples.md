# 使用示例

以下示例均来自 `scripts/run_flow.py` 对 `examples/input.json` 的实跑结果（退出码 0）。

## 示例 1：标准输入 —— 一篇母稿 → 3 平台工单

**输入**（节选）：

```json
{
  "content": "ChurnLens v0.9 is live: Stripe sync that takes 15 minutes to set up, weekly cohort views, and plain-English churn reports — no SQL...",
  "platforms": ["X/Twitter", "Product Hunt", "小红书"],
  "tag_pool": [{"tag": "#churn", "posts_per_week": 380, "avg_engagement": 130}]
}
```

**输出**：`out/一稿多平台适配工单.xlsx`（规格工单 + 逐平台标签组合 + 汇总）+
`out/multichannel_flow_result.json` + 各平台 `tags_*.json`。
同一标签池 → X 3 个 / PH 5 个 / 小红书 6 个，组合随上限自动伸缩。

## 示例 2：整改前后对照 —— 从「复制粘贴」到「同源多形」

| 阶段 | 做法 | 结果 |
|---|---|---|
| 改造前 | 母稿原样贴 3 平台，标签统一 8 个 | Reddit 版被删（裸贴链接）；X 触达低于均值；小红书版没有分段完读 30% |
| 改造后 | 工单先行：每平台规格/调性/自推合规/标签一次排好 → 模型按工单成稿 → 核对表通过后进排期 | 无删帖；X 首帖钩子 + 小红书前 2 行各按平台重写，数字三平台同源 |

**关键差异**：一稿多发的收益来自「信息一次整理，形态各自重写」——
工单把「各自重写」需要遵守的规则固化下来，不靠临场记忆。

## 示例 3：自推合规硬字段拦截

platforms 加入 r/SaaS（讨论型 sub）：工单该行「自推合规=禁止（先参与讨论，
9:1 达标）」→ 帖子版不存在，只允许评论参与形态，排期阶段也不会给它排位。
**合规不是成稿后的检查项，是工单里先于成稿存在的字段。**

## 示例 4：语言与标签的联动

中文母稿直接跑标签 → 全部候选词面相关度 0 被排除（组合为空）——这不是
bug 而是正确拦截：英文标签配中文内容就是 tag stuffing。处理路径：
先按平台成稿语言改写（小红书中文 / X 英文），再用成稿文本重跑标签。

## 示例 5：上游失败不静默

**演练**：临时重命名 tag_score.py 模拟脚本损坏 → run_flow.py 退出码 1，
打印「上游技能 hashtag-optimize 退出码 2，流程中止」——不产出缺标签的
半成品工单，修复后重跑即恢复。
