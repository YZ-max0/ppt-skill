#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""base 图表模板填充器 —— 数据 → 可直接进 svg_output 的页面 SVG。

用法：
    python fill_chart.py --type column --spec data.json -o out.svg
    python fill_chart.py --demo -o outdir/          # 出 T-02 示例三页

契约来源（T-E2E3 Part A 实测结论）：
    vendor-ppt-master/templates/charts/ 的 33 个 SVG 是**渲染好的示例**，不是待填槽位的骨架：
      · 无 `【槽位】` 标记；数据已硬编码进几何（柱高/点坐标/条长）
      · 每个模板内嵌 `<metadata type="application/json">`，声明数据模型
        （type / categories / series|values / style），并挂在
        `<g data-pptx-replace-with="chart">` 上（原生图表替换的 opt-in 标记）
    因此"接入"= 取两份契约（metadata 数据模型 + 视觉语言），按数据重算几何。
    本工具就是那个"重算器"，把手工坐标计算（v2/CONTRACT §2.6 易错点）自动化。

与 vendor 的关系：本文件属 repo 定制层 deltas/，**不修改 vendor**；
图表契约与模板保持只读引用。视觉语言向仓库既有骨架靠拢（见下）。

视觉语言（对齐 deltas/layout-assets）：
    文字 #0F172A ｜ 次级 #64748B ｜ 坐标轴 #94A3B8 ｜ 网格 #E2E8F0
    主色 #002FA7 ｜ 次色 #4A6FD4 ｜ 风险 #FF6B35 ｜ 画布 #FFFFFF
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

# ---------------------------------------------------------------------------
# 视觉常量（对齐 deltas/layout-assets 的语义色系统）
# ---------------------------------------------------------------------------

W, H = 1280, 720
FONT = ("-apple-system, BlinkMacSystemFont, 'Segoe UI', "
        "'PingFang SC', 'Microsoft YaHei', sans-serif")

INK = "#0F172A"        # 主文字
INK_2 = "#64748B"      # 次级文字
AXIS = "#94A3B8"       # 坐标轴
GRID = "#E2E8F0"       # 网格
PANEL = "#F0F0EE"      # 浅底
PRIMARY = "#002FA7"    # 主色（IKB 蓝）
PRIMARY_2 = "#4A6FD4"  # 同色系浅一档
RISK = "#FF6B35"       # 风险/未达标

# 绘图区
PLOT_L, PLOT_R = 160, 1160
PLOT_T, PLOT_B = 190, 560
CAT_Y = 600            # 类目标签基线
LEGEND_Y = 648         # 图例基线（必须独立于 CAT_Y：同排会与类目标签相撞）
NOTE_Y = 692           # 口径/来源说明基线


def esc(s: str) -> str:
    """XML 转义（raw Unicode 优先，仅转义保留字符）。"""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def nice_max(v: float) -> float:
    """把数据最大值上取整到"好看"的刻度上限。"""
    if v <= 0:
        return 1.0
    exp = math.floor(math.log10(v))
    base = 10.0 ** exp
    for m in (1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if v <= m * base + 1e-9:
            return m * base
    return 10.0 * base


def fmt(v: float) -> str:
    """数值标签格式：千分位，整数不带小数点。"""
    if abs(v - round(v)) < 1e-9:
        return f"{int(round(v)):,}"
    return f"{v:,.1f}"


# ---------------------------------------------------------------------------
# SVG 骨架
# ---------------------------------------------------------------------------

def page_open(title: str, subtitle: str = "", role: str = "content") -> list[str]:
    """页面根 + 标题区。role 消除 checker 的 page-role 警告（v0/CONTRACT §4.2）。"""
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" font-family="{FONT}" font-size="12" '
        f'data-pptx-page-role="{role}">',
        f'  <rect width="{W}" height="{H}" fill="#FFFFFF"/>',
        '  <g id="header" data-pptx-bounds="40 15 1200 125">',
        f'    <text x="80" y="90" font-size="40" font-weight="700" '
        f'fill="{INK}">{esc(title)}</text>',
    ]
    if subtitle:
        out.append(f'    <text x="80" y="128" font-size="18" '
                   f'fill="{INK_2}">{esc(subtitle)}</text>')
    out.append('  </g>')
    return out


def gridlines(lo: float, hi: float, divisions: int = 4) -> list[str]:
    """水平网格线 + 刻度标签。"""
    out = []
    for i in range(divisions + 1):
        val = lo + (hi - lo) * i / divisions
        y = PLOT_B - (PLOT_B - PLOT_T) * i / divisions
        dash = '' if i == 0 else ' stroke-dasharray="4,4"'
        color = AXIS if i == 0 else GRID
        out.append(f'    <line x1="{PLOT_L}" y1="{y:.0f}" x2="{PLOT_R}" '
                   f'y2="{y:.0f}" stroke="{color}" stroke-width="1"{dash}/>')
        out.append(f'    <text x="{PLOT_L - 16}" y="{y + 5:.0f}" '
                   f'font-size="14" fill="{INK_2}" text-anchor="end">'
                   f'{esc(fmt(val))}</text>')
    return out


def axis_lines() -> list[str]:
    return [
        f'    <line x1="{PLOT_L}" y1="{PLOT_T}" x2="{PLOT_L}" y2="{PLOT_B}" '
        f'stroke="{AXIS}" stroke-width="2"/>',
        f'    <line x1="{PLOT_L}" y1="{PLOT_B}" x2="{PLOT_R}" y2="{PLOT_B}" '
        f'stroke="{AXIS}" stroke-width="2"/>',
    ]


def note_line(note: str) -> list[str]:
    if not note:
        return []
    return [f'  <g id="note" data-pptx-bounds="80 668 1120 44">',
            f'    <text x="80" y="{NOTE_Y}" font-size="18" '
            f'fill="{INK_2}">{esc(note)}</text>',
            '  </g>']


def page_close() -> list[str]:
    return ['</svg>', '']


# ---------------------------------------------------------------------------
# 1) column —— 柱状对比（单序列或多序列分组）
# ---------------------------------------------------------------------------

def render_column(spec: dict) -> str:
    cats = spec["categories"]
    series = spec["series"]                      # [{name, values, color?}]
    unit = spec.get("unit", "")
    colors = spec.get("colors", [PRIMARY, PRIMARY_2, RISK])

    n, m = len(cats), len(series)
    allv = [v for s in series for v in s["values"]]
    top = nice_max(max(allv))

    slot = (PLOT_R - PLOT_L) / n
    group_w = slot * 0.62
    bar_w = min(78.0, group_w / m)

    out = page_open(spec["title"], spec.get("subtitle", ""))
    out.append(f'  <g id="chart-plot" data-pptx-bounds="{PLOT_L-60} {PLOT_T-30} '
               f'{PLOT_R-PLOT_L+80} {PLOT_B-PLOT_T+90}">')
    out += gridlines(0, top)

    for si, s in enumerate(series):
        color = s.get("color", colors[si % len(colors)])
        for i, v in enumerate(s["values"]):
            cx = PLOT_L + slot * (i + 0.5) + (si - (m - 1) / 2) * bar_w
            h = (v / top) * (PLOT_B - PLOT_T)
            x = cx - bar_w / 2
            y = PLOT_B - h
            out.append(f'    <rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" '
                       f'height="{h:.1f}" fill="{color}" rx="3"/>')
            out.append(f'    <text x="{cx:.1f}" y="{y - 12:.1f}" font-size="18" '
                       f'font-weight="700" fill="{INK}" '
                       f'text-anchor="middle">{esc(fmt(v))}</text>')

    out += axis_lines()

    for i, c in enumerate(cats):
        cx = PLOT_L + slot * (i + 0.5)
        out.append(f'    <text x="{cx:.1f}" y="{CAT_Y}" font-size="20" '
                   f'font-weight="600" fill="{INK}" text-anchor="middle">'
                   f'{esc(c)}</text>')

    out.append('  </g>')

    # 图例（多序列时）
    if m > 1:
        lx = PLOT_L
        # bounds 顶边须包住 18pt 文字 ascender（CAT_Y=600 → 内容顶约 582）
        out.append('  <g id="legend" data-pptx-bounds="160 620 760 44">')
        for si, s in enumerate(series):
            color = s.get("color", colors[si % len(colors)])
            out.append(f'    <rect x="{lx}" y="{LEGEND_Y - 16}" width="18" '
                       f'height="18" rx="3" fill="{color}"/>')
            out.append(f'    <text x="{lx + 26}" y="{LEGEND_Y}" font-size="18" '
                       f'font-weight="600" fill="{INK_2}">{esc(s["name"])}</text>')
            lx += 34 + len(s["name"]) * 19
        out.append('  </g>')

    out += note_line(spec.get("note", ""))
    out += page_close()
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# 2) line —— 趋势折线（1-4 序列，连续轴）
# ---------------------------------------------------------------------------

def render_line(spec: dict) -> str:
    cats = spec["categories"]
    series = spec["series"]
    colors = spec.get("colors", [PRIMARY, PRIMARY_2, RISK])

    n = len(cats)
    allv = [v for s in series for v in s["values"]]
    top = nice_max(max(allv))
    n_ = max(n - 1, 1)

    def px(i): return PLOT_L + (PLOT_R - PLOT_L) * i / n_
    def py(v): return PLOT_B - (v / top) * (PLOT_B - PLOT_T)

    out = page_open(spec["title"], spec.get("subtitle", ""))
    out.append(f'  <g id="chart-plot" data-pptx-bounds="{PLOT_L-60} {PLOT_T-30} '
               f'{PLOT_R-PLOT_L+80} {PLOT_B-PLOT_T+90}">')
    out += gridlines(0, top)

    for si, s in enumerate(series):
        color = s.get("color", colors[si % len(colors)])
        pts = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(s["values"]))
        out.append(f'    <polyline points="{pts}" fill="none" stroke="{color}" '
                   f'stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
        for i, v in enumerate(s["values"]):
            out.append(f'    <circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="7" '
                       f'fill="{color}" stroke="#FFFFFF" stroke-width="2"/>')

    # 末点数值标注（每序列一个，落在最新一期上 —— 述职场景读者最关心现值）
    for si, s in enumerate(series):
        color = s.get("color", colors[si % len(colors)])
        i = len(s["values"]) - 1
        v = s["values"][i]
        out.append(f'    <text x="{px(i):.1f}" y="{py(v) - 20:.1f}" font-size="20" '
                   f'font-weight="700" fill="{color}" text-anchor="end">'
                   f'{esc(fmt(v))}</text>')

    out += axis_lines()

    for i, c in enumerate(cats):
        out.append(f'    <text x="{px(i):.1f}" y="{CAT_Y}" font-size="20" '
                   f'font-weight="600" fill="{INK}" text-anchor="middle">'
                   f'{esc(c)}</text>')
    out.append('  </g>')

    lx = PLOT_L
    # bounds 必须包住文字 ascender（CAT_Y=600, 18pt → 内容顶约 582），故顶边取 576
    out.append('  <g id="legend" data-pptx-bounds="160 620 760 44">')
    for si, s in enumerate(series):
        color = s.get("color", colors[si % len(colors)])
        out.append(f'    <line x1="{lx}" y1="{LEGEND_Y - 7}" x2="{lx + 34}" '
                   f'y2="{LEGEND_Y - 7}" stroke="{color}" stroke-width="4" '
                   f'stroke-linecap="round"/>')
        out.append(f'    <circle cx="{lx + 17}" cy="{LEGEND_Y - 7}" r="6" fill="{color}"/>')
        out.append(f'    <text x="{lx + 44}" y="{LEGEND_Y}" font-size="18" '
                   f'font-weight="600" fill="{INK_2}">{esc(s["name"])}</text>')
        lx += 60 + len(s["name"]) * 19
    out.append('  </g>')

    out += note_line(spec.get("note", ""))
    out += page_close()
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# 3) bullet —— KPI 目标 vs 实际（横条 + 目标标尺 + 达成率）
# ---------------------------------------------------------------------------

def render_bullet(spec: dict) -> str:
    items = spec["items"]        # [{name, target, actual, unit, fmt?}]
    track_l, track_r = 420, 1010
    row_h = 96
    y0 = 200

    out = page_open(spec["title"], spec.get("subtitle", ""))
    # 顶边须容纳首行"目标"标签（cy-38 → 162，14pt ascender 约 150）
    out.append('  <g id="chart-plot" data-pptx-bounds="60 130 1160 520">')

    for i, it in enumerate(items):
        cy = y0 + i * row_h
        target, actual = it["target"], it["actual"]
        pct = actual / target * 100 if target else 0
        # 轨道按"目标值的 1.25 倍"作满宽，目标标尺落在 80% 处
        full = target * 1.25
        w_act = (actual / full) * (track_r - track_l)
        x_tgt = track_l + (target / full) * (track_r - track_l)
        ok = actual >= target
        color = PRIMARY if ok else RISK

        out.append(f'    <text x="80" y="{cy}" font-size="22" font-weight="600" '
                   f'fill="{INK}">{esc(it["name"])}</text>')
        out.append(f'    <text x="80" y="{cy + 28}" font-size="16" '
                   f'fill="{INK_2}">目标 {esc(fmt(target))}{esc(it.get("unit",""))}</text>')
        out.append(f'    <rect x="{track_l}" y="{cy - 20}" width="{track_r-track_l}" '
                   f'height="30" rx="4" fill="{PANEL}"/>')
        out.append(f'    <rect x="{track_l}" y="{cy - 20}" width="{w_act:.1f}" '
                   f'height="30" rx="4" fill="{color}"/>')
        out.append(f'    <line x1="{x_tgt:.1f}" y1="{cy - 32}" x2="{x_tgt:.1f}" '
                   f'y2="{cy + 22}" stroke="{INK}" stroke-width="3"/>')
        out.append(f'    <text x="{x_tgt:.1f}" y="{cy - 38}" font-size="14" '
                   f'fill="{INK_2}" text-anchor="middle">目标</text>')
        out.append(f'    <text x="{track_r + 26}" y="{cy}" font-size="20" '
                   f'font-weight="700" fill="{INK}">{esc(fmt(actual))}'
                   f'{esc(it.get("unit",""))}</text>')
        out.append(f'    <text x="{track_r + 26}" y="{cy + 26}" font-size="18" '
                   f'font-weight="700" fill="{color}">{pct:.0f}%</text>')

    out.append('  </g>')
    out += note_line(spec.get("note", ""))
    out += page_close()
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# 4) dual_axis —— 双纵轴折线（两个量纲不同的指标共享时间轴）
#    依据 charts_index: Pick for comparing 2 metrics with different units/scales
# ---------------------------------------------------------------------------

def render_dual_axis(spec: dict) -> str:
    cats = spec["categories"]
    left = spec["left"]        # {name, values, unit, color?}
    right = spec["right"]      # {name, values, unit, color?}

    c_l = left.get("color", PRIMARY)
    c_r = right.get("color", RISK)
    top_l = nice_max(max(left["values"]))
    top_r = nice_max(max(right["values"]))
    n = max(len(cats) - 1, 1)

    def px(i): return PLOT_L + (PLOT_R - PLOT_L) * i / n
    def py_l(v): return PLOT_B - (v / top_l) * (PLOT_B - PLOT_T)
    def py_r(v): return PLOT_B - (v / top_r) * (PLOT_B - PLOT_T)

    out = page_open(spec["title"], spec.get("subtitle", ""))
    out.append(f'  <g id="chart-plot" data-pptx-bounds="60 130 1160 520">')
    # 左轴网格（用左轴刻度）
    out += gridlines(0, top_l)

    # 左轴刻度标签染成左序列色、右轴染成右序列色，避免误读
    out.append(f'    <text x="{PLOT_L - 16}" y="{PLOT_T - 18}" font-size="15" '
               f'font-weight="600" fill="{c_l}" text-anchor="end">'
               f'{esc(left.get("unit",""))}</text>')
    out.append(f'    <text x="{PLOT_R + 16}" y="{PLOT_T - 18}" font-size="15" '
               f'font-weight="600" fill="{c_r}" text-anchor="start">'
               f'{esc(right.get("unit",""))}</text>')

    for values, color, py in ((left["values"], c_l, py_l),
                              (right["values"], c_r, py_r)):
        pts = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(values))
        out.append(f'    <polyline points="{pts}" fill="none" stroke="{color}" '
                   f'stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
        for i, v in enumerate(values):
            out.append(f'    <circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="7" '
                       f'fill="{color}" stroke="#FFFFFF" stroke-width="2"/>')

    # 右轴刻度（自上而下 4 档）
    for k in range(5):
        val = top_r * k / 4
        y = PLOT_B - (PLOT_B - PLOT_T) * k / 4
        out.append(f'    <text x="{PLOT_R + 16}" y="{y + 5:.0f}" font-size="14" '
                   f'fill="{INK_2}" text-anchor="start">{esc(fmt(val))}</text>')

    out += axis_lines()

    for i, c in enumerate(cats):
        out.append(f'    <text x="{px(i):.1f}" y="{CAT_Y}" font-size="20" '
                   f'font-weight="600" fill="{INK}" text-anchor="middle">'
                   f'{esc(c)}</text>')
    out.append('  </g>')

    # 图例（两序列，居中）
    lx = PLOT_L
    out.append('  <g id="legend" data-pptx-bounds="160 620 760 44">')
    for nm, color in ((left["name"], c_l), (right["name"], c_r)):
        out.append(f'    <line x1="{lx}" y1="{LEGEND_Y - 7}" x2="{lx + 34}" '
                   f'y2="{LEGEND_Y - 7}" stroke="{color}" stroke-width="4" '
                   f'stroke-linecap="round"/>')
        out.append(f'    <circle cx="{lx + 17}" cy="{LEGEND_Y - 7}" r="6" fill="{color}"/>')
        out.append(f'    <text x="{lx + 44}" y="{LEGEND_Y}" font-size="18" '
                   f'font-weight="600" fill="{INK_2}">{esc(nm)}</text>')
        lx += 60 + len(nm) * 19
    out.append('  </g>')

    out += note_line(spec.get("note", ""))
    out += page_close()
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# 5) progress —— 完成度条（3-8 项，每项一个百分比）
#    依据 charts_index: Pick for 3-8 items each with a completion %
# ---------------------------------------------------------------------------

def render_progress(spec: dict) -> str:
    items = spec["items"]        # [{name, pct, detail?}]
    track_l, track_r = 430, 1090
    y0 = 200
    # 行高自适应：3-8 项都必须落在 [200, 640] 内（含 detail 行）
    n = len(items)
    row_h = min(86.0, (612 - y0) / max(n - 1, 1))

    out = page_open(spec["title"], spec.get("subtitle", ""))
    out.append('  <g id="chart-plot" data-pptx-bounds="60 130 1160 530">')

    for i, it in enumerate(items):
        cy = y0 + i * row_h
        pct = it["pct"]
        w = max(0.0, min(pct, 100.0)) / 100.0 * (track_r - track_l)
        color = PRIMARY if pct >= 80 else (PRIMARY_2 if pct >= 50 else RISK)

        out.append(f'    <text x="80" y="{cy}" font-size="22" font-weight="600" '
                   f'fill="{INK}">{esc(it["name"])}</text>')
        if it.get("detail"):
            out.append(f'    <text x="80" y="{cy + 26}" font-size="16" '
                       f'fill="{INK_2}">{esc(it["detail"])}</text>')
        out.append(f'    <rect x="{track_l}" y="{cy - 20}" width="{track_r-track_l}" '
                   f'height="28" rx="4" fill="{PANEL}"/>')
        out.append(f'    <rect x="{track_l}" y="{cy - 20}" width="{w:.1f}" '
                   f'height="28" rx="4" fill="{color}"/>')
        out.append(f'    <text x="{track_r + 24}" y="{cy + 4}" font-size="22" '
                   f'font-weight="700" fill="{color}">{pct:.0f}%</text>')

    out.append('  </g>')
    out += note_line(spec.get("note", ""))
    out += page_close()
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# 6) area —— 面积折线（强调累积量级）
#    依据 charts_index: Pick for 1-2 cumulative trend series emphasizing volume
# ---------------------------------------------------------------------------

def render_area(spec: dict) -> str:
    cats = spec["categories"]
    series = spec["series"]
    colors = spec.get("colors", [PRIMARY, PRIMARY_2])

    n = len(cats)
    allv = [v for s in series for v in s["values"]]
    top = nice_max(max(allv))
    n_ = max(n - 1, 1)

    def px(i): return PLOT_L + (PLOT_R - PLOT_L) * i / n_
    def py(v): return PLOT_B - (v / top) * (PLOT_B - PLOT_T)

    out = page_open(spec["title"], spec.get("subtitle", ""))
    out.append(f'  <g id="chart-plot" data-pptx-bounds="60 130 1160 520">')
    out += gridlines(0, top)

    for si, s in enumerate(series):
        color = s.get("color", colors[si % len(colors)])
        pts = [(px(i), py(v)) for i, v in enumerate(s["values"])]
        poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        # 面积：折线 + 回到基线的闭合多边形
        area = (f"{PLOT_L:.1f},{PLOT_B:.1f} " + poly
                + f" {pts[-1][0]:.1f},{PLOT_B:.1f}")
        out.append(f'    <polygon points="{area}" fill="{color}" fill-opacity="0.12" '
                   f'stroke="none"/>')
        out.append(f'    <polyline points="{poly}" fill="none" stroke="{color}" '
                   f'stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
        for x, y in pts:
            out.append(f'    <circle cx="{x:.1f}" cy="{y:.1f}" r="6" '
                       f'fill="{color}" stroke="#FFFFFF" stroke-width="2"/>')

    out += axis_lines()

    for i, c in enumerate(cats):
        out.append(f'    <text x="{px(i):.1f}" y="{CAT_Y}" font-size="20" '
                   f'font-weight="600" fill="{INK}" text-anchor="middle">'
                   f'{esc(c)}</text>')
    out.append('  </g>')

    lx = PLOT_L
    out.append('  <g id="legend" data-pptx-bounds="160 620 760 44">')
    for si, s in enumerate(series):
        color = s.get("color", colors[si % len(colors)])
        out.append(f'    <rect x="{lx}" y="{LEGEND_Y - 16}" width="18" height="18" '
                   f'rx="3" fill="{color}" fill-opacity="0.35" stroke="{color}"/>')
        out.append(f'    <text x="{lx + 26}" y="{LEGEND_Y}" font-size="18" '
                   f'font-weight="600" fill="{INK_2}">{esc(s["name"])}</text>')
        lx += 34 + len(s["name"]) * 19
    out.append('  </g>')

    out += note_line(spec.get("note", ""))
    out += page_close()
    return "\n".join(out) + "\n"


RENDERERS = {"column": render_column, "line": render_line, "bullet": render_bullet,
             "dual_axis": render_dual_axis, "progress": render_progress,
             "area": render_area}


# ---------------------------------------------------------------------------
# T-02 示例数据（年终述职；模拟素材，口径见报告"假设声明"）
# ---------------------------------------------------------------------------

DEMO = {
    "P-revenue": {
        "type": "column",
        "title": "营业收入连续五年增长，2025 年创历史新高",
        "subtitle": "2021—2025 年营业收入（单位：万元）",
        "categories": ["2021", "2022", "2023", "2024", "2025"],
        "series": [{"name": "营业收入",
                    "values": [3200, 3850, 4520, 5180, 6240]}],
        "note": "口径：财务年度审计后营业收入，含税转不含税；数据为模拟素材，见假设声明。",
    },
    "P-trend": {
        "type": "line",
        "title": "收入与净利润同步走高，净利率稳定在 24% 以上",
        "subtitle": "2025 年分季度收入与净利润（单位：万元）",
        "categories": ["Q1", "Q2", "Q3", "Q4"],
        "series": [
            {"name": "营业收入", "values": [1180, 1520, 1690, 1850]},
            {"name": "净利润", "values": [286, 372, 448, 524]},
        ],
        "note": "口径：管理报表口径，未扣除非经常性损益；数据为模拟素材，见假设声明。",
    },
    "P-kpi": {
        "type": "bullet",
        "title": "四项年度考核指标：三项超额完成，一项待改进",
        "subtitle": "实际值 vs 年度目标值",
        "items": [
            {"name": "营业收入", "target": 6000, "actual": 6240, "unit": " 万元"},
            {"name": "净利润", "target": 1500, "actual": 1630, "unit": " 万元"},
            {"name": "客户续约率", "target": 90, "actual": 92.5, "unit": "%"},
            {"name": "人均产出", "target": 120, "actual": 116, "unit": " 万元"},
        ],
        "note": "判读：人均产出低于目标 3%，为本年度主要缺口；数据为模拟素材，见假设声明。",
    },
}


def run_demo(outdir: str) -> int:
    os.makedirs(outdir, exist_ok=True)
    for name, spec in DEMO.items():
        t = spec.pop("type")
        path = os.path.join(outdir, name + ".svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(RENDERERS[t](spec))
        spec["type"] = t
        print(f"[OK] {path}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="base 图表模板填充器")
    ap.add_argument("--type", choices=sorted(RENDERERS), help="图表类型")
    ap.add_argument("--spec", help="JSON 数据文件（UTF-8）")
    ap.add_argument("-o", "--out", required=True, help="输出路径（--demo 时视为目录）")
    ap.add_argument("--demo", action="store_true", help="生成 T-02 示例三页")
    a = ap.parse_args(argv)

    if a.demo:
        return run_demo(a.out)

    if not a.type or not a.spec:
        ap.error("需要 --type 与 --spec（或使用 --demo）")
    with open(a.spec, encoding="utf-8") as f:
        spec = json.load(f)
    svg = RENDERERS[a.type](spec)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[OK] {a.out}  ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
