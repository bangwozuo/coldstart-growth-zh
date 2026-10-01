# -*- coding: utf-8 -*-
"""
社区热帖洞察 —— 帖子四分类 + 热度分级 + 参与决策的确定性扫描器。

职责边界：本脚本只做**词表分类、热度打分、参与比核算与产物生成**（机器强项）。
痛点背后的真实动机、跟帖话术的语气拿捏由模型按 prompt.txt 完成（模型强项）。

用法：
  python insight_scan.py --input input.json --outdir out
  python insight_scan.py --demo              # 用内置样例跑一遍

产物：
  out/热帖洞察清单.xlsx   洞察明细（热门标红）/ 参与决策 / 汇总
  out/帖子类别分布.png    四类别占比柱状图
  out/insight.json        机器可读结果（供工作流读取）
"""
from __future__ import annotations

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(SKILL_DIR))
sys.path.insert(0, os.path.join(REPO, "lib"))

try:
    import assettools as at
except ImportError:  # pragma: no cover
    print("[错误] 未找到 lib/assettools.py。请确认技能位于 <repo>/skills/<slug>/scripts/ 下，"
          "且 <repo>/lib/assettools.py 存在。", file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------- 词表
# 每类：(正则, 类别)。顺序即优先级：先命中先归类。

PAIN_WORDS = [
    r"struggle|stuck|can'?t (?:figure|get|deal)|hate|frustrat|waste (?:of time|hours)",
    r"why is (?:it|this) so (?:hard|difficult)|anyone else (?:struggl|dealing|hate)|anyone (?:dealt|deal) with",
    r"pain point|painpoint|so painful|driving me (?:crazy|nuts)|burn(ed)? out|churn",
    r"too confus\w+|gave up|drop[- ]?off|drop(?:ped)? at|never come back|quietly disappear",
    r"花了好几个小时|搞不定|太折腾了|头疼|崩溃|踩坑|浪费",
]
FEATURE_REQUEST_WORDS = [
    r"i wish (?:there was|something)|would pay (?:for|money)|is there a (?:tool|app|service)",
    r"looking for (?:a |an |recommendations?|suggestions?)|any (?:tool|app) (?:that|which)",
    r"recommend(?:ation)?s? for|alternative to|who else needs",
    r"how do you (?:decide|handle|deal)|advice on|what'?s the best way to",
    r"求推荐|有没有工具|想要一个|愿意付费",
]
COMPETITOR_WORDS = [
    r"switched from|just cancelled|moved away from|leaving \w+|vs\.? ",
    r"\w+ is (?:too )?(?:expensive|slow|bloated|cluttered)|cancelled my \w+ subscription",
    r"换掉了|弃用|太贵了|不好用",
]
SHOWCASE_WORDS = [
    r"i (?:built|made|shipped|launched|created)|just (?:shipped|launched|released)",
    r"show (?:r/|me|off)|roast my|feedback (?:on|wanted)|launched on product hunt",
    r"我做了|上线了|求反馈|求围观",
]

# 痛点主题线索：命中后在「痛点线索」列标注主题，供选题聚类。
THEME_WORDS = {
    "定价": r"pricing|expensive|price|pay \w+ per|定价|收费|太贵",
    "上手门槛": r"onboarding|learning curve|steep|setup|confus|上手|配置",
    "集成导出": r"integration|export|import|api limit|sync|集成|导出|同步",
    "性能": r"slow|lag|crash|timeout|latency|卡|慢|崩溃",
    "隐私安全": r"privacy|gdpr|data breach|security|隐私|数据安全",
    "移动端": r"mobile|ios|android|responsive|手机|移动端",
    "协作": r"collaborat|team (?:plan|seat)|sharing|协作|团队席位",
}

# 参与建议（与 Reddit 板规一致）
ACTION = {
    "痛点吐槽": "高价值目标：以「同行+同样遇到」口吻参与讨论，本条不贴任何链接（计入 9 条非自推）",
    "功能求助": "最高价值：给出真实可用的方案或手动做法；若确有产品可解决，先问再提，披露开发者身份",
    "竞品流失": "关注但勿攻击竞品；记录流失原因进竞品档案，2 周内同类原因 ≥3 条则列为选题",
    "自推晒作": "仅 r/SideProject 等 明确允许自推的 sub 发；其余 sub 跳过本帖",
    "闲聊噪音": "不参与，不消耗当日 9:1 配额",
}


def classify(title: str) -> str:
    text = title
    for pat in SHOWCASE_WORDS:
        if re.search(pat, text, re.I):
            return "自推晒作"
    for pat in PAIN_WORDS:
        if re.search(pat, text, re.I):
            return "痛点吐槽"
    for pat in FEATURE_REQUEST_WORDS:
        if re.search(pat, text, re.I):
            return "功能求助"
    for pat in COMPETITOR_WORDS:
        if re.search(pat, text, re.I):
            return "竞品流失"
    return "闲聊噪音"


def heat_score(post: dict) -> tuple[float, str]:
    """热度 = ups + 2×评论数，按新鲜度加权；评论/点赞比 >0.3 判「讨论型」。"""
    ups = float(post.get("ups", 0) or 0)
    n_comments = float(post.get("num_comments", 0) or 0)
    age = float(post.get("age_hours", 48) or 48)
    base = ups + 2 * n_comments
    factor = 1.2 if age <= 24 else (1.0 if age <= 72 else 0.8)
    score = round(base * factor, 1)
    tier = "🔥 热" if score >= 200 else ("🌤 温" if score >= 50 else "❄ 冷")
    if ups > 0 and n_comments / ups > 0.3:
        tier += " · 讨论型"
    return score, tier


def themes(title: str) -> str:
    hits = [t for t, pat in THEME_WORDS.items() if re.search(pat, title, re.I)]
    return "、".join(hits[:3]) if hits else "—"


def build(payload, outdir):
    at.need("openpyxl")
    source = payload.get("source", "未指定")
    window = payload.get("window_days", 7)
    posts = payload.get("posts", [])

    rows = []
    for p in posts:
        title = str(p.get("title", ""))
        cat = classify(title)
        score, tier = heat_score(p)
        rows.append({
            "帖子ID": p.get("id", ""),
            "subreddit": str(p.get("subreddit", "")).replace("r/", ""),
            "标题": title,
            "类别": cat,
            "热度分": score,
            "热度档": tier,
            "点赞": p.get("ups", 0),
            "评论数": p.get("num_comments", 0),
            "帖龄(小时)": p.get("age_hours", 0),
            "痛点主题": themes(title),
            "参与建议": ACTION[cat],
            "URL": p.get("url", ""),
        })
    # 痛点/求助优先展示，热度降序
    order = {"痛点吐槽": 0, "功能求助": 1, "竞品流失": 2, "自推晒作": 3, "闲聊噪音": 4}
    rows.sort(key=lambda r: (order[r["类别"]], -r["热度分"]))

    counts = {}
    for r in rows:
        counts[r["类别"]] = counts.get(r["类别"], 0) + 1

    # 参与决策：按 9:1 核算今日可自推额度
    joinable = [r for r in rows if r["类别"] in ("痛点吐槽", "功能求助")]
    promo_quota = "今日如有 1 条自推需求，需先完成 ≥9 条非自推参与（9:1 规则）"
    summary = {
        "数据来源": source,
        "时间窗口": f"近 {window} 天",
        "帖子总数": len(rows),
        "痛点吐槽": counts.get("痛点吐槽", 0),
        "功能求助": counts.get("功能求助", 0),
        "竞品流失": counts.get("竞品流失", 0),
        "自推晒作": counts.get("自推晒作", 0),
        "闲聊噪音": counts.get("闲聊噪音", 0),
        "可参与目标帖": len(joinable),
        "自推额度核算": promo_quota,
        "高频痛点主题": "、".join(sorted({r["痛点主题"] for r in rows if r["痛点主题"] != "—"})[:5]) or "—",
        "说明": "分类/热度为词表机器判定；动机判断与跟帖话术由模型按 prompt.txt 复核，发帖动作保留人工确认",
    }

    at.ensure_outdir(outdir)
    xlsx = at.write_excel(
        os.path.join(outdir, "热帖洞察清单.xlsx"),
        {
            "洞察明细": rows,
            "参与决策": [
                {"项": "9:1 参与比", "规则": "近 10 条发帖/评论中自推 ≤1 条；未达标前只做非自推参与"},
                {"项": "Sub 差异", "规则": "r/SideProject 允许自推；r/SaaS 须先参与讨论再提及产品；多数 sub 禁直接广告"},
                {"项": "删帖高频原因", "规则": "无上下文裸贴链接 = 最高频删帖原因；链接必须挂在有价值回答之后"},
                {"项": "今日额度", "规则": promo_quota},
            ],
            "汇总": [{"项": k, "内容": str(v)} for k, v in summary.items()],
        },
        highlights={"洞察明细": {"类别": "contains:痛点吐槽", "热度档": "contains:🔥"}},
        widths={"洞察明细": {"标题": 44, "痛点主题": 12, "参与建议": 46, "URL": 22}},
    )
    cats = [k for k in ["痛点吐槽", "功能求助", "竞品流失", "自推晒作", "闲聊噪音"] if counts.get(k)]
    bar = at.bar_chart(
        os.path.join(outdir, "帖子类别分布.png"), cats, [counts[c] for c in cats],
        title=f"社区帖子类别分布（{source}，近 {window} 天）", ylabel="帖子数",
    )
    js = at.write_json({"summary": summary, "items": rows, "generated_at": at.stamp(),
                        "note": "词表机器分类结果；动机与话术由模型按 prompt.txt 复核"},
                       os.path.join(outdir, "insight.json"))
    return {"files": [xlsx, bar, js], "summary": summary, "count": len(rows)}


DEMO = {
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
        {"id": "P011", "subreddit": "r/SaaS", "title": "What's your Sunday routine as a solo founder? (casual)", "ups": 12, "num_comments": 4, "age_hours": 140, "url": "reddit.com/r/SaaS/comments/aa11"},
        {"id": "P012", "subreddit": "r/indiehackers", "title": "Just cancelled my Calendly subscription, moved away from seat-based pricing tools", "ups": 71, "num_comments": 29, "age_hours": 66, "url": "reddit.com/r/indiehackers/comments/aa12"},
    ],
}


def main():
    ap = argparse.ArgumentParser(description="社区热帖洞察 —— 四分类 + 热度分级 + 9:1 参与核算")
    ap.add_argument("--input", help="输入 JSON（source/window_days/posts）")
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--demo", action="store_true", help="用内置样例跑一遍")
    a = ap.parse_args()

    if a.demo:
        payload = DEMO
    elif a.input:
        payload = at.read_json(a.input)
    else:
        ap.error("需要 --input / --demo 之一")

    r = build(payload, a.outdir)
    s = r["summary"]
    print(f"共 {r['count']} 帖 —— 痛点 {s['痛点吐槽']} / 求助 {s['功能求助']} / 竞品 {s['竞品流失']} "
          f"/ 自推 {s['自推晒作']} / 噪音 {s['闲聊噪音']}；可参与 {s['可参与目标帖']} 帖")
    for f in r["files"]:
        print(" 产物:", f)
    at.emit(r)


if __name__ == "__main__":
    main()
