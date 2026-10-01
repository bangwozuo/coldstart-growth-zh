# 测试报告 —— data-driven-topic-iterate-flow

## 一、结构校验

| 项 | 结果 |
|---|---|
| 四件套齐全（SKILL.md / prompt.txt / schema.json / examples/input.json） | ✅ PASS |
| SKILL.md 九段齐全 + frontmatter + ID 行（de_dev_01_wf05） | ✅ PASS |
| prompt.txt ≥ 1200 字（T3 标准），实测约 1750 字 | ✅ PASS |
| DAG 节点 = 本仓真实 slug（weekly-data-review） | ✅ PASS |
| 步骤明细含输入/处理/输出/失败处理 | ✅ PASS |
| 无占位符残留 | ✅ PASS |

## 二、脚本实跑

**命令**：

```bash
python scripts/run_flow.py --demo
python scripts/run_flow.py --input examples/input.json --outdir out
```

**运行环境**：Windows 11 · Python 3.13 · openpyxl / matplotlib（经 subprocess
调用上游技能脚本 weekly-data-review/scripts/weekly_review.py）

| 项 | 结果 |
|---|---|
| 退出码 | 0 |
| 产物 1 | `out/复盘与选题迭代清单.xlsx`（渠道判定 5 行 + 权重更新 5 行 + 下周计划 5 行 + 汇总；降权行/停投行条件格式标红） |
| 产物 2 | `out/topic_iterate_result.json`（机器可读执行摘要） |
| 附属产物 | `out/review.json`、`out/周度复盘报告.xlsx`、`out/渠道漏斗对比.png`（上游产物） |
| 耗时 | < 4 s |

### 执行摘要（真实输出）

```
步骤 1  weekly-data-review  ✅  → out/review.json
步骤 2  选题权重更新     ✅（5 个在跑选题）
步骤 3  下周选题计划     ✅
汇总    保留 4 渠道 / 停投 付费投放（测试）；加权 3 / 1 / 1
```

### 质量核对

| 检查 | 结果 |
|---|---|
| 步骤衔接 | 权重表的渠道判定与 review.json channels 逐条一致 ✅ |
| 规则正确性 | 加权 3（保留/自然渠道）、暂缓 1（Reddit 漏斗破段）、降权 1（付费投放停投）✅ |
| 反追热点 | 付费投放注册 96 全场最高仍降权（CAC ¥225 超标）✅ |
| 样本保护 | 周注册 <30 的选题判定降级为参考并标注 ✅ |
| 失败处理演练 | 删除 review.json 后重跑 → 正确中止并打印「上游产物缺失」 ✅ |
| 空输入路径 | active_topics 为空 → 占位清单正常退出，退出码 0 ✅ |

## 三、边界与已知限制

| 限制 | 说明 |
|---|---|
| 权重依赖上游 | 渠道判定的正确性取决于 weekly-data-review（含归因口径质量） |
| 单周波动 | 规则含「连续 2 周同向才改权重」纪律，但跨周状态需人工在清单上延续记录 |
| 数据来源 | 渠道数据须先完成 UTM/引荐域归因；无主流量单列 |
| 资金决策 | 停投/加码只出建议，人工确认后执行 |

## 四、结论

**通过。** 端到端实跑产出真实迭代清单 Excel + JSON；三类权重判定、反追热点
规则、样本保护与失败处理（上游中止/产物缺失/空输入）经演练验证；
五个工作流的选题-内容-发布-复盘闭环在此收口。

---

*测试报告基于真实实跑输出生成 · 2026-09-30*
