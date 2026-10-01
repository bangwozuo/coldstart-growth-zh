> 「AI 生成内容」标识

# 输出示例（run_flow.py 实跑）

> 由 `scripts/run_flow.py` 处理 `examples/input.json` 真实产出，非手写。

## 适配工单结论

| 项 | 内容 |
|---|---|
| 母稿字数 / 目标平台 | 251 / 3（X/Twitter、Product Hunt、小红书） |
| 纪律 | 同源多形：信息点一条不丢一条不编；超标版本不出手 |

## 平台规格工单（步骤 1，引自 platform-format-adapt 规格矩阵）

| 平台 | 上限 | 结构 | 调性 | 自推合规 |
|---|---|---|---|---|
| X/Twitter | 单帖 ≤280 字符；thread ≤7 条；标签 ≤3 | 一帖一点，首帖=钩子 | 朋友报信 | 允许 |
| Product Hunt | tagline ≤60 字符；5 图 + ≤60s demo | 发布会式 + 首评自述 | 利益直给 | 允许（产品发布场景） |
| 小红书 | 标题 ≤20 字；正文 ≤1000 字；标签 ≤10 | emoji 分段，前 2 行定完读 | 闺蜜安利 | 允许（软性） |

每行均附信息保真纪律：数字不改写不换算；砍字按「数字>场景>功能>形容词」。

## 标签组合（步骤 2，hashtag-optimize 实跑，逐平台不同）

| 平台 | 标签组合 | 组合数 | 排除数 | 说明 |
|---|---|---|---|---|
| X/Twitter | #buildinpublic #solofounder #churn | 3 | 1 | ≤3 上限 → 大1:中1:小1 |
| Product Hunt | #buildinpublic #solofounder #stripe #churn #cohortanalysis | 5 | 1 | 5 topic → 大1:中2:小2 |
| 小红书 | #buildinpublic #startup #solofounder #stripe #churn #cohortanalysis | 6 | 1 | ≤10 → 尽量配满 大2:中4:小4（相关标签只有 6 个，如实配 6） |

排除的 1 个 = #launchday（与母稿词面零相关，tag stuffing 风险）。
各平台明细：`out/tags_X_Twitter.json`、`out/tags_Product_Hunt.json`、`out/tags_小红书.json`。

## 步骤执行摘要

```
步骤 1  平台规格核对表 ✅（3 平台）
步骤 2  标签组合 ✅（hashtag-optimize 实跑 3 平台）
产物    out/一稿多平台适配工单.xlsx
```

## 边界情形核对

- **组合随上限变化**：同一标签池，X 只放 3 个（每层 1 个）、小红书放 6 个——
  层配比逻辑由上游脚本按平台上限自动伸缩，工单逐平台如实记录。
- **成稿语言提醒**：母稿为英文而目标平台为小红书时，中文成稿后须用成稿文本
  重跑标签（词面相关度与语言强相关），工单汇总页已标注该纪律。
- Reddit / Indie Hackers 不在本次平台列表内；若加入，标签行将标注
  「不用 # 标签（正文关键词 + flair 承担）」。
