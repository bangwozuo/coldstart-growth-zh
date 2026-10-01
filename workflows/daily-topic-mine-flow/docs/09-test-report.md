# 测试报告 —— daily-topic-mine-flow

## 一、结构校验

| 项 | 结果 |
|---|---|
| 四件套齐全（SKILL.md / prompt.txt / schema.json / examples/input.json） | ✅ PASS |
| SKILL.md 九段齐全 + frontmatter + ID 行（de_dev_01_wf01） | ✅ PASS |
| prompt.txt ≥ 1200 字（T3 标准），实测约 1900 字 | ✅ PASS |
| DAG 节点 = 本仓真实 slug（community-post-insight、painpoint-sellingpoint-match 规则引用） | ✅ PASS |
| 步骤明细含输入/处理/输出/失败处理 | ✅ PASS |
| 无占位符残留 | ✅ PASS |

## 二、脚本实跑

**命令**：

```bash
python scripts/run_flow.py --demo
python scripts/run_flow.py --input examples/input.json --outdir out
```

**运行环境**：Windows 11 · Python 3.13 · openpyxl / matplotlib（经 subprocess
编排上游技能脚本 community-post-insight/scripts/insight_scan.py）

| 项 | 结果 |
|---|---|
| 退出码 | 0 |
| 产物 1 | `out/每日选题清单.xlsx`（选题卡 + 观察池 + 参与队列 + 汇总；入选行/求助行条件格式标红） |
| 产物 2 | `out/topic_mine_result.json`（机器可读执行摘要） |
| 附属产物 | `out/insight.json`、`out/热帖洞察清单.xlsx`、`out/帖子类别分布.png`（上游技能产物） |
| 耗时 | < 4 s |

### 执行摘要（真实输出）

```
步骤 1  community-post-insight ✅  → out/insight.json
步骤 2  主题聚类+选题卡   ✅  → out/每日选题清单.xlsx
汇总    13 帖：入选选题 1，观察池 4，可参与 8 帖
```

### 质量核对

| 检查 | 结果 |
|---|---|
| 步骤衔接 | 选题卡/观察池证据链与 insight.json items 逐条一致，零新增 ✅ |
| 3 帖门槛 | 上手门槛 3 帖入选；定价 2/3 等进观察池并标注缺口 ✅ |
| 失败处理演练 | 删除 insight.json 后重跑 → 正确中止并打印「上游产物缺失」，无静默失败 ✅ |
| 空输入路径 | posts: [] → 「今日无目标帖」占位清单，退出码 0 ✅ |
| 词表回归 | P013/P014 初版漏判 → 修复上游词表 → 主题凑满 3 帖入选（回归探测器价值实证） ✅ |

## 三、边界与已知限制

| 限制 | 说明 |
|---|---|
| 上游误判传导 | 词表分类漏判会传导到选题（本仓已有发现→修复→回归闭环示例） |
| 数据来源 | 仅 Reddit 官方 API / 人工粘贴；不做爬虫绕流控 |
| 观察池纪律 | 连续 2 周不足 3 帖的主题应放弃，需人工在周复盘时执行 |
| 发帖动作 | 流程无平台写权限，参与/发帖全部人工执行 |

## 四、结论

**通过。** 端到端实跑产出真实 Excel + JSON，3 帖门槛、证据链零新增、
9:1 队列与失败处理（上游中止/产物缺失/空输入）均经演练验证。

---

*测试报告基于真实实跑输出生成 · 2026-09-30*
