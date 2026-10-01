# -*- coding: utf-8 -*-
"""
一稿多平台适配流程 —— 端到端编排脚本。

编排逻辑（与 SKILL.md 的 DAG 一致）：
  母稿 → [platform-format-adapt 规则·内置展开] 逐平台规格核对表（上限/结构/调性）
       → [hashtag-optimize] 按平台生成标签组合（调用其脚本 tag_score.py）
       → 一稿多平台适配工单.xlsx（每平台一行：规格 + 标签 + 状态）

失败处理：
  - 上游标签脚本退出码 != 0 → 中止并打印错误（不静默失败）
  - tags.json 缺失/损坏 → 中止并提示重跑
  - 母稿为空 → 中止（无米之炊）
  - 平台未识别 → 按通用规格兜底并标注
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

TAG_SCRIPT = os.path.join(REPO, "skills", "hashtag-optimize", "scripts", "tag_score.py")

# 平台规格矩阵（引自 platform-format-adapt 的规格表，2026-Q3 快照）
PLATFORM_MATRIX = {
    "X/Twitter": {"上限": "单帖 ≤280 字符；thread ≤7 条；标签 ≤3", "结构": "一帖一点，首帖=钩子",
                  "调性": "朋友报信", "自推": "允许"},
    "Reddit r/SideProject": {"上限": "标题 ≤300 字符；正文 150-300 词", "结构": "先信息量后披露身份",
                             "调性": "同事口吻", "自推": "允许（允许自推的 sub）"},
    "Reddit 讨论型 sub": {"上限": "评论 ≤200 词", "结构": "直接回答问题", "调性": "同事口吻",
                          "自推": "禁止（先参与讨论，9:1 达标）"},
    "Product Hunt": {"上限": "tagline ≤60 字符；5 图 + ≤60s demo", "结构": "发布会式 + 首评自述",
                     "调性": "利益直给", "自推": "允许（产品发布场景）"},
    "小红书": {"上限": "标题 ≤20 字；正文 ≤1000 字；标签 ≤10", "结构": "emoji 分段，前 2 行定完读",
               "调性": "闺蜜安利", "自推": "允许（软性）"},
    "Indie Hackers": {"上限": "长文 600-1200 词；标题 ≤60 字符", "结构": "技术细节可保留",
                      "调性": "务实复盘", "自推": "允许（披露身份）"},
}

DEMO_INPUT = {
    "content": ("ChurnLens v0.9 is live: Stripe sync that takes 15 minutes to set up, "
                "weekly cohort views, and plain-English churn reports — no SQL. A user "
                "pulled 3 at-risk users back in week 2. Pricing: 39/mo, first 100 users 29. "
                "Building in public as a solo founder."),
    "platforms": ["X/Twitter", "Product Hunt", "小红书"],
    "tag_pool": [
        {"tag": "#buildinpublic", "posts_per_week": 8200, "avg_engagement": 96},
        {"tag": "#SaaS", "posts_per_week": 42000, "avg_engagement": 51},
        {"tag": "#indiehacker", "posts_per_week": 1900, "avg_engagement": 88},
        {"tag": "#microsaas", "posts_per_week": 2400, "avg_engagement": 105},
        {"tag": "#solofounder", "posts_per_week": 950, "avg_engagement": 72},
        {"tag": "#churn", "posts_per_week": 380, "avg_engagement": 130},
        {"tag": "#stripe", "posts_per_week": 1500, "avg_engagement": 64},
        {"tag": "#startup", "posts_per_week": 150000, "avg_engagement": 30},
        {"tag": "#cohortanalysis", "posts_per_week": 90, "avg_engagement": 41},
        {"tag": "#launchday", "posts_per_week": 1100, "avg_engagement": 58},
    ],
}


def run_tag_script(platform: str, payload: dict, outdir: str) -> dict:
    """步骤 2：调用 hashtag-optimize 脚本，返回该平台 tags.json。"""
    sub_in = os.path.join(outdir, f"_tag_input_{platform.replace('/', '_')}.json")
    at.write_json({"platform": platform, "content": payload["content"],
                   "tag_pool": payload.get("tag_pool", [])}, sub_in)
    r = subprocess.run(
        [sys.executable, TAG_SCRIPT, "--input", sub_in, "--outdir", outdir],
        cwd=FLOW_DIR, capture_output=True, text=True, timeout=180,
    )
    if r.returncode != 0:
        print(f"[失败处理] 上游技能 hashtag-optimize（{platform}）退出码 {r.returncode}，流程中止。", file=sys.stderr)
        print(r.stderr[-800:], file=sys.stderr)
        sys.exit(1)
    js = os.path.join(outdir, "tags.json")
    if not os.path.exists(js):
        print(f"[失败处理] 上游产物 {js} 缺失，流程中止（请重跑上游技能）。", file=sys.stderr)
        sys.exit(1)
    d = at.read_json(js)
    os.replace(js, os.path.join(outdir, f"tags_{platform.replace('/', '_')}.json"))
    return d


def main():
    ap = argparse.ArgumentParser(description="一稿多平台适配流程")
    ap.add_argument("--input", help="输入 JSON（content/platforms/tag_pool）")
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

    content = str(payload.get("content", "")).strip()
    if not content:
        raise SystemExit("[失败处理] 母稿为空：无米之炊，流程中止。")
    platforms = payload.get("platforms", [])
    if not platforms:
        raise SystemExit("[失败处理] platforms 为空：至少指定一个目标平台。")

    # 步骤 1（内置）：逐平台规格核对表（引自 platform-format-adapt 规格矩阵）
    spec_rows = []
    for p in platforms:
        spec = PLATFORM_MATRIX.get(p)
        spec_rows.append({
            "平台": p,
            "上限": spec["上限"] if spec else "未识别平台：按通用规格（3-6 标签）并人工核对官方页面",
            "结构": spec["结构"] if spec else "—",
            "调性": spec["调性"] if spec else "—",
            "自推合规": spec["自推"] if spec else "需人工核对",
            "信息保真": "数字不改写不换算；砍字按 数字>场景>功能>形容词",
        })

    # 步骤 2（上游脚本）：每平台标签组合（hashtag-optimize）
    tag_platforms = [p for p in platforms if p in ("X/Twitter", "TikTok", "小红书", "Instagram", "Product Hunt")]
    tag_rows = []
    for p in tag_platforms:
        d = run_tag_script(p, payload, a.outdir)
        combo = d.get("combo", [])
        tag_rows.append({"平台": p, "标签组合": " ".join(combo) or "（该平台不用 # 标签）",
                         "组合数": len(combo),
                         "排除数": d["summary"].get("低相关排除", 0),
                         "来源": "hashtag-optimize 实跑"})
    used_platforms = {r["平台"] for r in tag_rows}
    for p in platforms:
        if p not in used_platforms:
            tag_rows.append({"平台": p, "标签组合": "（Reddit/长文平台：标签由正文关键词与 flair 承担）",
                             "组合数": 0, "排除数": 0, "来源": "内置规则"})

    summary = {
        "母稿字数": len(content),
        "目标平台数": len(platforms),
        "标签平台数": len(tag_platforms),
        "适配纪律": "同一母稿同源多形：信息点一条不丢一条不编；超标版本不出手",
        "规则快照": "平台规格为 2026-Q3 快照，发布前以官方页面最新公示复核",
        "说明": "规格矩阵引自 platform-format-adapt；标签组合来自 hashtag-optimize 实跑；成稿由模型按其 prompt 完成，发布前人工确认",
    }

    at.ensure_outdir(a.outdir)
    xlsx = at.write_excel(
        os.path.join(a.outdir, "一稿多平台适配工单.xlsx"),
        {
            "平台规格工单": spec_rows,
            "标签组合": tag_rows,
            "汇总": [{"项": k, "内容": str(v)} for k, v in summary.items()],
        },
        highlights={"平台规格工单": {"自推合规": "contains:禁止"}},
        widths={"平台规格工单": {"上限": 34, "结构": 24, "信息保真": 30},
                "标签组合": {"标签组合": 40}},
    )
    js = at.write_json({"summary": summary, "specs": spec_rows, "tags": tag_rows,
                        "generated_at": at.stamp(),
                        "note": "标签为 hashtag-optimize 实跑结果；成稿按 platform-format-adapt 的 prompt 完成"},
                       os.path.join(a.outdir, "multichannel_flow_result.json"))
    print(f"步骤 1  平台规格核对表 ✅（{len(platforms)} 平台）")
    print(f"步骤 2  标签组合 ✅（hashtag-optimize 实跑 {len(tag_platforms)} 平台）")
    print(f"产物    {xlsx}")
    at.emit({"files": [xlsx, js], "summary": summary})


if __name__ == "__main__":
    main()
