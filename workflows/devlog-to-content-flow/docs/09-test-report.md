# 测试报告 —— devlog-to-content-flow

## 一、结构校验

| 项 | 结果 |
|---|---|
| 四件套齐全（SKILL.md / prompt.txt / schema.json / examples/input.json） | ✅ PASS |
| SKILL.md 九段齐全 + frontmatter + ID 行（de_dev_01_wf02） | ✅ PASS |
| prompt.txt ≥ 1200 字（T3 标准），实测约 1750 字 | ✅ PASS |
| DAG 节点 = 本仓真实 slug（painpoint-sellingpoint-match、narrative-rewrite） | ✅ PASS |
| 步骤明细含输入/处理/输出/失败处理 | ✅ PASS |
| 无占位符残留 | ✅ PASS |

## 二、脚本实跑

**命令**：

```bash
python scripts/run_flow.py --demo
python scripts/run_flow.py --input examples/input.json --outdir out
```

**运行环境**：Windows 11 · Python 3.13 · openpyxl（内置规则编排，无上游脚本调用——
两个被编排技能为 T2 提示词资产，其规则已确定性展开进工单）

| 项 | 结果 |
|---|---|
| 退出码 | 0 |
| 产物 1 | `out/devlog叙事改写工单.xlsx`（门槛检查 6 行 + 角度工单 3 行 + 骨架 15 行 + 汇总；绝对词命中行条件格式标红） |
| 产物 2 | `out/devlog_flow_result.json`（机器可读执行摘要） |
| 耗时 | < 2 s |

### 执行摘要（真实输出）

```
步骤 1  素材门槛检查 ✅（绝对词 0 处）
步骤 2  钩子角度工单   ✅（3 角度）
步骤 3  五段式叙事工单 ✅（3 平台 × 5 要素）
结论    ✅ 可成稿
```

### 质量核对

| 检查 | 结果 |
|---|---|
| 数字溯源 | 8s / 2.1s / 20 分钟全部登记，成稿核对有对照物 ✅ |
| 失败细节 | 缓存击穿事故被识别并标记「保留进成稿」 ✅ |
| 术语清单 | DB、Redis、Webhook、缓存、队列 5 项待翻译，附 ≤2 个/百字规则 ✅ |
| 回炉路径演练 | devlog 注入「史上最丝滑」 → 结论「❌ 回炉」+ 命中词列出 ✅ |
| 空输入路径 | devlog 为空 → 中止并提示「无米之炊，不编造」，退出码非 0 ✅ |
| metrics 缺失路径 | 标注「数字待溯源」，不中止 ✅ |

## 三、边界与已知限制

| 限制 | 说明 |
|---|---|
| 成稿环节 | 工单只到骨架；成稿质量取决于模型按 narrative-rewrite prompt 的执行 |
| 数字换算 | 脚本登记原样数字；「8s→2.1s 写成快 4 倍」类换算需人工/模型在核对时拦截 |
| 平台覆盖 | X/Reddit/长文三档已内置；新平台须先补形态参数 |
| 语录核查 | 用户语录类编造无法纯规则拦截，依赖人工确认环节 |

## 四、结论

**通过。** 端到端实跑产出真实工单 Excel + JSON；数字溯源、回炉路径、
空输入与 metrics 缺失四条路径经演练验证；与 daily-topic-mine-flow /
publish-schedule-flow 的上下游衔接明确。

---

*测试报告基于真实实跑输出生成 · 2026-09-30*
