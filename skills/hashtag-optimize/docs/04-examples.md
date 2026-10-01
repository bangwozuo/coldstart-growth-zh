# 使用示例

以下示例均来自 `scripts/tag_score.py` 对 `examples/input.json` 的实跑结果（退出码 0）。

## 示例 1：标准输入 —— X/Twitter 3 标签组合

**输入**（节选）：

```json
{
  "platform": "X/Twitter",
  "content": "Shipping v2 of my churn analytics SaaS today. Weekly cohort view, Stripe sync, and a plain-English churn report for solo founders building in public.",
  "tag_pool": [
    {"tag": "#buildinpublic", "posts_per_week": 8200, "avg_engagement": 96},
    {"tag": "#SaaS", "posts_per_week": 42000, "avg_engagement": 51},
    {"tag": "#churn", "posts_per_week": 380, "avg_engagement": 130}
  ]
}
```

**输出**：`out/标签组合清单.xlsx` + `out/标签分数分布.png` + `out/tags.json`。
12 候选 → 推荐组合 `#buildinpublic #microsaas #churn`（大1:中1:小1），
3 个零相关标签被排除。

## 示例 2：整改前后对照 —— 从「堆满标签」到「分层配比」

| 阶段 | 做法 | 结果 |
|---|---|---|
| 改造前 | 一条推文挂 8 个标签（#SaaS #startup #tech #AI #coffee #web #app #dev），全是 5,000+ 帖/周的大标签 | 触达持续低于账号均值；#coffee 与内容无关，被部分用户视为垃圾行为 |
| 改造后 | 3 个标签按大1:中1:小1 配比，每个标签有明确角色 | #churn 小池互动率高于大标签池；发帖进入 #microsaas 标签页并停留数小时 |

**关键差异**：标签不是「越多越大越好」——大标签 10 分钟冲走你的帖子，
中标签才是独立开发者性价比最高的分发位。

## 示例 3：零相关标签拦截（tag stuffing）

候选里 #coffee 周发帖 480,000、单帖均互动 210，数值全场最高。
脚本按相关度三级匹配（精确 token / 同义词表 / 前缀兜底）判定与内容零相关 →
适配分 ×0.3 重罚并标记「排除」。**互动数据再好，与内容无关的标签也不能要**——
这正是 tag stuffing 被平台判垃圾的典型场景。

## 示例 4：平台规则切换

同一文案发小红书：上限放宽到 10 个 → 配比自动扩为 大2:中4:小4（8 个可用标签
全部进入），并把最精准的 #churn 类标签放最前（小红书前 3 个标签决定分发池）。
同一脚本输入只改 `platform` 字段，无需重算。

## 示例 5：缺数据不猜

**输入**：`tag_pool` 中某标签缺 `posts_per_week`。

**输出**：该标签「层级」如实标注为「小（缺数据，按 0 处理）」，汇总页列出
缺失字段清单让用户从平台标签页补数——不虚构热度值、不填默认值。
