# 出海增长官

> **产品冷启动期的"增长合伙人"：替你想清楚今天在哪个社区、对谁、说什么话**

[![Stage](https://img.shields.io/badge/stage-P0-orange)](https://github.com/bangwozuo)
[![Asset](https://img.shields.io/badge/asset-prompt%20%2B%20scripts-blueviolet)](#资产形态)
[![NoKey](https://img.shields.io/badge/API%20Key-not%20required-success)](#资产形态)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)

![演示](docs/demo.mp4)

*20 秒实跑演示：社区热帖洞察 → 每日选题挖掘 → 一稿多平台适配 → 发布排期 → 数据驱动选题迭代（均为 `--demo` 真实执行截图串连，非摆拍）。*

---

## 它是谁

面向 **OPC** 的数字员工资产包。

| 项目 | 内容 |
|------|------|
| 目标用户 | 冷启动期 3-6 个月的 C 端/PLG 产品独立开发者，尤其中出海方向 |
| 交付物 | 周均内容产出 ≥5 条；目标社区（X/Reddit/即刻/小红书）月均曝光与Profile访问环比 +20%；冷启动期官网/产品页月均自然访问增量 |
| 技能数 | 7 |
| 工作流数 | 5 |
| 旧名存档 | `出海冷启动获客官（Build-in-Public 内容引擎）` |

---

## 数字员工总览

| 项目 | 内容 |
|------|------|
| 身份 | 出海增长官——产品冷启动期的「增长合伙人」，替你想清楚今天在哪个社区、对谁、说什么话 |
| 边界 | 只做选题/改写/排期/复盘的筛选与决策建议；不代刷量、不做付费投放执行、不代发帖（所有对外发布人工执行） |
| KPI | 周均内容产出 ≥5 条；目标社区月均曝光与 Profile 访问环比 +20%；冷启动期官网月均自然访问增量 |
| 资产形态 | 深度提示词 + 确定性 Python 脚本（无模型调用依赖、无 API Key、无平台写权限） |
| 交付纪律 | 所有输出 AI 辅助生成、人工审核后使用；数值以脚本输出为准 |

---

## 资产形态

| 特性 | 说明 |
|------|------|
| ✅ 无需 API Key | 一个 Key 都不需要 |
| ✅ 无需部署 | 提示词资产粘贴即用；脚本资产本地跑，产物落盘 Excel/PNG/JSON |
| ✅ 平台无关 | 提示词粘贴到任何 AI 工具；脚本只依赖 Python + openpyxl |
| ✅ 用户自备算力 | 模型来自你自己的订阅 |
| ✅ 确定性部分可复算 | 分类/打分/排期由脚本完成，可复算复核；语境判断由模型按 prompt 复核 |

---

## 资产矩阵（7 技能 + 5 工作流）

| # | 资产 | 一句话 | 类型 | README |
|---|------|--------|------|--------|
| 1 | 社区热帖洞察 | 热帖四分类 + 热度分档 + 9:1 额度核算，输出洞察清单与类别分布图 | T1 脚本型 | [README](skills/community-post-insight/README.md) |
| 2 | 痛点卖点匹配 | 痛点×功能配对，五角度钩子候选逐条过量化自检，错配如实弃用 | T2 提示词 | [README](skills/painpoint-sellingpoint-match/README.md) |
| 3 | 叙事改写 | devlog 五段式改写为 build-in-public 故事，数据诚实规则保命 | T2 提示词 | [README](skills/narrative-rewrite/README.md) |
| 4 | 平台格式适配 | 一篇母稿改 N 平台合格版本：硬规格表 + 信息保真 + 四步工作法 | T2 提示词 | [README](skills/platform-format-adapt/README.md) |
| 5 | 话题标签优化 | 6 平台上限 + 大中小三层配比 + 适配分公式，零相关重罚排除 | T1 脚本型 | [README](skills/hashtag-optimize/README.md) |
| 6 | 发布排期 | 4 平台时间轴规则 + 发布前五项检查 + 三类人工确认点 | T4 SOP | [README](skills/publish-schedule/README.md) |
| 7 | 周度数据复盘 | 渠道归因 + 漏斗基准体检 + CAC<LTV/3 判定，输出留/停决策表 | T1 脚本型 | [README](skills/weekly-data-review/README.md) |
| 8 | 每日选题挖掘 | 13 帖 → 选题卡 / 观察池 / 参与队列三张清单（每日 8:00） | T3 工作流 | [README](workflows/daily-topic-mine-flow/README.md) |
| 9 | 开发日志转内容 | devlog 过 6 项门槛 → 钩子角度 + 五段式叙事改写工单 | T3 工作流 | [README](workflows/devlog-to-content-flow/README.md) |
| 10 | 一稿多平台适配 | 母稿确认后一次铺多平台：规格工单 + 逐平台标签组合实跑 | T3 工作流 | [README](workflows/one-draft-multi-platform-flow/README.md) |
| 11 | 发布排期（工作流） | 待发布清单 → 三态周排期表（可执行/待备料/拒绝排入） | T3 工作流 | [README](workflows/publish-schedule-flow/README.md) |
| 12 | 数据驱动选题迭代 | 本周数据 → 渠道留/停 → 在跑选题加权/暂缓/降权 → 下周计划 | T3 工作流 | [README](workflows/data-driven-topic-iterate-flow/README.md) |

---

## 快速开始

```text
1. 打开 skills/community-post-insight/prompt.txt
2. 全文复制
3. 粘贴到你常用的 AI 工具（Coze / WorkBuddy / Dify / Claude / ChatGPT）
4. 按 SKILL.md 的输入规格提供数据
```

就这四步。完整指引见 [使用手册](docs/04-usage.md)。

---

## 仓库结构

```text
coldstart-growth-zh/
├── README.md / employee.md / package.yaml     # 入口与 12 字段定义卡
├── docs/01~07                                 # 员工级文档（架构/流程/场景/手册/示例/录像/测试）
├── skills/                                    # 7 个原子技能
│   └── <skill>/
│       ├── README.md  SKILL.md  prompt.txt  schema.json  examples/
│       └── docs/                              # 该技能自己的 10 项文档 + 配图
├── workflows/                                 # 5 条工作流（复合技能）
│   └── <workflow>/
│       ├── README.md  SKILL.md  prompt.txt  schema.json  examples/
│       └── docs/                              # 该工作流自己的 10 项文档 + 配图
├── knowledge/                                 # RAG wiki 知识库
│   ├── README.md  RAG-接入指南.md  template.md
│   └── wiki/(index.md, _template.md, entries/)
├── connectors/                                # 连接器说明 + 合规红线
├── quality/                                   # 效果基线与追踪日志
└── tests/                                     # 资产校验测试（离线，无需密钥）
```

### 每个技能 / 工作流自带的 docs

| 文档 | 内容 |
|------|------|
| `README.md` | 资产速览与快速开始 |
| `docs/01-usage-manual.md` | 安装使用手册 |
| `docs/02-architecture.md` | 业务架构图 |
| `docs/03-flow.md` | 流程图（Mermaid + 配图） |
| `docs/04-examples.md` | 使用示例 |
| `docs/05-media.md` | 截图和录屏（清单 + 分镜脚本） |
| `docs/06-scenarios.md` | 使用场景（适用 / 不适用） |
| `docs/07-audience.md` | 用户群体 |
| `docs/08-value.md` | 解决问题与价值 |
| `docs/09-test-report.md` | 测试报告 |
| `docs/assets/overview.svg` | 自动生成的流程示意图 |

---

## 交付物导航

| 文档 | 内容 |
|------|------|
| [业务架构](docs/01-architecture.md) | 四层架构 + 数据流 + 能力边界 |
| [工作流流程](docs/02-workflow.md) | 5 条工作流的 DAG 可视化 |
| [使用场景](docs/03-scenarios.md) | 3 个真实场景（含前后对比） |
| [使用手册](docs/04-usage.md) | 各平台导入指引 + 常见问题 |
| [示例库](docs/05-examples.md) | 7 组输入输出示例 |
| [录像脚本](docs/06-recording-script.md) | 7 镜头分镜 + 旁白稿 |
| [校验报告](docs/07-test-report.md) | 资产质量校验结果 |

---

## 知识库与连接器

| 目录 | 说明 |
|------|------|
| [`knowledge/`](knowledge/README.md) | RAG wiki 知识库：填入业务信息可显著提升输出质量 |
| [`connectors/`](connectors/README.md) | 连接器说明：数据从哪来、怎么合规地来 |

---

## 资产校验

```bash
pip install -r requirements.txt
pytest tests/ -v
```

校验技能完整性、提示词结构、契约一致性、工作流 DAG、技能级与工作流级 docs 完整性、知识库 wiki 与连接器结构。
**不需要任何 API Key。**

---

## 合规声明

- ✅ 所有输出为 **AI 辅助生成**，交付前须人工审核
- ✅ 提示词内置**违禁词禁止清单**，符合《广告法》要求
- ✅ 遵循《人工智能生成合成内容标识办法》
- ✅ 连接器只走**官方 API** 或**用户导出数据**
- ✅ 所有对外发布动作**保留人工确认环节**

---

## 许可

[Apache-2.0](LICENSE) — 可自由使用、修改、商用

---

*由 bangwozuo 业务库自动生成 · 2026-09-29*
