# 测试报告 —— community-post-insight

## 一、结构校验

| 项 | 结果 |
|---|---|
| 四件套齐全（SKILL.md / prompt.txt / schema.json / examples/input.json） | ✅ PASS |
| SKILL.md 九段齐全 + frontmatter + ID 行（de_dev_01_sk01） | ✅ PASS |
| prompt.txt ≥ 800 字（T1 标准），实测约 1900 字 | ✅ PASS |
| 量化约束（热度公式 / 24-72h 加权 / ≥200 分档 / 9:1 / ≥3 帖门槛） | ✅ PASS |
| 无占位符残留 | ✅ PASS |

## 二、脚本实跑

**命令**：

```bash
python scripts/insight_scan.py --demo
python scripts/insight_scan.py --input examples/input.json --outdir out
```

**运行环境**：Windows 11 · Python 3.13（WorkBuddy 内置环境）· openpyxl / matplotlib

| 项 | 结果 |
|---|---|
| 退出码 | 0 |
| 产物 1 | `out/热帖洞察清单.xlsx`（洞察明细 12 行 + 参与决策 4 条 + 汇总；痛点行、🔥 行条件格式标红） |
| 产物 2 | `out/帖子类别分布.png`（五类别柱状图，中文字体正常） |
| 产物 3 | `out/insight.json`（机器可读，供 daily-topic-mine-flow 读取） |
| 耗时 | < 3 s |

### 执行摘要（真实输出）

```
共 12 帖 —— 痛点 4 / 求助 2 / 竞品 2 / 自推 2 / 噪音 2；可参与 6 帖
 产物: out/热帖洞察清单.xlsx
 产物: out/帖子类别分布.png
 产物: out/insight.json
```

### 抽样核对（分类正确性）

| 帖子 | 机器判定 | 人工核对 |
|---|---|---|
| P001 Struggling with churn… | 痛点吐槽 🔥454.8 | ✅ 正确 |
| P004 Is there a tool…Would pay | 功能求助 🔥258.0 | ✅ 正确（含付费意愿信号） |
| P007 Pricing…how do you decide | 功能求助 🔥463.2 | ✅ 正确（初版误判噪音，词表迭代后修复，见 docs/04 示例 3） |
| P012 Just cancelled my Calendly… | 竞品流失 129.0 | ✅ 正确 |
| P002 I built…launched on PH | 自推晒作 76.8 | ✅ 正确 |

## 三、边界与已知限制

| 限制 | 说明 |
|---|---|
| 词表法误判 | 反讽/黑话（roast my、feels wrong）会漏判，须模型复核 |
| 版规时效 | sub 版规随时更新，参与前以侧边栏当前版规为准 |
| 数据来源 | 仅支持 Reddit 官方 API 或人工粘贴；不做爬虫绕流控 |
| 空数据 | posts 为空时如实输出 0 条，不编造 |

## 四、结论

**通过。** 端到端实跑产出 Excel + PNG + JSON 三类真实文件，四类判定抽样核对
5/5 正确（含 1 例初版误判经词表迭代修复）；9:1 额度核算与「单帖不成选题」
规则均落进产物。

---

*测试报告基于真实实跑输出生成 · 2026-09-30*
