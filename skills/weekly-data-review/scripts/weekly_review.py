# -*- coding: utf-8 -*-
"""
周度数据复盘 —— 渠道归因 + 漏斗基准体检 + CAC/LTV 判定的确定性计算器。

职责边界：本脚本只做**漏斗各级转化率计算、基准比对、CAC<LTV/3 判定与产物生成**
（机器强项）。归因口径的合理性判断、下周投入的取舍权衡由模型按 prompt.txt 完成
（模型强项）。

基准（出海冷启动漏斗，行业通行的下限-上限区间）：
  曝光→点击 CTR 2-5% | 落地页→注册 8-15% | 注册→激活（完成关键动作）20-40%
  低于下限 = 该段漏斗有问题，先修漏斗，不加投放。

用法：
  python weekly_review.py --input input.json --outdir out
  python weekly_review.py --demo

产物：
  out/周度复盘报告.xlsx   渠道明细（破线项标红）/ 漏斗体检 / 下周行动 / 汇总
  out/渠道漏斗对比.png    各渠道 注册→激活 率柱状图
  out/review.json         机器可读结果（供工作流读取）
"""
from __future__ import annotations

import argparse
import os
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


# ---------------------------------------------------------------- 基准
FUNNEL_BENCH = [
    ("CTR（曝光→点击）", "ctr", 0.02, 0.05, "检查曝光质量：低于 2% 说明素材/标题与人群错配"),
    ("落地页→注册", "lp_cr", 0.08, 0.15, "低于 8% 先修落地页（首屏承诺/加载速度/表单长度），不加投放"),
    ("注册→激活", "act_cr", 0.20, 0.40, "低于 20% 说明 onboarding 或关键动作设计有问题，先修产品不是加渠道"),
]

DEMO = {
    "week": "2026-W40",
    "ltv": 540,
    "channels": [
        {"name": "Product Hunt Launch", "spend": 0, "impressions": 8000, "clicks": 505, "signups": 82, "activated": 21, "paying": 9, "revenue": 1890},
        {"name": "Reddit r/SideProject", "spend": 0, "impressions": 12000, "clicks": 300, "signups": 21, "activated": 4, "paying": 1, "revenue": 89},
        {"name": "X buildinpublic", "spend": 60, "impressions": 30000, "clicks": 600, "signups": 54, "activated": 16, "paying": 5, "revenue": 745},
        {"name": "付费投放（测试）", "spend": 900, "impressions": 50000, "clicks": 1500, "signups": 96, "activated": 17, "paying": 4, "revenue": 320},
        {"name": "SEO 博客（自然）", "spend": 120, "impressions": 3500, "clicks": 220, "signups": 30, "activated": 11, "paying": 6, "revenue": 1120},
    ],
}


def _pct(a: float, b: float):
    return round(a / b * 100, 1) if b else None


def review_channel(ch: dict, ltv: float) -> dict:
    spend = float(ch.get("spend", 0) or 0)
    paying = float(ch.get("paying", 0) or 0)
    cac = round(spend / paying, 1) if paying > 0 else None
    m = {
        "渠道": ch.get("name", ""),
        "花费¥": spend,
        "曝光": ch.get("impressions", 0),
        "点击": ch.get("clicks", 0),
        "注册": ch.get("signups", 0),
        "激活": ch.get("activated", 0),
        "付费": int(paying),
        "收入¥": ch.get("revenue", 0),
        "CTR%": _pct(ch.get("clicks", 0), ch.get("impressions", 0)),
        "落地页→注册%": _pct(ch.get("signups", 0), ch.get("clicks", 0)),
        "注册→激活%": _pct(ch.get("activated", 0), ch.get("signups", 0)),
        "注册→付费%": _pct(paying, ch.get("signups", 0)),
        "CAC¥": cac if cac is not None else "∞（0 付费）",
        "ROAS": round(ch.get("revenue", 0) / spend, 2) if spend else "—",
    }
    # 漏斗体检
    flags = []
    vals = {"ctr": m["CTR%"], "lp_cr": m["落地页→注册%"], "act_cr": m["注册→激活%"]}
    for label, key, lo, hi, advice in FUNNEL_BENCH:
        v = vals[key]
        if v is None:
            continue
        if v < lo * 100:
            flags.append(f"⚠ {label} {v}% < 下限 {lo*100:g}%：{advice}")
        elif v > hi * 100:
            flags.append(f"ℹ {label} {v}% > 上限 {hi*100:g}%：核实流量真实性/统计口径")
    m["漏斗体检"] = "；".join(flags) if flags else "✅ 各段均在基准区间"

    # 渠道判定：CAC < LTV/3 保留，否则停/减
    third = ltv / 3
    if spend == 0:
        verdict = "✅ 自然渠道：CAC=0，持续投入并沉淀为常青内容"
        m["_cac_num"] = 0
    elif cac is None:
        verdict = f"🛑 暂停：有花费 0 付费，CAC 无法摊薄（试错预算上限 ¥300/次已超）" if spend > 300 \
            else "🛑 暂停：有花费 0 付费，先修转化再复测"
        m["_cac_num"] = 99999
    elif cac < third:
        verdict = f"✅ 保留/加码：CAC ¥{cac} < LTV/3（¥{third:g}）"
        m["_cac_num"] = cac
    else:
        verdict = f"🛑 停投：CAC ¥{cac} ≥ LTV/3（¥{third:g}）"
        m["_cac_num"] = cac
    m["判定"] = verdict
    return m


def build(payload, outdir):
    at.need("openpyxl")
    week = payload.get("week", "")
    ltv = float(payload.get("ltv", 0) or 0)
    channels = payload.get("channels", [])
    if ltv <= 0:
        raise SystemExit("[失败处理] ltv 缺失或非正数：CAC<LTV/3 判定无法执行。"
                         "请在输入中补充 LTV（可用「人均收入×平均留存月数」估算，估算值须注明口径），不猜默认值。")

    rows = [review_channel(ch, ltv) for ch in channels]
    rows.sort(key=lambda r: (r["_cac_num"], -float(r["收入¥"] or 0)))

    tot_spend = sum(float(c.get("spend", 0) or 0) for c in channels)
    tot_paying = sum(float(c.get("paying", 0) or 0) for c in channels)
    tot_rev = sum(float(c.get("revenue", 0) or 0) for c in channels)
    tot_clicks = sum(c.get("clicks", 0) for c in channels)
    tot_signups = sum(c.get("signups", 0) for c in channels)
    tot_act = sum(c.get("activated", 0) for c in channels)
    keep = [r for r in rows if r["判定"].startswith("✅")]
    third = ltv / 3

    funnel_rows = []
    for label, key, lo, hi, advice in FUNNEL_BENCH:
        funnel_rows.append({
            "漏斗段": label, "基准下限%": lo * 100, "基准上限%": hi * 100,
            "全渠道整体%": {"ctr": _pct(tot_clicks, sum(c.get("impressions", 0) for c in channels)),
                            "lp_cr": _pct(tot_signups, tot_clicks),
                            "act_cr": _pct(tot_act, tot_signups)}[key],
            "低于下限的处理原则": advice,
        })

    actions = [{"#": i + 1, "渠道": r["渠道"], "行动": r["判定"],
                "下周预算": ("维持自然投入" if r["花费¥"] == 0 else
                             (f"可加码（CAC ¥{r['CAC¥']} 达标）" if str(r["判定"]).startswith("✅") and r["花费¥"] else "停投，预算转给达标渠道"))}
               for i, r in enumerate(rows)]

    summary = {
        "复盘周": week,
        "LTV 假设": f"¥{ltv:g}（CAC 判定线 = LTV/3 = ¥{third:g}）",
        "渠道数": len(rows),
        "总花费¥": tot_spend,
        "总收入¥": tot_rev,
        "整体 CAC¥": round(tot_spend / tot_paying, 1) if tot_paying else "∞（0 付费）",
        "保留渠道": "、".join(r["渠道"] for r in keep) or "无",
        "停投渠道": "、".join(r["渠道"] for r in rows if r["判定"].startswith("🛑")) or "无",
        "试错纪律": "单渠道试错预算上限 ¥300/次；低于下限先修漏斗，不加投放",
        "说明": "转化率/CAC 为脚本计算；归因口径（UTM/引荐域）与取舍权衡由模型按 prompt.txt 复核",
    }

    at.ensure_outdir(outdir)
    xlsx = at.write_excel(
        os.path.join(outdir, "周度复盘报告.xlsx"),
        {
            "渠道明细": rows,
            "漏斗体检": funnel_rows,
            "下周行动": actions,
            "汇总": [{"项": k, "内容": str(v)} for k, v in summary.items()],
        },
        highlights={"渠道明细": {"判定": "contains:🛑", "漏斗体检": "contains:⚠"}},
        widths={"渠道明细": {"渠道": 20, "漏斗体检": 48, "判定": 40},
                "漏斗体检": {"低于下限的处理原则": 50}},
    )
    bar = at.bar_chart(
        os.path.join(outdir, "渠道漏斗对比.png"),
        [r["渠道"] for r in rows],
        [r["注册→激活%"] or 0 for r in rows],
        title=f"各渠道 注册→激活率 vs 基准 20-40%（{week}）", ylabel="%",
    )
    js = at.write_json({"summary": summary, "channels": rows, "funnel_check": funnel_rows,
                        "actions": actions, "generated_at": at.stamp(),
                        "note": "机器计算结果；归因口径与投入取舍由模型按 prompt.txt 复核"},
                       os.path.join(outdir, "review.json"))
    return {"files": [xlsx, bar, js], "summary": summary, "count": len(rows)}


def main():
    ap = argparse.ArgumentParser(description="周度数据复盘 —— 渠道归因 + 漏斗体检 + CAC 判定")
    ap.add_argument("--input", help="输入 JSON（week/ltv/channels）")
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
    print(f"{s['复盘周']}：保留 {s['保留渠道'] or '无'} / 停投 {s['停投渠道'] or '无'}；"
          f"整体 CAC ¥{s['整体 CAC¥']}")
    for f in r["files"]:
        print(" 产物:", f)
    at.emit(r)


if __name__ == "__main__":
    main()
