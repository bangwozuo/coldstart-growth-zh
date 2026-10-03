# 截图与录屏

> 以下素材均来自**真实执行**：`--run` 实拍终端 / 实跑产物文件，无摆拍。

## 演示视频

![演示视频](assets/demo.mp4)

*Hyperframes 动态渲染 14s：命令逐字敲入（光标闪烁）→ 17 行真实输出逐行流式 → 实跑产物 Ken Burns 缓推*

## 执行截图

![真实执行](assets/run-terminal.png)

## 实跑产物

| 文件 | 说明 |
|---|---|
| [`out/_demo_input.json`](out/_demo_input.json) | 结构化结果（实跑生成） · 1 KB |
| [`out/_tag_input_Product Hunt.json`](out/_tag_input_Product Hunt.json) | 结构化结果（实跑生成） · 1 KB |
| [`out/_tag_input_X_Twitter.json`](out/_tag_input_X_Twitter.json) | 结构化结果（实跑生成） · 1 KB |
| [`out/_tag_input_小红书.json`](out/_tag_input_小红书.json) | 结构化结果（实跑生成） · 1 KB |
| [`out/multichannel_flow_result.json`](out/multichannel_flow_result.json) | 结构化结果（实跑生成） · 2 KB |
| [`out/tags_Product Hunt.json`](out/tags_Product Hunt.json) | 结构化结果（实跑生成） · 3 KB |
| [`out/tags_X_Twitter.json`](out/tags_X_Twitter.json) | 结构化结果（实跑生成） · 3 KB |
| [`out/tags_小红书.json`](out/tags_小红书.json) | 结构化结果（实跑生成） · 3 KB |
| [`out/一稿多平台适配工单.xlsx`](out/一稿多平台适配工单.xlsx) | Excel 工作簿（实跑生成） · 7 KB |
| [`out/标签分数分布.png`](out/标签分数分布.png) | 图表产物（实跑生成） · 32 KB |
| [`out/标签组合清单.xlsx`](out/标签组合清单.xlsx) | Excel 工作簿（实跑生成） · 7 KB |


---

## 附录：实跑输出明细

> 本资产为纯提示词客户端资产，无界面可截图。以下为**实跑运行效果**。

## 运行效果

### 输入

```json
{
  "input": "请提供工作流的初始输入数据"
}

```

### 输出

> 「AI 生成内容」标识

## 执行摘要

工作流因缺少初始输入数据而暂停，未进入任何原子技能执行步骤。

## 分步结果

1. 步骤 1（平台格式适配）：未执行 — 缺少 `content`、`target`、`platform` 输入。
2. 步骤 2（话题标签优化）：未执行 — 上一步无输出。

## 最终交付物

（无）

> 依据工作原则第 3 条：上一步输出不完整时，先提示补充，不强行继续。请提供待适配的原文及目标平台/风格要求后重新执行本工作流。


---

*运行效果由实跑验证生成*
