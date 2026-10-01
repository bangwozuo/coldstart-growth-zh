# -*- coding: utf-8 -*-
"""
话题标签优化 —— 标签分层评估 + 组合配比的确定性计算器。

职责边界：本脚本只做**标签分层、竞争度/相关度计算、组合配比与产物生成**（机器强项）。
标签与内容调性的匹配、平台热词的时效判断由模型按 prompt.txt 复核（模型强项）。

用法：
  python tag_score.py --input input.json --outdir out
  python tag_score.py --demo               # 用内置样例跑一遍

产物：
  out/标签组合清单.xlsx   标签评估明细（低相关标红）/ 推荐组合 / 汇总
  out/标签分数分布.png    各标签适配分柱状图
  out/tags.json           机器可读结果（供工作流读取）
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


# ---------------------------------------------------------------- 平台规则
# max_tags: 标签数上限（超上限触达反降）；combo: 大:中:小 配比（在上限内先满足小标签）
PLATFORM_RULES = {
    "X/Twitter":  {"max_tags": 3,  "note": "X 算法下标签弱于正文关键词，>3 个反而压触达"},
    "TikTok":     {"max_tags": 6,  "note": "3-6 个；至少 1 个中小标签否则淹没在热标签流"},
    "小红书":      {"max_tags": 10, "note": "≤10 个；前 3 个决定分发池"},
    "Instagram":  {"max_tags": 5,  "note": "3-5 个精准标签优于 30 个泛标签"},
    "Product Hunt": {"max_tags": 5, "note": "PH 用 topic（非 # 标签），选 3-5 个"},
    "通用":        {"max_tags": 6,  "note": "未识别平台按 3-6 个处理"},
}

# 分层阈值：posts_per_week（周发帖量，来自平台标签页或第三方工具导出）
TIER_RULES = [
    ("大", 5000),   # ≥5000/周：曝光大但单帖被淹没快
    ("中", 500),    # 500-5000/周：性价比区
    ("小", 0),      # <500/周：精准小池，互动率高
]

COMBO_RATIO = {"大": 3, "中": 5, "小": 4}   # 12 标签满配 = 3:5:4

# 上限受限时的配比表（大,中,小）：3-4 个的小上限平台也要保证每层至少 1 个
COMBO_BY_MAX = {3: (1, 1, 1), 4: (1, 2, 1), 5: (1, 2, 2), 6: (1, 3, 2),
                8: (2, 3, 3), 10: (2, 4, 4), 12: (3, 5, 4)}

# 相关性同义词表：标签 token → 内容侧关联词（词表法的标准做法，覆盖范围有限，
# 未覆盖的交给 prefix 兜底与模型复核）
SYNONYMS = {
    "buildinpublic": ["build in public", "building in public", "shipping", "shipped"],
    "launchday": ["launch", "shipped", "launched", "shipping"],
    "microsaas": ["saas"],
    "indiehacker": ["indie", "indie hackers", "bootstrap"],
    "solofounder": ["solo founder", "solo founders", "founder", "opc"],
    "startup": ["founder", "founders", "bootstrap"],
    "devtools": ["tool", "tools", "dev"],
}


def _tokens(s: str) -> set[str]:
    s = s.lower()
    s = re.sub(r"[#_\-\./]", " ", s)
    return {t for t in s.split() if len(t) >= 2}


def relevance(tag: str, content: str) -> float:
    """相关度 = 标签与内容的词面重合（0-1）。
    三级匹配：① 精确 token 重合；② 同义词表（syn 出现在内容中）；③ 长词（≥5 字符）前缀互含。
    0 分 = 与内容词面无关，重罚排除（防 tag stuffing）。"""
    t_tokens = _tokens(tag)
    if not t_tokens:
        return 0.0
    c_tokens = _tokens(content)
    c_low = content.lower()
    hit = 0
    for t in t_tokens:
        if t in c_tokens:
            hit += 1
            continue
        if any(s in c_low for s in SYNONYMS.get(t, [])):
            hit += 1
            continue
        if len(t) >= 5 and any((c.startswith(t) or t.startswith(c)) for c in c_tokens if len(c) >= 5):
            hit += 1
    return round(hit / len(t_tokens), 2)


def tier_of(posts_per_week: float) -> str:
    for name, th in TIER_RULES:
        if posts_per_week >= th:
            return name
    return "小"


def score_tag(tag_row: dict, content: str) -> dict:
    p = float(tag_row.get("posts_per_week", 0) or 0)
    e = float(tag_row.get("avg_engagement", 0) or 0)   # 该标签下单帖平均互动（赞+评+转）
    tier = tier_of(p)
    rel = relevance(tag_row.get("tag", ""), content)
    # 适配分（0-100）：单帖互动为主（minmax 归一，权重 70%），竞争度对数衰减惩罚（30%）
    comp = 1 / (1 + (p / 1000 if p > 0 else 0))        # 0-1，越大竞争越小
    fit = round(0.7 * at.minmax_score(e, 0, 200) + 0.3 * comp * 100, 1)
    if rel == 0:
        fit = round(fit * 0.3, 1)                       # 零相关重罚
    return {
        "标签": tag_row.get("tag", ""),
        "周发帖量": int(p),
        "单帖均互动": e,
        "层级": tier,
        "相关度": rel,
        "适配分": fit,
        "判定": "❌ 低相关·排除" if rel == 0 else ("✅ 进组合" if fit >= 45 else "⚠ 备选"),
    }


def build_combo(evals: list[dict], platform: str) -> list[str]:
    rule = PLATFORM_RULES.get(platform, PLATFORM_RULES["通用"])
    max_tags = rule["max_tags"]
    ok = [e for e in evals if e["相关度"] > 0]
    ratio = COMBO_BY_MAX.get(max_tags, (3, 5, 4))
    combo: list[str] = []
    # 按层配额取高分：大借曝光、中做性价比、小保精准
    for tier, quota in zip(("大", "中", "小"), ratio):
        pool = sorted([e for e in ok if e["层级"] == tier and e["标签"] not in combo],
                      key=lambda x: -x["适配分"])
        combo += [e["标签"] for e in pool[:quota]]
    # 缺档（该层无可用标签）时用剩余高分标签补位至上限
    if len(combo) < max_tags:
        rest = sorted([e for e in ok if e["标签"] not in combo], key=lambda x: -x["适配分"])
        combo += [e["标签"] for e in rest[: max_tags - len(combo)]]
    return combo[:max_tags]


DEMO = {
    "platform": "X/Twitter",
    "content": ("Shipping v2 of my churn analytics SaaS today. Weekly cohort view, "
                "Stripe sync, and a plain-English churn report for solo founders "
                "building in public."),
    "tag_pool": [
        {"tag": "#buildinpublic", "posts_per_week": 8200, "avg_engagement": 96},
        {"tag": "#SaaS", "posts_per_week": 42000, "avg_engagement": 51},
        {"tag": "#indiehacker", "posts_per_week": 1900, "avg_engagement": 88},
        {"tag": "#microsaas", "posts_per_week": 2400, "avg_engagement": 105},
        {"tag": "#solofounder", "posts_per_week": 950, "avg_engagement": 72},
        {"tag": "#churn", "posts_per_week": 380, "avg_engagement": 130},
        {"tag": "#stripe", "posts_per_week": 1500, "avg_engagement": 64},
        {"tag": "#startup", "posts_per_week": 150000, "avg_engagement": 30},
        {"tag": "#devtools", "posts_per_week": 5600, "avg_engagement": 45},
        {"tag": "#cohortanalysis", "posts_per_week": 90, "avg_engagement": 41},
        {"tag": "#coffee", "posts_per_week": 480000, "avg_engagement": 210},
        {"tag": "#launchday", "posts_per_week": 1100, "avg_engagement": 58},
    ],
}


def build(payload, outdir):
    at.need("openpyxl")
    platform = payload.get("platform", "通用")
    content = str(payload.get("content", ""))
    pool = payload.get("tag_pool", [])

    evals = [score_tag(r, content) for r in pool]
    evals.sort(key=lambda x: -x["适配分"])
    combo = build_combo(evals, platform)
    rule = PLATFORM_RULES.get(platform, PLATFORM_RULES["通用"])

    summary = {
        "平台": platform,
        "平台上限": f"{rule['max_tags']} 个（{rule['note']}）",
        "候选标签数": len(pool),
        "低相关排除": sum(1 for e in evals if e["相关度"] == 0),
        "推荐组合": " ".join(combo),
        "组合数": len(combo),
        "配比说明": "大:中:小 ≈ 3:5:4；大标签借曝光、中标签做性价比、小标签保精准互动",
        "说明": "分层/打分为机器计算；标签热度过时快（周级），发布前用平台标签页现值复核",
    }

    at.ensure_outdir(outdir)
    xlsx = at.write_excel(
        os.path.join(outdir, "标签组合清单.xlsx"),
        {
            "标签评估明细": evals,
            "推荐组合": [{"序": i + 1, "标签": t, "层级": next(e["层级"] for e in evals if e["标签"] == t)}
                        for i, t in enumerate(combo)],
            "汇总": [{"项": k, "内容": str(v)} for k, v in summary.items()],
        },
        highlights={"标签评估明细": {"判定": "contains:低相关"}},
        widths={"标签评估明细": {"标签": 20, "判定": 16}},
    )
    chart_tags = [e["标签"] for e in evals[:10]]
    bar = at.bar_chart(
        os.path.join(outdir, "标签分数分布.png"),
        [t.lstrip("#") for t in chart_tags],
        [e["适配分"] for e in evals if e["标签"] in chart_tags],
        title=f"标签适配分 Top10（{platform}）", ylabel="适配分", horizontal=True,
    )
    js = at.write_json({"summary": summary, "combo": combo, "evals": evals,
                        "generated_at": at.stamp(),
                        "note": "机器打分结果；标签时效由模型按 prompt.txt 复核"},
                       os.path.join(outdir, "tags.json"))
    return {"files": [xlsx, bar, js], "summary": summary, "combo": combo}


def main():
    ap = argparse.ArgumentParser(description="话题标签优化 —— 分层评估 + 组合配比")
    ap.add_argument("--input", help="输入 JSON（platform/content/tag_pool）")
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
    print(f"{s['平台']}：候选 {s['候选标签数']} 个，排除低相关 {s['低相关排除']} 个 → "
          f"推荐组合 {s['组合数']} 个：{s['推荐组合']}")
    for f in r["files"]:
        print(" 产物:", f)
    at.emit(r)


if __name__ == "__main__":
    main()
