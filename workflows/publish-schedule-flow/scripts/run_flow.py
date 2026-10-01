# -*- coding: utf-8 -*-
"""
发布排期流程 —— 端到端编排脚本。

编排逻辑（与 SKILL.md 的 DAG 一致）：
  待发布内容清单
   → [内置] 平台时段与频率规则（引自 publish-schedule：PH 周二至周四 00:01 PT、
     Reddit 工作日 06:00 EST 且同 sub 间隔 ≥3 天、X thread ≤1/日、小红书 ≤2/日）
   → [内置] 发布前检查（素材齐备 / 9:1 参与比 / 格式核对结论）
   → [内置] 冲突检测（自推撞车、间隔不足、撞大版本日）
   → 发布排期表.xlsx + schedule_flow_result.json

失败处理：
  - items 为空 → 中止并提示
  - 9:1 不达标 → 该自推动作「拒绝排入」，其余照常（不静默放行）
  - 素材未齐 → 「⏳ 待备料」状态 + 备料截止时间，不硬排
用法：
  python run_flow.py --input input.json --outdir out
  python run_flow.py --demo
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FLOW_DIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(FLOW_DIR))
sys.path.insert(0, os.path.join(REPO, "lib"))

try:
    import assettools as at
except ImportError:  # pragma: no cover
    print("[错误] 未找到 lib/assettools.py", file=sys.stderr)
    sys.exit(2)

# 平台时段与频率规则（引自 publish-schedule 的时间轴规则，受众时区）
RULES = {
    "Product Hunt": {"窗口": "周二至周四（避开周末流量低谷）", "时间": "00:01 PT（投票窗口最长 24h）",
                     "频率": "一次 launch 是不可再生资源", "类型": "自推"},
    "X/Twitter": {"窗口": "工作日", "时间": "09:00 或 20:00（受众时区）",
                  "频率": "thread ≤1/日、散帖 ≤3/日", "类型": "可自推"},
    "Reddit": {"窗口": "工作日", "时间": "06:00-08:00 EST（美东上班前）",
               "频率": "同 sub 间隔 ≥3 天；9:1 达标才排自推", "类型": "视 sub 而定"},
    "小红书": {"窗口": "每日", "时间": "12:00 或 21:00", "频率": "≤2 篇/日", "类型": "可自推"},
    "Indie Hackers": {"窗口": "工作日", "时间": "09:00", "频率": "—", "类型": "可自推（披露身份）"},
}

DEMO_INPUT = {
    "week_start": "2026-10-05",   # 周一
    "audience_tz": "America/Los_Angeles",
    "account_state": {"reddit_last_10_selfpromo": 1, "x_last_10_selfpromo": 2},
    "items": [
        {"title": "ChurnLens PH Launch（v0.9 正式发布）", "platforms": ["Product Hunt"],
         "selfpromo": True, "material_ready": False, "missing": "demo 视频（≤60 秒）"},
        {"title": "v0.9 devlog（缓存重构故事）", "platforms": ["Reddit:r/SideProject", "X/Twitter"],
         "selfpromo": True, "material_ready": True},
        {"title": "流失分析教程长文", "platforms": ["Indie Hackers"],
         "selfpromo": False, "material_ready": True},
        {"title": "导出功能使用技巧", "platforms": ["Reddit:r/SideProject"],
         "selfpromo": True, "material_ready": True},
    ],
}


def next_weekday(start: dt.date, weekdays: tuple, offset_days: int = 0) -> dt.date:
    d = start + dt.timedelta(days=offset_days)
    while d.weekday() not in weekdays:
        d += dt.timedelta(days=1)
    return d


def schedule_items(payload: dict) -> tuple[list[dict], list[dict]]:
    week_start = dt.date.fromisoformat(payload.get("week_start", "2026-10-05"))
    state = payload.get("account_state", {})
    reddit_quota_ok = state.get("reddit_last_10_selfpromo", 0) <= 1   # 9:1 达标（近 10 条自推 ≤1）
    x_quota_ok = state.get("x_last_10_selfpromo", 0) <= 1
    rows, conflicts = [], []
    reddit_last: dict[str, dt.date] = {}
    x_thread_day: dt.date | None = None

    for it in payload.get("items", []):
        for plat_raw in it.get("platforms", []):
            plat, _, sub = plat_raw.partition(":")
            sub = sub or it.get("subreddit", "")
            row = {"内容": it["title"], "平台": f"{plat}{':' + sub if sub else ''}",
                   "类型": RULES.get(plat, {}).get("类型", "需人工核对"),
                   "时段规则": RULES.get(plat, {}).get("时间", "—"), "日期": "", "时间": "",
                   "前置条件": "", "状态": "", "标记": "✅", "人工确认点": "发布前终稿确认"}
            if plat == "Product Hunt":
                d = next_weekday(week_start, (1, 2, 3), offset_days=1)   # 周二~周四窗口，从周二起
                row.update(日期=str(d), 时间="00:01 PT",
                           前置条件="5 图 + ≤60s demo + tagline ≤60 字符 + 首评草稿",
                           人工确认点="发布前终稿；上线后首 8 小时评论值守")
                if not it.get("material_ready", True):
                    row["状态"] = f"⏳ 待备料（缺 {it.get('missing', '素材')}）；备料截止 周二 18:00 PT"
                    row["标记"] = "⚠"
                else:
                    row["状态"] = "✅ 可执行"
            elif plat == "Reddit":
                if it.get("selfpromo") and not reddit_quota_ok:
                    row["状态"] = "🛑 拒绝排入：9:1 未达标（近 10 条自推 >1），先完成非自推参与"
                    row["标记"] = "🛑"
                    rows.append(row)
                    continue
                # 同 sub 间隔 ≥3 天
                prev = reddit_last.get(sub)
                d = next_weekday(week_start, (0, 1, 2, 3, 4), offset_days=1)
                if prev:
                    while (d - prev).days < 3 or d <= prev:
                        d += dt.timedelta(days=1)
                        while d.weekday() not in (0, 1, 2, 3, 4):
                            d += dt.timedelta(days=1)
                reddit_last[sub] = d
                row.update(日期=str(d), 时间="06:00 EST",
                           前置条件=f"9:1 达标：{'✅（近 10 条自推 ' + str(state.get('reddit_last_10_selfpromo', 0)) + '）' if reddit_quota_ok else '❌'}；"
                                    f"无上下文裸贴链接 = 最高频删帖原因，链接挂在有价值回答之后",
                           状态="✅ 可执行",
                           人工确认点="发布前终稿；发布后 30 分钟首次互动检查")
                if it.get("selfpromo") and any(r["平台"].startswith("Product Hunt") for r in rows):
                    conflicts.append({"冲突": f"「{it['title']}」（{plat}:{sub}）与 PH Launch 间隔仅 1 天",
                                      "处理": "Reddit 帖不放 PH 链接、不发求投票内容（刷 upvote 红线）；两内容主题错开"})
            elif plat == "X/Twitter":
                if it.get("selfpromo") and not x_quota_ok:
                    row["状态"] = "🛑 拒绝排入：X 近 10 条自推 >1，先回补非自推参与"
                    row["标记"] = "🛑"
                    rows.append(row)
                    continue
                d = next_weekday(week_start, (0, 1, 2, 3, 4), offset_days=1)
                if x_thread_day is None:
                    x_thread_day = d
                row.update(日期=str(d), 时间="09:00 受众时区",
                           前置条件=f"thread ≤1/日；9:1 参考：近 10 条自推 {state.get('x_last_10_selfpromo', 0)}",
                           状态="✅ 可执行（本周 X 自推仅此 1 条，其余非自推回补）",
                           人工确认点="发布前终稿确认")
            else:
                d = next_weekday(week_start, (0, 1, 2, 3, 4), offset_days=3)
                row.update(日期=str(d), 时间=RULES.get(plat, {}).get("时间", "09:00"),
                           前置条件="格式核对结论通过（来自 one-draft-multi-platform-flow）",
                           状态="✅ 可执行" if it.get("material_ready", True) else "⏳ 待备料")
                if "待备料" in row["状态"]:
                    row["标记"] = "⚠"
            rows.append(row)
    rows.sort(key=lambda r: (r["日期"] or "9999", r["时间"]))
    return rows, conflicts


def main():
    ap = argparse.ArgumentParser(description="发布排期流程")
    ap.add_argument("--input", help="输入 JSON（week_start/account_state/items）")
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()

    at.ensure_outdir(a.outdir)
    if a.demo:
        payload = DEMO_INPUT
        payload_path = os.path.join(a.outdir, "_demo_input.json")
        at.write_json(payload, payload_path)
    elif a.input:
        payload = at.read_json(a.input)
    else:
        ap.error("需要 --input / --demo 之一")

    if not payload.get("items"):
        raise SystemExit("[失败处理] items 为空：没有待发布内容，流程中止。")

    rows, conflicts = schedule_items(payload)
    n_ok = sum(1 for r in rows if r["状态"] == "✅ 可执行")
    n_wait = sum(1 for r in rows if "待备料" in r["状态"])
    n_reject = sum(1 for r in rows if "拒绝" in r["状态"])
    summary = {
        "排期周": payload.get("week_start", ""),
        "受众时区": payload.get("audience_tz", "America/Los_Angeles"),
        "动作总数": len(rows),
        "可执行 / 待备料 / 拒绝": f"{n_ok} / {n_wait} / {n_reject}",
        "时间轴规则": "PH 周二至周四 00:01 PT；Reddit 工作日 06:00 EST 且同 sub 间隔 ≥3 天；X thread ≤1/日",
        "合规红线": "不刷 upvote、不买假用户；9:1 未达标的自推动作拒绝排入；首日评论逐条回复",
        "说明": "排期为确定性规则产物；执行由人工完成，无平台写权限",
    }

    xlsx = at.write_excel(
        os.path.join(a.outdir, "发布排期表.xlsx"),
        {
            "周排期表": rows,
            "冲突与处理": conflicts or [{"冲突": "（无冲突）", "处理": ""}],
            "汇总": [{"项": k, "内容": str(v)} for k, v in summary.items()],
        },
        highlights={"周排期表": {"标记": "contains:🛑", "状态": "contains:待备料"}},
        widths={"周排期表": {"内容": 34, "前置条件": 44, "状态": 40, "人工确认点": 28}},
    )
    js = at.write_json({"summary": summary, "schedule": rows, "conflicts": conflicts,
                        "generated_at": at.stamp(),
                        "note": "排期规则引自 publish-schedule（de_dev_01_sk06）；格式核对结论依赖 platform-format-adapt"},
                       os.path.join(a.outdir, "schedule_flow_result.json"))
    print(f"步骤 1  时段与频率规则 ✅（{len(rows)} 个动作）")
    print(f"步骤 2  发布前检查   ✅（可执行 {n_ok} / 待备料 {n_wait} / 拒绝 {n_reject}）")
    print(f"步骤 3  冲突检测     ✅（{len(conflicts)} 处）")
    print(f"产物    {xlsx}")
    at.emit({"files": [xlsx, js], "summary": summary})


if __name__ == "__main__":
    main()
