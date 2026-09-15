#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2 图表骨架 · 数据→几何重算器（T-A1 Part B）

关闭 `deltas/layout-assets/v2/CONTRACT.md` §2.6 的手工坐标风险。

覆盖 v2 的 4 类图表骨架，**按 v2/CONTRACT.md §2 的公式**重算几何：
  · bar-chart       柱高 = 值/nice_max×290；柱宽 130；x 起点 190/420/650/880
  · line-chart      点x = 160 + i/(n-1)×960；点y = 500 - 值/max×300
  · donut-chart     每段 stroke-dasharray = 占比×C（C=2π×160≈1005）
  · comparison-bars 条长 = 值/max×最大可用长度（800）；起点 x=360，条高 34

**视觉对齐**：完全复用 v2 骨架的几何常量与语义色（`#002FA7` / `#4A6FD4` / `#E2E8F0` /
`#0A0A0A` / `#737373`），使生成结果与手写骨架**逐像素同构**（同数据时）。

与 `fill_chart.py` 的分工：
  · `fill_chart.py`  → base `templates/charts/` 契约（带原生 chart 标记、轴与刻度）
  · `v2_chart_gen.py` → 仓库 `deltas/layout-assets/v2/` 骨架契约（无轴、极简、IKB 蓝）
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

# ---------------------------------------------------------------------------
# v2 视觉常量（严格照抄 v2 骨架）
# ---------------------------------------------------------------------------
W, H = 1280, 720
FONT = "Microsoft YaHei, Arial, sans-serif"

INK = "#0A0A0A"        # 主文字
INK_2 = "#737373"      # 次级文字
RULE = "#E2E8F0"       # 基线 / 轴
PRIMARY = "#002FA7"    # 主色（IKB）
PRIMARY_2 = "#4A6FD4"  # 同色系浅一档（donut 次段）

# bar-chart
BAR_BASE_Y = 500
BAR_MAX_H = 290
BAR_W = 130
BAR_X = [190, 420, 650, 880]
BAR_VALUE_DY = 18      # 数值标签在柱顶上方
CAT_BASE_Y = 546       # 类目名基线

# line-chart
LINE_X0, LINE_X1 = 160, 1120
LINE_BASE_Y = 500
LINE_TOP_Y = 200
LINE_MAX_H = 300
LINE_CAT_Y = 520
LINE_VAL_DY = 24

# donut-chart
DONUT_CX, DONUT_CY, DONUT_R, DONUT_SW = 360, 380, 160, 56
DONUT_C = 2 * math.pi * DONUT_R          # ≈1005.3

# comparison-bars
CB_BAR_X = 360
CB_BAR_H = 34
CB_ROW_Y = [216, 316, 416]
CB_MAX_W = 800
CB_AXIS_Y = 180
CB_AXIS_H = 300
CB_NAME_Y_OFF = 24
CB_VAL_X = 1180

NOTE_Y = 640
NOTE_BOUNDS_Y = 590


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def nice_max(v: float) -> float:
    """把最大值上取整到好看的刻度（与 fill_chart.py 同口径）。"""
    if v <= 0:
        return 1.0
    exp = math.floor(math.log10(v))
    base = 10.0 ** exp
    for m in (1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if v <= m * base + 1e-9:
            return m * base
    return 10.0 * base


def fmt(v) -> str:
    if isinstance(v, str):
        return v
    if abs(v - round(v)) < 1e-9:
        return f"{int(round(v)):,}"
    return f"{v:,.1f}"


def _page_open(title: str) -> list:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}"',
        f'     data-pptx-page-role="content" font-family="{FONT}">',
        '  <g id="page-bg" data-pptx-bounds="0 0 1280 720">',
        '    <rect width="1280" height="720" fill="#FFFFFF"/>',
        '  </g>',
        '  <g id="page-title" data-pptx-bounds="80 40 1120 100">',
        f'    <text x="80" y="90" font-size="40" font-weight="700" '
        f'fill="{INK}">{esc(title)}</text>',
        f'    <rect x="80" y="112" width="80" height="4" fill="{PRIMARY}"/>',
        '  </g>',
    ]


def _note_block(note: str, gid: str) -> list:
    if not note:
        return []
    return [
        f'  <g id="{gid}" data-pptx-bounds="120 {NOTE_BOUNDS_Y} 1080 90">',
        f'    <text x="120" y="{NOTE_Y}" font-size="18" '
        f'fill="{INK_2}">{esc(note)}</text>',
        '  </g>',
    ]


# ---------------------------------------------------------------------------
# 1) bar-chart
# ---------------------------------------------------------------------------

def gen_bar_chart(spec: dict) -> str:
    cats = spec["categories"]
    values = spec["values"]
    values_fmt = spec.get("value_labels", [fmt(v) for v in values])
    n = len(cats)
    if n > len(BAR_X):
        raise ValueError(f"bar-chart 最多 {len(BAR_X)} 根柱，收到 {n}")
    mx = nice_max(max(values)) if spec.get("auto_max", False) else max(values)

    out = _page_open(spec["title"])
    out.append('  <g id="bar-plot" data-pptx-bounds="120 160 1080 400">')
    out.append(f'    <rect x="120" y="{BAR_BASE_Y}" width="1080" height="2" '
               f'fill="{RULE}"/>')
    for i, (cat, val, lab) in enumerate(zip(cats, values, values_fmt)):
        h = round(val / mx * BAR_MAX_H)
        x = BAR_X[i]
        y = BAR_BASE_Y - h
        cx = x + BAR_W / 2
        out.append(f'    <rect x="{x}" y="{y}" width="{BAR_W}" height="{h}" '
                   f'fill="{PRIMARY}"/>')
        out.append(f'    <text x="{cx:.0f}" y="{y - BAR_VALUE_DY}" font-size="28" '
                   f'font-weight="700" fill="{PRIMARY}" text-anchor="middle">'
                   f'{esc(lab)}</text>')
        out.append(f'    <text x="{cx:.0f}" y="{CAT_BASE_Y}" font-size="22" '
                   f'font-weight="600" fill="{INK}" text-anchor="middle">'
                   f'{esc(cat)}</text>')
    out.append('  </g>')
    out += _note_block(spec.get("note", ""), "bar-note")
    out.append('</svg>')
    out.append('')
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 2) line-chart
# ---------------------------------------------------------------------------

def gen_line_chart(spec: dict) -> str:
    cats = spec["categories"]
    values = spec["values"]
    values_fmt = spec.get("value_labels", [fmt(v) for v in values])
    n = len(cats)
    if n < 2:
        raise ValueError("line-chart 至少需要 2 个点")
    mx = nice_max(max(values)) if spec.get("auto_max", False) else max(values)

    pts = []
    for i, v in enumerate(values):
        x = LINE_X0 + (i / (n - 1)) * (LINE_X1 - LINE_X0)
        y = LINE_BASE_Y - (v / mx) * LINE_MAX_H
        pts.append((x, y))

    out = _page_open(spec["title"])
    out.append('  <g id="line-plot" data-pptx-bounds="110 150 1060 400">')
    out.append(f'    <rect x="{LINE_X0}" y="{LINE_BASE_Y}" width="960" height="2" '
               f'fill="{RULE}"/>')
    out.append(f'    <rect x="{LINE_X0}" y="{LINE_TOP_Y}" width="2" '
               f'height="{LINE_BASE_Y - LINE_TOP_Y}" fill="{RULE}"/>')
    poly = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)
    out.append(f'    <polyline points="{poly}" fill="none" stroke="{PRIMARY}" '
               f'stroke-width="4"/>')
    for x, y in pts:
        out.append(f'    <circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="{PRIMARY}"/>')
    for i, cat in enumerate(cats):
        x, y = pts[i]
        out.append(f'    <text x="{x:.0f}" y="{LINE_CAT_Y}" font-size="22" '
                   f'font-weight="600" fill="{INK}" text-anchor="middle">'
                   f'{esc(cat)}</text>')
        # 末点标签右对齐、首点左对齐，避免超出 canvas 触发 checker
        anchor = "end" if i == n - 1 else ("start" if i == 0 else "middle")
        out.append(f'    <text x="{x:.0f}" y="{y - LINE_VAL_DY:.0f}" font-size="24" '
                   f'font-weight="700" fill="{PRIMARY}" text-anchor="{anchor}">'
                   f'{esc(values_fmt[i])}</text>')
    out.append('  </g>')
    out += _note_block(spec.get("note", ""), "line-note")
    out.append('</svg>')
    out.append('')
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 3) donut-chart
# ---------------------------------------------------------------------------

def gen_donut_chart(spec: dict) -> str:
    segs = spec["segments"]        # [{name, value, label?}]
    if len(segs) > 4:
        raise ValueError("donut-chart ≤4 段（v2 契约 §2.3）")
    total = sum(s["value"] for s in segs)
    if total <= 0:
        raise ValueError("donut 总值必须 > 0")
    colors = [PRIMARY, PRIMARY_2, "#002FA7", "#4A6FD4"]

    out = _page_open(spec["title"])
    out.append('  <g id="donut-plot" data-pptx-bounds="140 180 460 400">')
    out.append(f'    <circle cx="{DONUT_CX}" cy="{DONUT_CY}" r="{DONUT_R}" '
               f'fill="none" stroke="{RULE}" stroke-width="{DONUT_SW}"/>')
    acc = 0.0
    for i, s in enumerate(segs):
        frac = s["value"] / total
        dash = frac * DONUT_C
        # 累加角度：首段从 12 点方向起，后续段按累计占比旋转
        angle = -90 + (acc / total) * 360
        # 角度格式化：整数去掉小数（与手写骨架 `-90` 写法一致，便于逐项比对）
        ang_s = (f"{angle:.0f}" if abs(angle - round(angle)) < 1e-9
                 else f"{angle:.2f}")
        out.append(f'    <circle cx="{DONUT_CX}" cy="{DONUT_CY}" r="{DONUT_R}" '
                   f'fill="none" stroke="{colors[i % len(colors)]}" '
                   f'stroke-width="{DONUT_SW}" '
                   f'stroke-dasharray="{dash:.0f} {DONUT_C:.0f}" '
                   f'transform="rotate({ang_s} {DONUT_CX} {DONUT_CY})"/>')
        acc += s["value"]
    out.append(f'    <text x="{DONUT_CX}" y="368" font-size="56" font-weight="700" '
               f'fill="{INK}" text-anchor="middle">{esc(spec.get("center_value",""))}</text>')
    out.append(f'    <text x="{DONUT_CX}" y="410" font-size="20" font-weight="600" '
               f'fill="{INK_2}" text-anchor="middle">{esc(spec.get("center_label",""))}</text>')
    out.append('  </g>')

    out.append('  <g id="donut-legend" data-pptx-bounds="660 240 520 280">')
    for i, s in enumerate(segs):
        y = 250 + i * 110
        out.append(f'    <rect x="660" y="{y}" width="20" height="20" '
                   f'fill="{colors[i % len(colors)]}"/>')
        out.append(f'    <text x="700" y="{y + 18}" font-size="24" font-weight="600" '
                   f'fill="{INK}">{esc(s["name"])}</text>')
        out.append(f'    <text x="700" y="{y + 50}" font-size="18" '
                   f'fill="{INK_2}">{esc(s.get("label", fmt(s["value"])))}</text>')
    out.append('  </g>')
    out += _note_block(spec.get("note", ""), "donut-note")
    out.append('</svg>')
    out.append('')
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 4) comparison-bars
# ---------------------------------------------------------------------------

def gen_comparison_bars(spec: dict) -> str:
    items = spec["items"]          # [{name, value, label?}]，条长按 value/max
    if len(items) > len(CB_ROW_Y):
        raise ValueError(f"comparison-bars ≤{len(CB_ROW_Y)} 项（v2 契约 §2.4）")
    mx = max(i["value"] for i in items) or 1

    out = _page_open(spec["title"])
    out.append('  <g id="compare-bars" data-pptx-bounds="120 180 1080 400">')
    for i, it in enumerate(items):
        y = CB_ROW_Y[i]
        w = round(it["value"] / mx * CB_MAX_W)
        out.append(f'    <text x="120" y="{y + CB_NAME_Y_OFF}" font-size="24" '
                   f'font-weight="600" fill="{INK}">{esc(it["name"])}</text>')
        out.append(f'    <rect x="{CB_BAR_X}" y="{y}" width="{w}" '
                   f'height="{CB_BAR_H}" fill="{PRIMARY}"/>')
        out.append(f'    <text x="{CB_VAL_X}" y="{y + CB_NAME_Y_OFF}" font-size="24" '
                   f'font-weight="700" fill="{PRIMARY}" text-anchor="end">'
                   f'{esc(it.get("label", fmt(it["value"])))}</text>')
    out.append(f'    <rect x="{CB_BAR_X}" y="{CB_AXIS_Y}" width="2" '
               f'height="{CB_AXIS_H}" fill="{RULE}"/>')
    out.append('  </g>')
    out += _note_block(spec.get("note", ""), "compare-note")
    out.append('</svg>')
    out.append('')
    return "\n".join(out)


GENERATORS = {
    "bar-chart": gen_bar_chart,
    "line-chart": gen_line_chart,
    "donut-chart": gen_donut_chart,
    "comparison-bars": gen_comparison_bars,
}


# ---------------------------------------------------------------------------
# v2 契约 §2 记录的同源数据（用于"生成版 vs 手写版"对比）
# ---------------------------------------------------------------------------

DEMO = {
    "bar-chart": {
        "title": "预算四项构成对比",
        "categories": ["软件许可", "实施集成", "硬件存储", "培训预备"],
        "values": [40, 20, 12, 8],
        "value_labels": ["40 万", "20 万", "12 万", "8 万"],
        "note": "四项合计八十万元，均为一次性投入",
    },
    "line-chart": {
        "title": "投入与年节省的趋势对照",
        "categories": ["投入", "第一年", "第二年"],
        "values": [80, 35, 10],
        "value_labels": ["80 万", "35 万", "10 万"],
        "note": "净投入随节省逐年回落，约二十个月后转正",
    },
    "donut-chart": {
        "title": "预算分配占比",
        "center_value": "80 万",
        "center_label": "总预算",
        "segments": [
            {"name": "软件与实施", "value": 60, "label": "60 万"},
            {"name": "硬件与培训", "value": 20, "label": "20 万"},
        ],
        "note": "两项支出分别占预算的七成五与两成五",
    },
    "comparison-bars": {
        "title": "验收指标达成水平对比",
        "items": [
            {"name": "检索响应", "value": 620, "label": "秒级"},
            {"name": "权限准确", "value": 800, "label": "全部正确"},
            {"name": "试点使用", "value": 700, "label": "周活跃"},
        ],
        "note": "条长表示各项达成水平，均取自验收结论",
    },
}


def run_demo(outdir: str) -> int:
    os.makedirs(outdir, exist_ok=True)
    for key, spec in DEMO.items():
        path = os.path.join(outdir, key + ".svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(GENERATORS[key](spec))
        print(f"[OK] {key} -> {path}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v2 图表骨架 数据→几何重算器")
    ap.add_argument("--type", choices=sorted(GENERATORS), help="图表类型")
    ap.add_argument("--spec", help="JSON 数据文件（UTF-8）")
    ap.add_argument("-o", "--out", required=True, help="输出路径（--demo 时视为目录）")
    ap.add_argument("--demo", action="store_true", help="生成 v2 同源数据四页")
    a = ap.parse_args(argv)
    if a.demo:
        return run_demo(a.out)
    if not a.type or not a.spec:
        ap.error("需要 --type 与 --spec（或使用 --demo）")
    with open(a.spec, encoding="utf-8") as f:
        spec = json.load(f)
    svg = GENERATORS[a.type](spec)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[OK] {a.out}  ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
