# -*- coding: utf-8 -*-
"""
数据驱动选题迭代流程 —— 端到端编排脚本。

编排逻辑（与 SKILL.md 的 DAG 一致）：
  本周渠道数据 → [weekly-data-review] 渠道归因 + 漏斗体检 + CAC<LTV/3 判定
              → [内置] 选题权重更新（在跑选题按渠道判定加权/降权/转向）
              → [内置] 下周选题计划（保留渠道加倍、停投渠道转向、破段先修漏斗）
              → 复盘与选题迭代清单.xlsx + topic_iterate_result.json

失败处理：
  - 上游复盘脚本退出码 != 0 → 中止并打印错误（不静默失败）
  - review.json 缺失/损坏 → 中止并提示重跑上游
  - 在跑选题为空 → 输出「无在跑选题」占位并正常退出
  - 周注册 <30 的渠道 → 选题判定标「样本不足」，只报值不下结论
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

REVIEW_SCRIPT = os.path.join(REPO, "skills", "weekly-data-review", "scripts", "weekly_review.py")

DEMO_INPUT = {
    "week": "2026-W40",
    "ltv": 540,
    "channels": [
        {"name": "Product Hunt Launch", "spend": 0, "impressions": 8000, "clicks": 505, "signups": 82, "activated": 21, "paying": 9, "revenue": 1890},
        {"name": "Reddit r/SideProject", "spend": 0, "impressions": 12000, "clicks": 300, "signups": 21, "activated": 4, "paying": 1, "revenue": 89},
        {"name": "X buildinpublic", "spend": 60, "impressions": 30000, "clicks": 600, "signups": 54, "activated": 16, "paying": 5, "revenue": 745},
        {"name": "付费投放（测试）", "spend": 900, "impressions": 50000, "clicks": 1500, "signups": 96, "activated": 17, "paying": 4, "revenue": 320},
        {"name": "SEO 博客（自然）", "spend": 120, "impressions": 3500, "clicks": 220, "signups": 30, "activated": 11, "paying": 6, "revenue": 1120},
    ],
    "active_topics": [
        {"topic": "churn 分析实战（PH 发布配套）", "channel": "Product Hunt Launch", "week_signups": 82},
        {"topic": "缓存重构 devlog 系列", "channel": "X buildinpublic", "week_signups": 54},
        {"topic": "付费投放素材组 A/B", "channel": "付费投放（测试）", "week_signups": 96},
        {"topic": "Stripe 对账教程（SEO）", "channel": "SEO 博客（自然）", "week_signups": 30},
        {"topic": "webhook 配置踩坑帖", "channel": "Reddit r/SideProject", "week_signups": 21},
    ],
}


def run_upstream(payload_path: str, outdir: str) -> str:
    """步骤 1：调用 weekly-data-review 脚本，返回其 JSON 产物路径。"""
    r = subprocess.run(
        [sys.executable, REVIEW_SCRIPT, "--input", payload_path, "--outdir", outdir],
        cwd=FLOW_DIR, capture_output=True, text=True, timeout=180,
    )
    if r.returncode != 0:
        print(f"[失败处理] 上游技能 weekly-data-review 退出码 {r.returncode}，流程中止。", file=sys.stderr)
        print(r.stderr[-800:], file=sys.stderr)
        sys.exit(1)
    js = os.path.join(outdir, "review.json")
    if not os.path.exists(js):
        print(f"[失败处理] 上游产物 {js} 缺失，流程中止（请重跑上游技能）。", file=sys.stderr)
        sys.exit(1)
    return js


def iterate_topics(review: dict, active_topics: list[dict]) -> tuple[list[dict], list[dict]]:
    """步骤 2（内置）：按渠道判定更新选题权重。返回（权重表, 下周计划）。"""
    verdict_by_channel = {c["渠道"]: c["判定"] for c in review.get("channels", [])}
    broken = {c["渠道"] for c in review.get("channels", []) if "⚠" in c.get("漏斗体检", "")}
    weight_rows, plan_rows = [], []
    for t in active_topics:
        topic, channel = t.get("topic", ""), t.get("channel", "")
        verdict = verdict_by_channel.get(channel, "（渠道本周无数据）")
        signups = t.get("week_signups", 0)
        if "拒绝" in verdict or "停投" in verdict:
            weight, action = "↓ 降权", f"选题转向：本周该渠道判停投/拒绝，「{topic}」迁移到保留渠道重写"
        elif channel in broken:
            weight, action = "→ 暂缓", f"先修漏斗：{channel} 转化破基准段，选题照跑但预算不加，修完复测"
        elif "保留" in verdict or "自然渠道" in verdict:
            weight = "↑ 加权"
            action = f"加倍：「{topic}」系列化（本周 {signups} 注册），拆成 2-3 个子题连载"
        else:
            weight, action = "→ 观察", "样本不足或无数据：只报值不下结论，再观察 1 周"
        if signups < 30:
            action += "（周注册 <30，样本不足，判定降级为参考）"
        weight_rows.append({"选题": topic, "渠道": channel, "本周注册": signups,
                            "渠道判定": verdict, "权重": weight, "依据": action})
        plan_rows.append({"下周动作": action, "选题": topic, "渠道": channel,
                          "衔接": "新选题交 daily-topic-mine-flow 证据链校验后进入 devlog-to-content-flow"})
    order = {"↑ 加权": 0, "→ 暂缓": 1, "→ 观察": 2, "↓ 降权": 3}
    weight_rows.sort(key=lambda r: order.get(r["权重"], 9))
    return weight_rows, plan_rows


def main():
    ap = argparse.ArgumentParser(description="数据驱动选题迭代流程")
    ap.add_argument("--input", help="输入 JSON（week/ltv/channels/active_topics）")
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

    # 步骤 1：上游渠道归因 + 漏斗体检 + CAC 判定
    review_js = run_upstream(payload_path, a.outdir)
    review = at.read_json(review_js)

    # 步骤 2/3（内置）：选题权重更新 + 下周计划
    active = payload.get("active_topics", [])
    weight_rows, plan_rows = iterate_topics(review, active)

    s = review["summary"]
    summary = {
        "复盘周": s.get("复盘周", ""),
        "保留渠道": s.get("保留渠道", ""),
        "停投渠道": s.get("停投渠道", ""),
        "整体 CAC": s.get("整体 CAC¥", ""),
        "在跑选题数": len(active),
        "加权 / 暂缓 / 降权": " / ".join(str(sum(1 for r in weight_rows if w in r["权重"]))
                                          for w in ("↑", "→", "↓")),
        "迭代纪律": "连续 2 周加权的主题进入常青选题库；连续 2 周降权的主题关闭",
        "说明": "渠道判定为 weekly-data-review 脚本产物；选题权重更新为确定性规则；取舍权衡由模型按 prompt.txt 复核",
    }

    at.ensure_outdir(a.outdir)
    xlsx = at.write_excel(
        os.path.join(a.outdir, "复盘与选题迭代清单.xlsx"),
        {
            "渠道判定（上游）": review.get("channels", []),
            "选题权重更新": weight_rows or [{"选题": "（无在跑选题）", "渠道": "", "本周注册": 0,
                                              "渠道判定": "", "权重": "", "依据": ""}],
            "下周选题计划": plan_rows or [{"下周动作": "（无在跑选题，先跑 daily-topic-mine-flow 挖新题）",
                                            "选题": "", "渠道": "", "衔接": ""}],
            "汇总": [{"项": k, "内容": str(v)} for k, v in summary.items()],
        },
        highlights={"选题权重更新": {"权重": "contains:↓"},
                    "渠道判定（上游）": {"判定": "contains:🛑"}},
        widths={"选题权重更新": {"选题": 30, "依据": 52},
                "下周选题计划": {"下周动作": 52, "衔接": 40}},
    )
    js = at.write_json({"summary": summary, "weights": weight_rows, "plan": plan_rows,
                        "review_summary": s, "generated_at": at.stamp(),
                        "note": "渠道判定来自上游 review.json；权重更新规则确定性执行"},
                       os.path.join(a.outdir, "topic_iterate_result.json"))
    print(f"步骤 1  weekly-data-review  ✅  → {review_js}")
    print(f"步骤 2  选题权重更新     ✅（{len(weight_rows)} 个在跑选题）")
    print(f"步骤 3  下周选题计划     ✅")
    print(f"汇总    保留 {s.get('保留渠道', '') and len(s.get('保留渠道', '').split('、'))} 渠道 / "
          f"停投 {s.get('停投渠道') or '无'}；加权 {summary['加权 / 暂缓 / 降权']}")
    at.emit({"files": [xlsx, js], "summary": summary})


if __name__ == "__main__":
    main()
