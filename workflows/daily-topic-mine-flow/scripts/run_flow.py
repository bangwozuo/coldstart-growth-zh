# -*- coding: utf-8 -*-
"""
每日选题挖掘流程 —— 端到端编排脚本。

编排逻辑（与 SKILL.md 的 DAG 一致）：
  社区帖子流 → [community-post-insight] 四分类+热度分档+9:1 额度核算
            → 内置：痛点主题聚类 → 选题卡生成（按 painpoint-sellingpoint-match
              的五角度规则映射，标注证据帖与证据强度）
            → 每日选题清单.xlsx

失败处理：
  - 上游技能脚本退出码 != 0 → 中止并打印错误（不静默失败）
  - 上游产物 insight.json 缺失/损坏 → 中止并提示重跑上游
  - 帖子为空 → 输出「今日无目标帖」占位清单并正常退出
  - 主题证据不足 3 帖 → 不判选题，列观察池（单帖不成选题）

用法：
  python run_flow.py --input input.json --outdir out
  python run_flow.py --demo
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
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

INSIGHT_SCRIPT = os.path.join(REPO, "skills", "community-post-insight", "scripts", "insight_scan.py")

# 选题角度映射（与 painpoint-sellingpoint-match 的五角度一致）
THEME_ANGLE = {
    "定价": "成本账角度：把定价痛换算成用户的时间/金钱账",
    "上手门槛": "痛点瞬间角度：抓配置/接入卡住的具体时刻",
    "集成导出": "前后对比角度：手动搬运 vs 自动同步的具体数字对比",
    "性能": "前后对比角度：等待秒数从 X 到 Y（须真实实测）",
    "隐私安全": "反共识角度：小团队也能做好合规的具体清单",
    "移动端": "痛点瞬间角度：用户在移动场景卡住的那一下",
    "协作": "身份共鸣角度：一人团队也要协作的真实处境",
}
MIN_EVIDENCE = 3  # 单帖不成选题：同主题 ≥3 帖才入选

DEMO_INPUT = {
    "source": "r/SaaS + r/SideProject + r/indiehackers",
    "window_days": 7,
    "posts": [
        {"id": "P001", "subreddit": "r/SaaS", "title": "Struggling with churn - users sign up, never come back after day 3. What am I doing wrong?", "ups": 187, "num_comments": 96, "age_hours": 20, "url": "reddit.com/r/SaaS/comments/aa1"},
        {"id": "P002", "subreddit": "r/SaaS", "title": "I built a churn analytics tool and just launched on Product Hunt today - feedback wanted", "ups": 42, "num_comments": 11, "age_hours": 9, "url": "reddit.com/r/SaaS/comments/aa2"},
        {"id": "P003", "subreddit": "r/SideProject", "title": "Anyone else hate configuring webhooks? Spent 5 hours debugging one today", "ups": 96, "num_comments": 38, "age_hours": 30, "url": "reddit.com/r/SideProject/comments/aa3"},
        {"id": "P004", "subreddit": "r/indiehackers", "title": "Is there a tool that turns Stripe invoices into a simple monthly P&L? Would pay for this", "ups": 154, "num_comments": 52, "age_hours": 46, "url": "reddit.com/r/indiehackers/comments/aa4"},
        {"id": "P005", "subreddit": "r/SaaS", "title": "Switched from Intercom to a cheaper helpdesk - onboarding docs were the real cost", "ups": 88, "num_comments": 31, "age_hours": 80, "url": "reddit.com/r/SaaS/comments/aa5"},
        {"id": "P006", "subreddit": "r/SideProject", "title": "Just shipped v2 of my side project, roast my landing page", "ups": 25, "num_comments": 18, "age_hours": 15, "url": "reddit.com/r/SideProject/comments/aa6"},
        {"id": "P007", "subreddit": "r/indiehackers", "title": "Pricing my first SaaS at $9/mo feels wrong - how do you decide pricing?", "ups": 210, "num_comments": 88, "age_hours": 12, "url": "reddit.com/r/indiehackers/comments/aa7"},
        {"id": "P008", "subreddit": "r/SaaS", "title": "PSA: export your data before your tool shuts down (again)", "ups": 61, "num_comments": 24, "age_hours": 100, "url": "reddit.com/r/SaaS/comments/aa8"},
        {"id": "P009", "subreddit": "r/indiehackers", "title": "Why is GDPR compliance so painful for a one-person EU startup?", "ups": 133, "num_comments": 57, "age_hours": 55, "url": "reddit.com/r/indiehackers/comments/aa9"},
        {"id": "P010", "subreddit": "r/SideProject", "title": "My app is slow on mobile, anyone dealt with this? Lag on every scroll", "ups": 34, "num_comments": 15, "age_hours": 28, "url": "reddit.com/r/SideProject/comments/aa10"},
        {"id": "P012", "subreddit": "r/indiehackers", "title": "Just cancelled my Calendly subscription, moved away from seat-based pricing tools", "ups": 71, "num_comments": 29, "age_hours": 66, "url": "reddit.com/r/indiehackers/comments/aa12"},
        {"id": "P013", "subreddit": "r/SaaS", "title": "Setup wizard is too confusing - 40% drop off at step 2 of onboarding", "ups": 65, "num_comments": 27, "age_hours": 40, "url": "reddit.com/r/SaaS/comments/aa13"},
        {"id": "P014", "subreddit": "r/indiehackers", "title": "Learning curve too steep: gave up configuring self-hosted analytics after a weekend", "ups": 58, "num_comments": 22, "age_hours": 62, "url": "reddit.com/r/indiehackers/comments/aa14"},
    ],
}


def run_upstream(payload_path: str, outdir: str) -> str:
    """步骤 1：调用 community-post-insight 脚本，返回其 JSON 产物路径。"""
    r = subprocess.run(
        [sys.executable, INSIGHT_SCRIPT, "--input", payload_path, "--outdir", outdir],
        cwd=FLOW_DIR, capture_output=True, text=True, timeout=180,
    )
    if r.returncode != 0:
        print(f"[失败处理] 上游技能 community-post-insight 退出码 {r.returncode}，流程中止。", file=sys.stderr)
        print(r.stderr[-800:], file=sys.stderr)
        sys.exit(1)
    js = os.path.join(outdir, "insight.json")
    if not os.path.exists(js):
        print(f"[失败处理] 上游产物 {js} 缺失，流程中止（请重跑上游技能）。", file=sys.stderr)
        sys.exit(1)
    return js


def build_topic_cards(items: list[dict]) -> tuple[list[dict], list[dict]]:
    """步骤 2（内置）：主题聚类 → 选题卡。返回（选题卡, 观察池）。"""
    # 只用痛点/求助/竞品帖做主题聚类（自推与噪音不成选题）
    pool = [i for i in items if i["类别"] in ("痛点吐槽", "功能求助", "竞品流失")]
    themes: dict[str, list[dict]] = {}
    for it in pool:
        if it["痛点主题"] and it["痛点主题"] != "—":
            for t in it["痛点主题"].split("、"):
                themes.setdefault(t, []).append(it)

    cards, watch = [], []
    for theme, posts in sorted(themes.items(), key=lambda kv: -len(kv[1])):
        posts_sorted = sorted(posts, key=lambda p: -p["热度分"])[:3]
        evidence = [{"id": p["帖子ID"], "sub": f"r/{p['subreddit']}",
                     "heat": p["热度分"], "url": p["URL"]} for p in posts_sorted]
        card = {
            "主题": theme,
            "证据帖数": len(posts),
            "总热度": sum(p["热度分"] for p in posts),
            "证据链": json.dumps(evidence, ensure_ascii=False),
            "建议角度": THEME_ANGLE.get(theme, "痛点瞬间角度：抓具体场景"),
            "下一步": "交 painpoint-sellingpoint-match 生成钩子候选",
        }
        if len(posts) >= MIN_EVIDENCE:
            card["判定"] = f"✅ 入选（{len(posts)} 帖 ≥ {MIN_EVIDENCE} 帖门槛）"
            cards.append(card)
        else:
            card["判定"] = f"⚠ 观察池（{len(posts)} 帖 < {MIN_EVIDENCE} 帖门槛，单帖不成选题）"
            watch.append(card)
    cards.sort(key=lambda c: -c["总热度"])
    watch.sort(key=lambda c: -c["总热度"])
    return cards, watch


def main():
    ap = argparse.ArgumentParser(description="每日选题挖掘流程")
    ap.add_argument("--input", help="流程输入 JSON（同 community-post-insight 输入）")
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()

    at.ensure_outdir(a.outdir)
    if a.demo:
        payload_path = os.path.join(a.outdir, "_demo_input.json")
        at.write_json(DEMO_INPUT, payload_path)
    elif a.input:
        payload_path = a.input
    else:
        ap.error("需要 --input / --demo 之一")

    # 步骤 1：上游四分类 + 热度分档
    insight_js = run_upstream(payload_path, a.outdir)
    insight = at.read_json(insight_js)
    items = insight.get("items", [])

    # 步骤 2（内置）：主题聚类 → 选题卡 / 观察池
    cards, watch = build_topic_cards(items)

    if not items:
        summary = {"结论": "今日无目标帖（输入为空）", "帖子总数": 0}
    else:
        summary = dict(insight["summary"])
        summary["入选选题数"] = len(cards)
        summary["观察池主题数"] = len(watch)

    # 人工参与队列（非自推优先，呼应 9:1）
    join_queue = [{"帖子ID": i["帖子ID"], "sub": f"r/{i['subreddit']}",
                   "类别": i["类别"], "热度档": i["热度档"], "URL": i["URL"],
                   "参与建议": i["参与建议"]}
                  for i in items if i["类别"] in ("痛点吐槽", "功能求助")]

    at.ensure_outdir(a.outdir)
    xlsx = at.write_excel(
        os.path.join(a.outdir, "每日选题清单.xlsx"),
        {
            "选题卡": cards or [{"主题": "（今日无入选选题）", "判定": "—", "证据帖数": 0,
                                 "总热度": 0, "证据链": "", "建议角度": "", "下一步": ""}],
            "观察池": watch or [{"主题": "（观察池为空）", "判定": "—", "证据帖数": 0,
                                 "总热度": 0, "证据链": "", "建议角度": "", "下一步": ""}],
            "参与队列": join_queue or [{"帖子ID": "（无可参与帖）", "sub": "", "类别": "",
                                        "热度档": "", "URL": "", "参与建议": ""}],
            "汇总": [{"项": k, "内容": str(v)} for k, v in summary.items()],
        },
        highlights={"选题卡": {"判定": "contains:入选"},
                    "观察池": {"判定": "contains:观察池"},
                    "参与队列": {"类别": "contains:功能求助"}},
        widths={"选题卡": {"证据链": 40, "建议角度": 34, "下一步": 30},
                "观察池": {"证据链": 40, "建议角度": 34},
                "参与队列": {"参与建议": 46}},
    )
    js = at.write_json({"summary": summary, "topic_cards": cards, "watchlist": watch,
                        "join_queue": join_queue, "generated_at": at.stamp(),
                        "note": "选题判定的证据链均来自上游 insight.json，未新增任何帖子"},
                       os.path.join(a.outdir, "topic_mine_result.json"))
    print(f"步骤 1  community-post-insight ✅  → {insight_js}")
    print(f"步骤 2  主题聚类+选题卡   ✅  → {xlsx}")
    print(f"汇总    {summary.get('帖子总数', 0)} 帖：入选选题 {len(cards)}，观察池 {len(watch)}，"
          f"可参与 {len(join_queue)} 帖")
    at.emit({"files": [xlsx, js], "summary": summary})


if __name__ == "__main__":
    main()
