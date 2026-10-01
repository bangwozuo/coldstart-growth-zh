# 测试报告 —— one-draft-multi-platform-flow

## 一、结构校验

| 项 | 结果 |
|---|---|
| 四件套齐全（SKILL.md / prompt.txt / schema.json / examples/input.json） | ✅ PASS |
| SKILL.md 九段齐全 + frontmatter + ID 行（de_dev_01_wf03） | ✅ PASS |
| prompt.txt ≥ 1200 字（T3 标准），实测约 1800 字 | ✅ PASS |
| DAG 节点 = 本仓真实 slug（platform-format-adapt、hashtag-optimize） | ✅ PASS |
| 步骤明细含输入/处理/输出/失败处理 | ✅ PASS |
| 无占位符残留 | ✅ PASS |

## 二、脚本实跑

**命令**：

```bash
python scripts/run_flow.py --demo
python scripts/run_flow.py --input examples/input.json --outdir out
```

**运行环境**：Windows 11 · Python 3.13 · openpyxl（经 subprocess 逐平台调用
上游技能脚本 hashtag-optimize/scripts/tag_score.py）

| 项 | 结果 |
|---|---|
| 退出码 | 0 |
| 产物 1 | `out/一稿多平台适配工单.xlsx`（规格工单 3 行 + 标签组合 3 行 + 汇总；自推合规「禁止」行标红） |
| 产物 2 | `out/multichannel_flow_result.json`（机器可读执行摘要） |
| 附属产物 | `out/tags_X_Twitter.json`、`out/tags_Product_Hunt.json`、`out/tags_小红书.json`（上游实跑产物） |
| 耗时 | < 5 s（3 次上游调用） |

### 执行摘要（真实输出）

```
步骤 1  平台规格核对表 ✅（3 平台）
步骤 2  标签组合 ✅（hashtag-optimize 实跑 3 平台）
产物    out/一稿多平台适配工单.xlsx
X/Twitter -> #buildinpublic #solofounder #churn
Product Hunt -> #buildinpublic #solofounder #stripe #churn #cohortanalysis
小红书 -> #buildinpublic #startup #solofounder #stripe #churn #cohortanalysis
```

### 质量核对

| 检查 | 结果 |
|---|---|
| 组合随上限伸缩 | X 3 个（1:1:1）/ PH 5 个（1:2:2）/ 小红书 6 个（配满可用相关标签） ✅ |
| 自推合规硬字段 | 工单逐平台登记；讨论型 sub 场景拦截路径在 docs/04 示例 3 演练 ✅ |
| 零相关排除 | #launchday 全平台排除（tag stuffing 拦截传导正常） ✅ |
| 失败处理演练 | 重命名 tag_score.py 模拟损坏 → 退出码 1 + stderr 打印，无静默失败 ✅ |
| 空输入路径 | content 为空 → 中止提示「无米之炊」 ✅ |

## 三、边界与已知限制

| 限制 | 说明 |
|---|---|
| 规格快照 | 平台上限为 2026-Q3 快照，季度复核；未识别平台按通用规格兜底 |
| 语言联动 | 标签相关度与成稿语言强相关；母稿语言 ≠ 成稿语言时须用成稿重跑标签 |
| 成稿环节 | 工单到骨架为止；成稿由模型按 platform-format-adapt prompt 完成 |
| 写权限 | 流程无平台写权限，发布由人工/排期工作流调度执行 |

## 四、结论

**通过。** 端到端实跑产出真实工单 Excel + JSON + 3 份上游标签产物；
组合随平台伸缩、自推合规硬字段、失败不静默三条核心行为经演练验证。

---

*测试报告基于真实实跑输出生成 · 2026-09-30*
