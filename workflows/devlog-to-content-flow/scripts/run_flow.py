# -*- coding: utf-8 -*-
"""
开发日志转内容流程 —— 端到端编排脚本。

编排逻辑（与 SKILL.md 的 DAG 一致）：
  开发日志 → [内置] 素材门槛检查（数字溯源 / 绝对词扫描 / 失败细节检查）
          → [内置] 钩子角度工单（按 painpoint-sellingpoint-match 五角度规则）
          → [内置] 五段式叙事工单（按 narrative-rewrite 结构与平台上限）
          → devlog 叙事改写工单.xlsx（人工/模型按工单成稿）

失败处理：
  - devlog 为空 → 中止并提示（无米之炊，不编造）
  - devlog 全部数字无法溯源（metrics 缺失且有数字）→ 标「数字待溯源」不中止，
    工单中该数字标黄提醒，不得直接发布
  - 含绝对化用语 → 判定「回炉」，列出命中词

用法：
  python run_flow.py --input input.json --outdir out
  python run_flow.py --demo
"""
from __future__ import annotations

import argparse
import os
import re
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

# 平台形态上限（与 narrative-rewrite / platform-format-adapt 规格一致）
PLATFORM_SPECS = {
    "X/Twitter": {"形态": "thread 3-7 条", "字数上限": "首帖 ≤280 字符/帖", "钩子位": "首帖"},
    "Reddit r/SideProject": {"形态": "故事帖", "字数上限": "正文 150-300 词", "钩子位": "标题+首段"},
    "Reddit 评论": {"形态": "参与回复", "字数上限": "≤200 词", "钩子位": "首句"},
    "Indie Hackers": {"形态": "长文", "字数上限": "600-1200 词", "钩子位": "开头 2 段"},
    "dev.to": {"形态": "长文", "字数上限": "600-1200 词", "钩子位": "开头 2 段"},
}

FIVE_SECTIONS = ["钩子（含数字/时间/场景细节）", "冲突（用户视角的痛）",
                 "尝试（做了什么+一句为什么）", "结果（真实数字，含没修好的）", "提问（一个具体问题）"]

ANGLE_TABLE = [
    ("痛点瞬间", "用日志里最狼狈的具体时刻开头（凌晨 1 点的报错截图、用户的抱怨原话）"),
    ("前后对比", "日志里的性能/指标变化按原样报（8s→2.1s），不换算不夸大"),
    ("身份共鸣", "把技术困境翻译成「每个 {身份} 都经历过」的处境"),
]

ABSOLUTE_PAT = re.compile(r"最[好强佳优第一快]|第一|100\s*%|百分百|保证|必[定然]")

DEMO_INPUT = {
    "devlog": ("本周重构了缓存层：引入 Redis 做二级缓存，页面平均响应时间从 8s 降到 2.1s，"
               "dashboard 首屏受益最明显。顺便把 CSV 导出改成了队列异步处理。周四凌晨出现一次"
               "缓存击穿把 DB 打满的事故，20 分钟后降级恢复。下周计划做 Webhook 重试机制。"),
    "metrics": {"users": 47, "mrr_cny": 312},
    "platforms": ["X/Twitter", "Reddit r/SideProject", "Indie Hackers"],
}


def extract_numbers(text: str) -> list[str]:
    """抽取日志中的数字（性能/计数/金额等），供溯源检查。"""
    pats = [r"\d+(?:\.\d+)?\s*(?:s|秒|ms|%)", r"\d+(?:\.\d+)?\s*(?:倍|x)",
            r"¥\s?\d+", r"\$\d+(?:\.\d+)?", r"\d+\s*(?:个|位|名|条|次|分钟|小时)"]
    nums = []
    for p in pats:
        nums += re.findall(p, text)
    return sorted(set(nums))


def gate_check(payload: dict) -> list[dict]:
    """步骤 1（内置）：素材门槛检查。"""
    devlog = str(payload.get("devlog", ""))
    rows = []
    # 数字溯源
    nums = extract_numbers(devlog)
    for n in nums:
        rows.append({"检查项": f"数字溯源：{n}", "结果": "✅ 来自日志原文（可用，发布时原样报，不换算）",
                     "处理": ""})
    if not payload.get("metrics"):
        rows.append({"检查项": "metrics 缺失", "结果": "⚠ 数字待溯源（仅可用日志自带数字）",
                     "处理": "成稿不得新增任何数字"})
    # 绝对词
    hits = ABSOLUTE_PAT.findall(devlog)
    rows.append({"检查项": "绝对化用语扫描", "结果": ("✅ 未命中" if not hits else f"❌ 命中：{'、'.join(set(hits))}"),
                 "处理": "命中即回炉，替换为事实表述"})
    # 失败细节
    has_fail = bool(re.search(r"事故|失败|翻车|打满|回滚|降级|崩|没修好|未改善", devlog))
    rows.append({"检查项": "失败细节（build-in-public 交换物）",
                 "结果": "✅ 有（保留进成稿）" if has_fail else "⚠ 无——日志只报喜？确认是否有翻车点可写",
                 "处理": ""})
    # 视角转换素材
    tech_terms = re.findall(r"Redis|队列|缓存|数据库|DB|API|Webhook|并发|缓存击穿", devlog)
    rows.append({"检查项": "术语清单（供视角转换）", "结果": "、".join(sorted(set(tech_terms))) or "—",
                 "处理": "成稿每个术语须带用户侧后果，非必要术语 ≤2 个/百字"})
    return rows


def build(payload, outdir):
    at.need("openpyxl")
    devlog = str(payload.get("devlog", "")).strip()
    platforms = payload.get("platforms", [])
    if not devlog:
        raise SystemExit("[失败处理] devlog 为空：无米之炊，流程中止。请提供开发日志原文，不编造。")

    checks = gate_check(payload)

    # 步骤 2：钩子角度工单（引自 painpoint-sellingpoint-match 五角度中适用于 devlog 的三类）
    angle_rows = [{"角度": a, "怎么用（结合本日志）": hint} for a, hint in ANGLE_TABLE]

    # 步骤 3：五段式叙事工单（引自 narrative-rewrite 结构与平台规格）
    spec_rows = []
    for p in platforms:
        spec = PLATFORM_SPECS.get(p, PLATFORM_SPECS["Reddit r/SideProject"])
        for sec in FIVE_SECTIONS:
            spec_rows.append({"平台": p, "平台形态": spec["形态"], "字数上限": spec["字数上限"],
                              "五段式要素": sec, "钩子位": spec["钩子位"],
                              "完成": "（待成稿后人工勾选）"})
    n_abs = sum(1 for c in checks if "❌" in c["结果"])
    verdict = "❌ 回炉：日志含绝对化用语，替换后再成稿" if n_abs else \
        ("⚠ 可成稿：数字仅限日志自带，不得新增" if not payload.get("metrics") else "✅ 可成稿")
    summary = {
        "平台数": len(platforms),
        "门槛检查项": len(checks),
        "绝对词命中": n_abs,
        "工单结论": verdict,
        "数据诚实规则": "成稿数字全部来自日志原文与 metrics；没有的数字不写； traction 造假 = 社区永久拉黑",
        "说明": "工单为确定性规则产出；成稿由模型按 narrative-rewrite / painpoint-sellingpoint-match 的 prompt 完成，发布前人工确认",
    }

    at.ensure_outdir(outdir)
    xlsx = at.write_excel(
        os.path.join(outdir, "devlog叙事改写工单.xlsx"),
        {
            "门槛检查": checks,
            "钩子角度工单": angle_rows,
            "五段式叙事工单": spec_rows,
            "汇总": [{"项": k, "内容": str(v)} for k, v in summary.items()],
        },
        highlights={"门槛检查": {"结果": "contains:❌"}, "五段式叙事工单": {"字数上限": "contains:280"}},
        widths={"门槛检查": {"检查项": 34, "结果": 44, "处理": 26},
                "五段式叙事工单": {"五段式要素": 30}},
    )
    js = at.write_json({"summary": summary, "checks": checks, "angles": angle_rows,
                        "platform_specs": spec_rows, "generated_at": at.stamp(),
                        "note": "工单不含成稿正文；成稿按两个原子技能的 prompt 完成"},
                       os.path.join(outdir, "devlog_flow_result.json"))
    print(f"步骤 1  素材门槛检查 ✅（绝对词 {n_abs} 处）")
    print(f"步骤 2  钩子角度工单   ✅（{len(angle_rows)} 角度）")
    print(f"步骤 3  五段式叙事工单 ✅（{len(platforms)} 平台 × 5 要素）")
    print(f"结论    {verdict}")
    at.emit({"files": [xlsx, js], "summary": summary})


def main():
    ap = argparse.ArgumentParser(description="开发日志转内容流程")
    ap.add_argument("--input", help="输入 JSON（devlog/metrics/platforms）")
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()

    if a.demo:
        payload = DEMO_INPUT
    elif a.input:
        payload = at.read_json(a.input)
    else:
        ap.error("需要 --input / --demo 之一")

    build(payload, a.outdir)


if __name__ == "__main__":
    main()
