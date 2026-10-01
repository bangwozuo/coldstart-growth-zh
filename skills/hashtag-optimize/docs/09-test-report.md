# 测试报告 —— hashtag-optimize

## 一、结构校验

| 项 | 结果 |
|---|---|
| 四件套齐全（SKILL.md / prompt.txt / schema.json / examples/input.json） | ✅ PASS |
| SKILL.md 九段齐全 + frontmatter + ID 行（de_dev_01_sk05） | ✅ PASS |
| prompt.txt ≥ 800 字（T1 标准），实测约 1750 字 | ✅ PASS |
| 量化约束（≤3 / 3-6 / ≤10 上限、5000/500 分层阈值、0.7/0.3 权重、×0.3 重罚） | ✅ PASS |
| 无占位符残留 | ✅ PASS |

## 二、脚本实跑

**命令**：

```bash
python scripts/tag_score.py --demo
python scripts/tag_score.py --input examples/input.json --outdir out
```

**运行环境**：Windows 11 · Python 3.13（WorkBuddy 内置环境）· openpyxl / matplotlib

| 项 | 结果 |
|---|---|
| 退出码 | 0 |
| 产物 1 | `out/标签组合清单.xlsx`（评估明细 12 行 + 推荐组合 + 汇总；低相关行条件格式标红） |
| 产物 2 | `out/标签分数分布.png`（Top10 适配分横向柱状图） |
| 产物 3 | `out/tags.json`（机器可读，供 one-draft-multi-platform-flow 读取） |
| 耗时 | < 3 s |

### 执行摘要（真实输出）

```
X/Twitter：候选 12 个，排除低相关 3 个 → 推荐组合 3 个：#buildinpublic #microsaas #churn
 产物: out/标签组合清单.xlsx
 产物: out/标签分数分布.png
 产物: out/tags.json
```

### 抽样核对

| 检查 | 结果 |
|---|---|
| 分层正确性 | #churn(380/周)=小、#microsaas(2,400)=中、#buildinpublic(8,200)=大 ✅ |
| 配比正确性 | X 上限 3 → 大1:中1:小1，三层齐全 ✅ |
| tag stuffing 拦截 | #coffee（互动 210 全场最高，相关度 0）被排除 ✅ |
| 适配分排序 | #churn(67.2) > #microsaas(45.6) > #buildinpublic(36.9)，与互动/竞争度一致 ✅ |
| 开发迭代记录 | 初版相关度仅精确词面匹配导致 9/12 误杀；补同义词表 + 前缀兜底后排除数收敛到 3 个（2 个真无关 + 1 个真低频词） ✅ |

## 三、边界与已知限制

| 限制 | 说明 |
|---|---|
| 快照时效 | 热度数据是快照，周级过时；发布前须用平台标签页现值复核 |
| 同义词覆盖 | 词表覆盖有限（#buildinpublic 等已内置），长尾标签靠前缀兜底 + 模型复核 |
| 数据来源 | 周发帖量/均互动来自平台标签页或第三方工具导出，缺数据时不虚构 |
| 平台差异 | Reddit 用 flair 不用 #；PH 用 topic——平台表未识别时按「通用」处理 |

## 四、结论

**通过。** 端到端实跑产出 Excel + PNG + JSON 三类真实文件；分层/配比/零相关拦截
抽样核对全部正确；开发过程中的误杀问题（相关度过严）已修复并记录。

---

*测试报告基于真实实跑输出生成 · 2026-09-30*
