# 测试报告 —— weekly-data-review

## 一、结构校验

| 项 | 结果 |
|---|---|
| 四件套齐全（SKILL.md / prompt.txt / schema.json / examples/input.json） | ✅ PASS |
| SKILL.md 九段齐全 + frontmatter + ID 行（de_dev_01_sk07） | ✅ PASS |
| prompt.txt ≥ 800 字（T1 标准），实测约 1750 字 | ✅ PASS |
| 量化约束（2-5% / 8-15% / 20-40% 基准、LTV/3 判定线、¥300 试错上限、7 天归因窗口） | ✅ PASS |
| 无占位符残留 | ✅ PASS |

## 二、脚本实跑

**命令**：

```bash
python scripts/weekly_review.py --demo
python scripts/weekly_review.py --input examples/input.json --outdir out
```

**运行环境**：Windows 11 · Python 3.13（WorkBuddy 内置环境）· openpyxl / matplotlib

| 项 | 结果 |
|---|---|
| 退出码 | 0 |
| 产物 1 | `out/周度复盘报告.xlsx`（渠道明细 5 行 + 漏斗体检 3 段 + 下周行动 5 条 + 汇总；破段/停投行条件格式标红） |
| 产物 2 | `out/渠道漏斗对比.png`（各渠道注册→激活率柱状图，基准 20-40% 标注在标题） |
| 产物 3 | `out/review.json`（机器可读，供 data-driven-topic-iterate-flow 读取） |
| 耗时 | < 3 s |

### 执行摘要（真实输出）

```
2026-W40：保留 Product Hunt Launch、Reddit r/SideProject、X buildinpublic、SEO 博客（自然）
          / 停投 付费投放（测试）；整体 CAC ¥43.2
 产物: out/周度复盘报告.xlsx
 产物: out/渠道漏斗对比.png
 产物: out/review.json
```

### 抽样核对（计算正确性）

| 检查 | 人工复算 | 脚本输出 | 结果 |
|---|---|---|---|
| 付费投放 CAC | 900÷4=225 | ¥225.0，判 🛑（≥180） | ✅ |
| X CAC | 60÷5=12 | ¥12.0，判 ✅（<180） | ✅ |
| Reddit 落地页→注册 | 21÷300=7.0% | 7.0% ⚠ <8% | ✅ |
| PH CTR | 505÷8000=6.3% | 6.3% ℹ >5% 核实口径 | ✅ |
| 整体 CAC | 1080÷25=43.2 | ¥43.2 | ✅ |
| 失败处理 | 去掉 ltv 重跑 | 退出非 0，打印补充 LTV 提示，不猜默认值 | ✅ |

## 三、边界与已知限制

| 限制 | 说明 |
|---|---|
| 归因依赖 UTM | 输入须先完成 UTM/引荐域归因；无主流量进「直接/未知」单列 |
| 小样本失真 | 周注册 <30 的渠道转化率天然波动 ±5%，模型复核时须加「样本不足」标注 |
| LTV 口径 | 输入估算 LTV 时判定线随之偏差，报告要求注明口径 |
| 资金决策 | 停投/加码仅出建议，人工确认后执行 |

## 四、结论

**通过。** 端到端实跑产出 Excel + PNG + JSON 三类真实文件；CAC、各级转化率
人工复算与脚本输出 6/6 一致；LTV 缺失拒绝执行的保护路径经演练验证。

---

*测试报告基于真实实跑输出生成 · 2026-09-30*
