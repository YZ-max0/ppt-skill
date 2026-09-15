#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""base 表格模板填充器 —— 数据 → 可直接进 svg_output 的页面 SVG（T-A1 Part A）。

契约来源（实测结论，与 charts 族同款）
------------------------------------
`vendor-ppt-master/templates/tables/` 的 6 个 SVG 是**渲染好的示例**，不是待填槽位的骨架：
  · 无 `【槽位】` 标记（实测 0 命中）
  · 数据已硬编码进几何（单元格文本、列宽、行高）
  · **只有 2/6 带原生 Table 标记**（`record_table` / `hierarchical_table`）
    —— 其余 4 个 `grep data-pptx-replace-with` 为 0，即使加 `--native-charts-and-tables`
    也只会渲染成散落文本框（实测：metric_table 拆出 37 个文本框）

因此"接入"= 取两份契约（`<metadata>` 的数据模型 + 模板的网格视觉语言），按数据重算几何。
本工具就是那个"重算器"。

与 charts 的差异（重要）
----------------------
| 维度 | charts | tables |
|---|---|---|
| 数据模型位置 | 每个模板都有 `<metadata>` | **仅 2/6 有**；其余需从几何反推 |
| 原生标记 | 全部有 `replace-with="chart"` | **仅 2/6 有** |
| 几何复杂度 | 高（坐标映射公式） | 低（等宽/等高网格，按 column_widths/row_heights 累加） |
| 默认导出 | 矢量形状 | 矢量形状（同上） |

→ 故本工具的**主要价值不在"算坐标"**（表格是简单累加），而在：
  ① 统一产出**带原生标记 + metadata** 的合规 SVG（让 4 个无标记模板也能走原生表格路径）
  ② 消除手改 6 个 svg 的重复劳动
  ③ 与 `fill_chart.py` 同一套 spec/CLI 风格

视觉语言
--------
沿用仓库语义色（`#F0F0EE` 表头底 / `#0F172A` 正文 / `#E2E8F0` 边框 / `#002FA7` 主色），
**不沿用** base 模板的 Tailwind 色（`#F1F5F9`/`#475569` 等），以符合 `v2/CONTRACT.md` v2-2。
即：**借模板的网格契约与 metadata schema，不借它的配色**。
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# ---------------------------------------------------------------------------
# 视觉常量（对齐 deltas/layout-assets 语义色）
# ---------------------------------------------------------------------------
W, H = 1280, 720
FONT = ("-apple-system, BlinkMacSystemFont, 'Segoe UI', "
        "'PingFang SC', 'Microsoft YaHei', sans-serif")

INK = "#0F172A"        # 主文字
INK_2 = "#64748B"      # 次级文字
PANEL = "#F0F0EE"      # 浅底（表头 / 斑马纹）
BORDER = "#E2E8F0"     # 表格边框
PRIMARY = "#002FA7"    # 主色
POS = "#002FA7"        # 正向（与主色同）
NEG = "#FF6B35"        # 负向 / 风险

TABLE_X, TABLE_Y = 80, 150
DEFAULT_COL_W = 200
DEFAULT_ROW_H = 56
HEADER_ROW_H = 60


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def vw_of(text: str) -> float:
    """视觉宽度（vw），口径同 capacity.py / fill_chart.py。"""
    w = 0.0
    for ch in text:
        if ("\u4e00" <= ch <= "\u9fff"
                or "\u3000" <= ch <= "\u303f"
                or "\uff00" <= ch <= "\uffef"):
            w += 1.0
        elif ch == " ":
            w += 0.35
        elif ch.isascii():
            w += 0.5
        else:
            w += 0.8
    return w


# ---------------------------------------------------------------------------
# 几何
# ---------------------------------------------------------------------------

def compute_grid(spec: dict):
    """返回 (col_widths, row_heights, x, y, total_w, total_h)。"""
    cols = spec["columns"]
    rows = spec["rows"]
    ncol, nrow = len(cols), len(rows) + 1        # +1 表头行

    col_w = spec.get("column_widths")
    if not col_w:
        total = spec.get("table_width", 1120)
        col_w = [round(total / ncol)] * ncol
    col_w = list(col_w) + [DEFAULT_COL_W] * (ncol - len(col_w))
    col_w = col_w[:ncol]

    row_h = spec.get("row_heights")
    if not row_h:
        row_h = [HEADER_ROW_H] + [DEFAULT_ROW_H] * (nrow - 1)
    row_h = list(row_h) + [DEFAULT_ROW_H] * (nrow - len(row_h))
    row_h = row_h[:nrow]

    x = spec.get("x", TABLE_X)
    y = spec.get("y", TABLE_Y)
    return col_w, row_h, x, y, sum(col_w), sum(row_h)


def _cell_align(col_spec: dict, cell: dict, default: str = "l") -> str:
    return cell.get("align") or col_spec.get("align") or default


def _anchor(align: str) -> str:
    return {"l": "start", "ctr": "middle", "c": "middle", "r": "end"}.get(align, "start")


def _cell_x(cx: float, cw: float, align: str, pad: float) -> float:
    if align in ("ctr", "c"):
        return cx + cw / 2
    if align == "r":
        return cx + cw - pad
    return cx + pad


# ---------------------------------------------------------------------------
# 渲染
# ---------------------------------------------------------------------------

def render_table(spec: dict) -> str:
    cols = spec["columns"]
    rows = spec["rows"]
    col_w, row_h, tx, ty, total_w, total_h = compute_grid(spec)

    title = spec.get("title", "")
    subtitle = spec.get("subtitle", "")
    note = spec.get("note", "")
    name = spec.get("name", "data-table")
    fs = spec.get("font_size", 15)
    hfs = spec.get("header_font_size", 13)
    pad = spec.get("padding", 12)
    band = spec.get("band_row", True)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" font-family="{FONT}" font-size="12" '
        f'data-pptx-page-role="content">',
        f'  <rect width="{W}" height="{H}" fill="#FFFFFF"/>',
    ]

    # 标题区
    if title:
        out.append('  <g id="header" data-pptx-bounds="80 35 1120 80">')
        out.append(f'    <text x="80" y="72" font-size="32" font-weight="700" '
                   f'fill="{INK}">{esc(title)}</text>')
        if subtitle:
            out.append(f'    <text x="80" y="102" font-size="16" '
                       f'fill="{INK_2}">{esc(subtitle)}</text>')
        out.append('  </g>')

    # 原生表格标记组：可见 SVG 回退 + metadata（两者描述同一份数据）
    out.append(f'  <g id="{esc(name)}" data-pptx-bounds="{tx} {ty} {total_w} {total_h}" '
               f'data-pptx-replace-with="table">')

    # --- 可见回退：斑马纹底 + 表头底 ---
    ys = [ty]
    for h in row_h:
        ys.append(ys[-1] + h)
    out.append(f'    <rect x="{tx}" y="{ty}" width="{total_w}" '
               f'height="{row_h[0]}" fill="{PANEL}"/>')
    if band:
        for ri in range(1, len(row_h)):
            if ri % 2 == 0:
                out.append(f'    <rect x="{tx}" y="{ys[ri]:.0f}" width="{total_w}" '
                           f'height="{row_h[ri]:.0f}" fill="{PANEL}" fill-opacity="0.55"/>')

    # --- 边框 + 网格线 ---
    out.append(f'    <rect x="{tx}" y="{ty}" width="{total_w}" height="{total_h}" '
               f'fill="none" stroke="{BORDER}" stroke-width="1.5"/>')
    out.append(f'    <g stroke="{BORDER}" stroke-width="1">')
    cx = tx
    for wdt in col_w[:-1]:
        cx += wdt
        out.append(f'      <line x1="{cx:.0f}" y1="{ty}" x2="{cx:.0f}" '
                   f'y2="{ty + total_h}"/>')
    for yy in ys[1:-1]:
        out.append(f'      <line x1="{tx}" y1="{yy:.0f}" x2="{tx + total_w}" '
                   f'y2="{yy:.0f}"/>')
    out.append('    </g>')

    # --- 表头文本 ---
    cx = tx
    for ci, c in enumerate(cols):
        cw = col_w[ci]
        align = _cell_align(c, c, "l")
        x = _cell_x(cx, cw, align, pad)
        out.append(f'    <text x="{x:.0f}" y="{ys[0] + row_h[0]/2 + 5:.0f}" '
                   f'font-size="{hfs}" font-weight="700" fill="{INK}" '
                   f'text-anchor="{_anchor(align)}">{esc(c["text"])}</text>')
        cx += cw

    # --- 数据行文本 ---
    for ri, row in enumerate(rows):
        ry = ys[ri + 1]
        rh = row_h[ri + 1]
        cx = tx
        for ci, col in enumerate(cols):
            cw = col_w[ci]
            cell = row[ci] if ci < len(row) else {}
            if isinstance(cell, str):
                cell = {"text": cell}
            align = _cell_align(col, cell, "l")
            x = _cell_x(cx, cw, align, pad)
            color = cell.get("color") or (INK if cell.get("bold") else INK_2)
            weight = "700" if cell.get("bold") else "400"
            out.append(f'    <text x="{x:.0f}" y="{ry + rh/2 + 5:.0f}" '
                       f'font-size="{fs}" font-weight="{weight}" fill="{color}" '
                       f'text-anchor="{_anchor(align)}">{esc(cell.get("text",""))}</text>')
            cx += cw

    # --- metadata（原生 Table 的数据来源，schema 对齐 base）---
    meta = {
        "name": name,
        "x": tx, "y": ty, "width": total_w, "height": total_h,
        "strict_grid": True,
        "column_widths": col_w,
        "row_heights": row_h,
        "style": {
            "font_family": "Microsoft YaHei",
            "font_size": fs,
            "header_font_size": hfs,
            "header_fill": PANEL,
            "header_text": INK,
            "body_fill": "#FFFFFF",
            "body_text": INK,
            "band_row": bool(band),
            "band_fill": PANEL,
            "border_color": BORDER,
            "border_width": 1,
            "padding": {"left": pad, "right": pad, "top": 6, "bottom": 6},
            "valign": "middle",
        },
        "columns": [
            {k: v for k, v in {
                "text": c["text"],
                "bold": True,
                "align": _cell_align(c, c, "l"),
            }.items() if v not in (None, False)}
            for c in cols
        ],
        "rows": [
            [
                {k: v for k, v in {
                    "text": (cell if isinstance(cell, str) else cell.get("text", "")),
                    "align": _cell_align(cols[ci] if ci < len(cols) else {}, 
                                         cell if isinstance(cell, dict) else {}, "l"),
                    "bold": (isinstance(cell, dict) and cell.get("bold")) or None,
                    "color": (cell.get("color") if isinstance(cell, dict) else None),
                }.items() if v not in (None, False)}
                for ci, cell in enumerate(row)
            ]
            for row in rows
        ],
    }
    out.append('    <metadata type="application/json">')
    out.append(json.dumps(meta, ensure_ascii=False))
    out.append('    </metadata>')
    out.append('  </g>')

    if note:
        # note 基线随表格高度浮动，bounds 必须同步（否则 checker 报垂直溢出）
        ny = TABLE_Y + total_h + 46
        out.append(f'  <g id="note" data-pptx-bounds="80 {ny - 20:.0f} 1120 44">')
        out.append(f'    <text x="80" y="{ny:.0f}" font-size="18" '
                   f'fill="{INK_2}">{esc(note)}</text>')
        out.append('  </g>')

    out.append('</svg>')
    out.append('')
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 示例数据（T-A1 Part A 验证用；题材沿用 T-06 数据中台语境）
# ---------------------------------------------------------------------------

DEMO = {
    "T-record": {
        "name": "deliverable-record",
        "title": "二期交付物台账",
        "subtitle": "按交付物逐条记录状态与验收情况",
        "columns": [
            {"text": "交付物", "bold": True},
            {"text": "说明", "bold": True},
            {"text": "责任方", "bold": True},
            {"text": "状态", "align": "ctr", "bold": True},
            {"text": "完成度", "align": "r", "bold": True},
        ],
        "column_widths": [200, 420, 180, 140, 180],
        "rows": [
            [{"text": "源系统接入", "color": INK_2}, {"text": "19 个源系统完成验收", "bold": True},
             {"text": "平台组", "color": INK_2},
             {"text": "已完成", "align": "ctr", "color": POS, "bold": True},
             {"text": "100%", "align": "r", "bold": True}],
            [{"text": "指标口径库", "color": INK_2}, {"text": "320 项指标发布", "bold": True},
             {"text": "治理组", "color": INK_2},
             {"text": "已完成", "align": "ctr", "color": POS, "bold": True},
             {"text": "100%", "align": "r", "bold": True}],
            [{"text": "自助取数平台", "color": INK_2}, {"text": "14 个场景完成切换", "bold": True},
             {"text": "平台组", "color": INK_2},
             {"text": "已完成", "align": "ctr", "color": POS, "bold": True},
             {"text": "100%", "align": "r", "bold": True}],
            [{"text": "历史数据迁移", "color": INK_2}, {"text": "4.2 亿条双向核对", "bold": True},
             {"text": "平台组", "color": INK_2},
             {"text": "已完成", "align": "ctr", "color": POS, "bold": True},
             {"text": "100%", "align": "r", "bold": True}],
            [{"text": "实时能力", "color": INK_2}, {"text": "时效 12 分钟，未达分钟级", "bold": True},
             {"text": "平台组", "color": INK_2},
             {"text": "延期", "align": "ctr", "color": NEG, "bold": True},
             {"text": "45%", "align": "r", "bold": True}],
            [{"text": "治理自动化", "color": INK_2}, {"text": "规则引擎原型阶段", "bold": True},
             {"text": "治理组", "color": INK_2},
             {"text": "延期", "align": "ctr", "color": NEG, "bold": True},
             {"text": "30%", "align": "r", "bold": True}],
        ],
        "note": "口径：完成度按开发、测试、上线三段加权；后两项为三期重点。",
    },
    "T-hier": {
        "name": "budget-hierarchy",
        "title": "三期预算分项拆解",
        "subtitle": "按方向分组，含小计与总计",
        "columns": [
            {"text": "项目", "bold": True},
            {"text": "方向", "align": "r", "bold": True},
            {"text": "实施", "align": "r", "bold": True},
            {"text": "小计", "align": "r", "bold": True},
            {"text": "占比", "align": "r", "bold": True},
        ],
        "column_widths": [400, 180, 180, 180, 180],
        "rows": [
            [{"text": "  实时链路改造", "color": INK_2}, {"text": "170", "align": "r", "color": INK_2},
             {"text": "170", "align": "r", "color": INK_2}, {"text": "340", "align": "r", "bold": True},
             {"text": "55%", "align": "r", "bold": True}],
            [{"text": "  高价值链路验证", "color": INK_2}, {"text": "120", "align": "r", "color": INK_2},
             {"text": "80", "align": "r", "color": INK_2}, {"text": "200", "align": "r", "bold": True},
             {"text": "32%", "align": "r", "bold": True}],
            [{"text": "治理引擎建设", "color": INK_2}, {"text": "120", "align": "r", "color": INK_2},
             {"text": "80", "align": "r", "color": INK_2}, {"text": "200", "align": "r", "bold": True},
             {"text": "32%", "align": "r", "bold": True}],
            [{"text": "储备资金", "color": INK_2}, {"text": "40", "align": "r", "color": INK_2},
             {"text": "40", "align": "r", "color": INK_2}, {"text": "80", "align": "r", "bold": True},
             {"text": "13%", "align": "r", "bold": True}],
            [{"text": "合计", "bold": True}, {"text": "330", "align": "r", "bold": True},
             {"text": "290", "align": "r", "bold": True}, {"text": "620", "align": "r", "bold": True},
             {"text": "100%", "align": "r", "bold": True}],
        ],
        "note": "口径：单位万元。合计 620 万元，与三期立项建议书一致。",
    },
}


def run_demo(outdir: str) -> int:
    os.makedirs(outdir, exist_ok=True)
    for key, spec in DEMO.items():
        path = os.path.join(outdir, key + ".svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(render_table(spec))
        print(f"[OK] {path}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="base 表格模板填充器")
    ap.add_argument("--spec", help="JSON 数据文件（UTF-8）")
    ap.add_argument("-o", "--out", required=True, help="输出路径（--demo 时视为目录）")
    ap.add_argument("--demo", action="store_true", help="生成 T-A1 示例两页")
    a = ap.parse_args(argv)

    if a.demo:
        return run_demo(a.out)

    if not a.spec:
        ap.error("需要 --spec（或使用 --demo）")
    with open(a.spec, encoding="utf-8") as f:
        spec = json.load(f)
    svg = render_table(spec)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[OK] {a.out}  ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
