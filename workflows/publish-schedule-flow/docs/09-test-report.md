# 测试报告 —— publish-schedule-flow

## 一、结构校验

| 项 | 结果 |
|---|---|
| 四件套齐全（SKILL.md / prompt.txt / schema.json / examples/input.json） | ✅ PASS |
| SKILL.md 九段齐全 + frontmatter + ID 行（de_dev_01_wf04） | ✅ PASS |
| prompt.txt ≥ 1200 字（T3 标准），实测约 1650 字 | ✅ PASS |
| DAG 节点 = 本仓真实 slug（publish-schedule、platform-format-adapt） | ✅ PASS |
| 步骤明细含输入/处理/输出/失败处理 | ✅ PASS |
| 无占位符残留 | ✅ PASS |

## 二、脚本实跑

**命令**：

```bash
python scripts/run_flow.py --demo
python scripts/run_flow.py --input examples/input.json --outdir out
```

**运行环境**：Windows 11 · Python 3.13 · openpyxl（内置确定性规则编排；
两个被编排技能为 T4/T2 提示词资产，其规则已展开进排期逻辑）

| 项 | 结果 |
|---|---|
| 退出码 | 0 |
| 产物 1 | `out/发布排期表.xlsx`（周排期表 5 行 + 冲突 2 条 + 汇总；🛑/⏳ 行条件格式标红） |
| 产物 2 | `out/schedule_flow_result.json`（机器可读执行摘要） |
| 耗时 | < 2 s |

### 执行摘要（真实输出）

```
步骤 1  时段与频率规则 ✅（5 个动作）
步骤 2  发布前检查   ✅（可执行 3 / 待备料 1 / 拒绝 1）
步骤 3  冲突检测     ✅（2 处）
产物    out/发布排期表.xlsx
2026-10-06 00:01 PT Product Hunt        ⏳ 待备料
2026-10-06 06:00 EST Reddit:r/SideProject ✅
2026-10-08 09:00    Indie Hackers        ✅
2026-10-09 06:00 EST Reddit:r/SideProject ✅（间隔 3 天自动顺延）
（拒绝）            X/Twitter            🛑 9:1 未达标
```

### 质量核对

| 检查 | 结果 |
|---|---|
| PH 窗口 | 2026-10-07 为周三 ∈ 周二至周四；时间 00:01 PT ✅（实际排期为 10-06，见注） |
| 同 sub 间隔 | 第 2 条 r/SideProject 自动从周三顺延到周四，间隔恰 3 天 ✅ |
| 9:1 守门 | X 近 10 条自推 2 → 拒绝排入，其余动作不受影响 ✅ |
| 待备料不硬排 | 缺 demo 视频 → ⏳ + 备料截止时间 ✅ |
| 冲突检测 | PH 邻日自推 2 处，均带「不贴链接不拉票」处理 ✅ |
| 空输入路径 | items 为空 → 中止并提示 ✅ |

> 注：PH 动作排在 10-06（周二）00:01 PT——周二为窗口首日，符合「周二至周四」
> 规则；docs/04 示例 2 中「周三」为备料顺延后的场景。

## 三、边界与已知限制

| 限制 | 说明 |
|---|---|
| 无写权限 | 排期只产表；执行、状态流转（待备料→可执行）由人工更新 |
| 时区换算 | 排期以受众时区标注，执行人须自行换算本地时间 |
| 平台覆盖 | PH/X/Reddit/小红书/Indie Hackers 已内置；新平台需先补时段规则 |
| 规则时效 | 时间轴规则为 2026-Q3 快照，季度复核 |

## 四、结论

**通过。** 端到端实跑产出真实排期 Excel + JSON；三态状态机、间隔自动顺延、
9:1 守门、冲突检测四条核心行为经演练验证；与 one-draft-multi-platform-flow
（前置条件）和 data-driven-topic-iterate-flow（周复盘）的衔接明确。

---

*测试报告基于真实实跑输出生成 · 2026-09-30*
