# 使用示例

以下示例均来自 `scripts/run_flow.py` 对 `examples/input.json` 的实跑结果（退出码 0）。

## 示例 1：标准输入 —— 4 条内容 → 5 动作的周排期

**输入**（节选）：

```json
{
  "week_start": "2026-10-05",
  "account_state": {"reddit_last_10_selfpromo": 1, "x_last_10_selfpromo": 2},
  "items": [
    {"title": "ChurnLens PH Launch", "platforms": ["Product Hunt"], "selfpromo": true, "material_ready": false},
    {"title": "v0.9 devlog", "platforms": ["Reddit:r/SideProject", "X/Twitter"], "selfpromo": true, "material_ready": true}
  ]
}
```

**输出**：`out/发布排期表.xlsx`（周排期表+冲突+汇总）+ `out/schedule_flow_result.json`。
可执行 3 / 待备料 1 / 拒绝 1，冲突 2 处带处理。

## 示例 2：整改前后对照 —— 从「想起来就发」到「状态机排期」

| 阶段 | 做法 | 结果 |
|---|---|---|
| 改造前 | 周五晚临时发 PH（周末流量低谷）；Reddit 两天连发两条自推 | PH 排名 15 以后；第二条被自动过滤，账号进观察名单 |
| 改造后 | PH 排周三 00:01 PT；Reddit 同 sub 间隔 ≥3 天自动顺延；9:1 未达标的 X 自推被拒绝排入 | PH 当日进前 10；Reddit 帖正常分发，无删帖 |

**关键差异**：排期表不是日历，是「账号资格 + 素材就绪 + 时段窗口」三个
闸门的状态机——三态（✅/⏳/🛑）让「能不能发」一目了然。

## 示例 3：9:1 守门（拒绝排入）

X 账号近 10 条自推 2 条 → X 自推动作「🛑 拒绝排入：先回补非自推参与」。
**拒绝不是惩罚是保护**：自推超标账号的帖子会被 sub/平台算法过滤，
排期表替你守住这个红线。

## 示例 4：同 sub 间隔自动顺延

第 2 条 r/SideProject 自推本应落周三，与第一条（周二）间隔仅 1 天 →
排期器自动顺延到周四，间隔恰好 3 天。间隔规则不靠人记，排期器兜底。

## 示例 5：待备料不硬排 + 备料截止

PH Launch 缺 demo 视频 → 「⏳ 待备料」+ 截止时间（周二 18:00 PT）。
若截止前仍未备齐，人工将其顺延到下周三——仍在周二至周四窗口内。
宁可晚一周，不烧不可再生的 launch 窗口。
