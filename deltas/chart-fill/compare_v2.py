#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2 生成版 vs 手写版 · 几何一致性对比（T-A1 Part B 硬要求）。

做法：把两侧 SVG 的**关键几何数值**抽出来逐项比对，而不是靠肉眼。
  · bar-chart       ：柱的 (x,y,w,h) 列表
  · line-chart      ：折线点坐标 + 数据点圆 cx,cy
  · donut-chart     ：每段 stroke-dasharray 与 rotate 角度
  · comparison-bars ：条 (x,y,w,h) 列表 + 名称/数值基线

输出：差异表 + 判定（[SAME] / [DIFF]）。

注：标记刻意用纯 ASCII——Windows 控制台默认 GBK，emoji 会 UnicodeEncodeError。
"""

from __future__ import annotations

import os
import re
import sys
from xml.etree import ElementTree as ET


def s(tag):
    return tag.split("}")[-1]


def rects(path, gid):
    root = ET.parse(path).getroot()
    out = []
    for g in root.iter():
        if s(g.tag) == "g" and g.get("id") == gid:
            for r in g.iter():
                if s(r.tag) == "rect":
                    out.append(tuple(round(float(r.get(k) or 0), 1)
                                     for k in ("x", "y", "width", "height")))
    return out


def circles(path, gid):
    root = ET.parse(path).getroot()
    out = []
    for g in root.iter():
        if s(g.tag) == "g" and g.get("id") == gid:
            for c in g.iter():
                if s(c.tag) == "circle":
                    out.append((round(float(c.get("cx") or 0), 1),
                                round(float(c.get("cy") or 0), 1),
                                c.get("r"), c.get("stroke-dasharray"),
                                c.get("transform")))
    return out


def polyline(path, gid):
    root = ET.parse(path).getroot()
    for g in root.iter():
        if s(g.tag) == "g" and g.get("id") == gid:
            for p in g.iter():
                if s(p.tag) == "polyline":
                    return p.get("points")
    return None


def texts(path, gid):
    root = ET.parse(path).getroot()
    out = []
    for g in root.iter():
        if s(g.tag) == "g" and g.get("id") == gid:
            for t in g.iter():
                if s(t.tag) == "text":
                    out.append((t.get("x"), t.get("y"),
                                (t.text or "").strip()[:24]))
    return out


def diff(label, a, b):
    """逐项比对，返回 (same, notes)。"""
    if a == b:
        return True, []
    notes = [f"  生成版: {a}", f"  手写版: {b}"]
    return False, notes


def main(hand_dir: str, gen_dir: str) -> int:
    print("=" * 74)
    print("v2 生成版 vs 手写版 · 几何对比")
    print("=" * 74)
    overall = True

    # ---- bar-chart ----
    print("\n### bar-chart（柱几何）")
    h = rects(os.path.join(hand_dir, "bar-chart.svg"), "bar-plot")
    g = rects(os.path.join(gen_dir, "bar-chart.svg"), "bar-plot")
    # 去掉基线 rect（y=500,h=2）
    hb = [r for r in h if r[3] > 10]
    gb = [r for r in g if r[3] > 10]
    ok, notes = diff("bars", gb, hb)
    print(f"  手写 {len(hb)} 柱 / 生成 {len(gb)} 柱 -> {'[SAME]' if ok else '[DIFF]'}")
    for n in notes:
        print(n)
    overall &= ok

    # ---- line-chart ----
    print("\n### line-chart（折线点 + 数据点）")
    hp = polyline(os.path.join(hand_dir, "line-chart.svg"), "line-plot")
    gp = polyline(os.path.join(gen_dir, "line-chart.svg"), "line-plot")
    norm = lambda p: [(round(float(a), 1), round(float(b), 1))
                      for a, b in (xy.split(",") for xy in (p or "").split())]
    ok, notes = diff("polyline", norm(gp), norm(hp))
    print(f"  折线点 -> {'[SAME]' if ok else '[DIFF]'}")
    for n in notes:
        print(n)
    if not ok:
        print("  （说明：手写版点 x 为 240/560/1040，文档 §2.2 公式为 160/640/1120）")
    overall &= ok

    # ---- donut-chart ----
    print("\n### donut-chart（段 dasharray + 角度）")
    hc = circles(os.path.join(hand_dir, "donut-chart.svg"), "donut-plot")
    gc = circles(os.path.join(gen_dir, "donut-chart.svg"), "donut-plot")
    hseg = [(c[3], c[4]) for c in hc if c[3]]
    gseg = [(c[3], c[4]) for c in gc if c[3]]
    ok, notes = diff("segments", gseg, hseg)
    print(f"  弧段 -> {'[SAME]' if ok else '[DIFF]'}")
    for n in notes:
        print(n)
    overall &= ok

    # ---- comparison-bars ----
    print("\n### comparison-bars（条几何）")
    hb = rects(os.path.join(hand_dir, "comparison-bars.svg"), "compare-bars")
    gb = rects(os.path.join(gen_dir, "comparison-bars.svg"), "compare-bars")
    hb = [r for r in hb if r[3] == 34]
    gb = [r for r in gb if r[3] == 34]
    ok, notes = diff("bars", gb, hb)
    print(f"  手写 {len(hb)} 条 / 生成 {len(gb)} 条 -> {'[SAME]' if ok else '[DIFF]'}")
    for n in notes:
        print(n)
    overall &= ok

    print("\n" + "=" * 74)
    print(f"总体判定：{'[SAME] 生成版与手写版几何完全一致' if overall else '[DIFF] 存在差异（见上，属预期或需修正）'}")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
