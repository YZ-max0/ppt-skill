#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跨组重叠检查器 · 拦截"单组几何合法、跨组整体冲突"（T-FIX5 / C-015）。

第三类"测不出"问题
------------------
本项目已沉淀三道闸，各管一层：

| 闸 | 管什么 | 拦得住 | 拦不住 |
|---|---|---|---|
| `svg_quality_checker` | 几何 | 元素超出自身 `<g>` bounds / 画布 | 跨组冲突 |
| `pptx-fill-check`（D-2） | 填充后出框、标题一致性 | 文本溢出容器 | 跨组冲突 |
| `check_hygiene`（T-FIX4） | 内容泄漏 | 骨架示例内容残留 | 跨组冲突 |
| **本工具** | **跨组重叠** | 图例压字、标签叠印 | — |

C-011（内容泄漏）与 C-015（图例压字）同根：**每组各自合法，整体却错**。
C-015 实测：`legend` 组与 `chart-plot` 组的图例/类目标签同在 `y=600`，
两者 bounds 都在自己组内，checker 报 `blocking: 0`，只能靠人眼看 contact sheet 发现。

判据
----
1. **文本 × 文本**（跨组）：两文本估算 bbox 相交
2. **文本 × 图形**（跨组）：文本 bbox 与图形元素 bbox 相交
   （**同组内**文本-图形重叠合法：深色格反白字、色块上的标签、柱顶数值等，一律放行）
3. 重叠面积占**较小者**面积的比例 > 阈值（默认 5%）才报 —— 避免贴边误报

豁免机制
--------
- `id="page-bg"` 的组整体跳过（整页背景本就该被内容覆盖）
- 任一元素或其祖先组带 `data-ok-overlap="true"` → 该元素跳过（刻意叠放，如装饰压字）
- 同组 / 祖先-后代组之间不比较

bbox 口径（与 `pptx-fill-check/capacity.py` 的 `vw_of` 一致）
    CJK/全角 = 1.0，ASCII = 0.5，空格 = 0.35，其他 = 0.8
    文本宽 = vw(text) × font-size；高 = ascent 0.85 + descent 0.35（与 vendor checker 同）
    rect/circle/polyline/polygon 取几何极值；line 取两端点

用法
----
    python check_overlap.py <svg_dir> [--threshold 0.05] [--json] [-o OUT] [--verbose]

退出码：0 = 无跨组重叠 ｜ 2 = 发现重叠（P1）
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from xml.etree import ElementTree as ET

# ---------------------------------------------------------------------------
# 常量（与 capacity.py / vendor checker 对齐）
# ---------------------------------------------------------------------------
ASCENT_RATIO = 0.85      # vendor checker: ascent = font_size * 0.85
DESCENT_RATIO = 0.35     # vendor checker: descent = font_size * 0.35
DEFAULT_THRESHOLD = 0.05  # 重叠面积 / 较小者面积
DEFAULT_FONT_SIZE = 12.0
BG_GROUP_IDS = {"page-bg"}
OK_OVERLAP_ATTR = "data-ok-overlap"

# 不做 bbox 估算的元素（无法稳定求极值）
SKIP_TAGS = {"metadata", "defs", "style", "title", "desc", "tspan"}


def s(tag: str) -> str:
    return tag.split("}")[-1]


def vw_of(text: str) -> float:
    """视觉宽度（vw 单位）。口径同 deltas/pptx-fill-check/capacity.py。"""
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


def fnum(v, default=0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def points_bbox(points: str):
    nums = re.findall(r"-?\d+(?:\.\d+)?", points or "")
    if len(nums) < 2:
        return None
    xs = [float(n) for n in nums[0::2]]
    ys = [float(n) for n in nums[1::2]]
    if not xs or not ys:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


# ---------------------------------------------------------------------------
# 元素收集
# ---------------------------------------------------------------------------

class El:
    """一个待比较的元素（文本或图形），带所属组。"""

    __slots__ = ("kind", "gid", "label", "box", "ok")

    def __init__(self, kind, gid, label, box, ok):
        self.kind = kind        # 'text' | 'shape'
        self.gid = gid          # 所属组 id（'' 表示根级）
        self.label = label      # 展示用摘要
        self.box = box          # (x0, y0, x1, y1)
        self.ok = ok            # 是否显式豁免


def _inherited(el, root_by_id, attr, default=None):
    """沿祖先链取属性（近似 CSS 继承；用于 font-size / text-anchor）。"""
    cur = el
    while cur is not None:
        v = cur.get(attr)
        if v is not None:
            return v
        cur = root_by_id.get(id(cur))
    return default


def collect(path: str):
    """解析单个 SVG，返回元素列表。"""
    tree = ET.parse(path)
    root = tree.getroot()

    parent_by_id = {id(c): p for p in root.iter() for c in list(p)}

    # 祖先链上的组 id / 豁免标记
    def chain(el):
        out = []
        cur = el
        while cur is not None:
            out.append(cur)
            cur = parent_by_id.get(id(cur))
        return out

    def group_id_of(el):
        for anc in chain(el):
            if s(anc.tag) == "g":
                return anc.get("id") or ""
        return ""

    def is_ok(el):
        return any(a.get(OK_OVERLAP_ATTR) == "true" for a in chain(el))

    def in_bg(el):
        """整页背景：page-bg 组内，或根级满画布 rect。

        骨架（如 v0/kpi-hero）与 chart-fill 产物都可能把背景 rect 裸放在根级，
        它天然覆盖全页，必须排除，否则会对每个元素报 100% 重叠。
        """
        for a in chain(el):
            if s(a.tag) == "g" and (a.get("id") or "") in BG_GROUP_IDS:
                return True
        if s(el.tag) == "rect":
            w = fnum(el.get("width"))
            h = fnum(el.get("height"))
            if w >= 1200 and h >= 660:      # 近似满画布（1280×720）
                return True
        return False

    els = []

    for el in root.iter():
        tag = s(el.tag)
        if tag in SKIP_TAGS:
            continue
        if in_bg(el):
            continue

        gid = group_id_of(el)
        ok = is_ok(el)

        if tag == "text":
            visible = "".join(el.itertext()).strip()
            if not visible:
                continue
            # 多行：tspan 各自 x/dy；无 tspan 则单行
            tspans = [c for c in el if s(c.tag) == "tspan"]
            base_x = fnum(el.get("x"))
            base_y = fnum(el.get("y"))
            size = fnum(_inherited(el, parent_by_id, "font-size"), DEFAULT_FONT_SIZE)
            anchor = (_inherited(el, parent_by_id, "text-anchor") or "start").strip()

            lines = []
            if tspans:
                cur_y = base_y
                for ts in tspans:
                    tx = fnum(ts.get("x"), base_x) if ts.get("x") is not None else base_x
                    dy = fnum(ts.get("dy"))
                    if ts.get("y") is not None:
                        cur_y = fnum(ts.get("y"))
                    else:
                        cur_y += dy
                    txt = "".join(ts.itertext())
                    lines.append((tx, cur_y, txt))
            else:
                lines.append((base_x, base_y, visible))

            x0 = y0 = float("inf")
            x1 = y1 = float("-inf")
            for lx, ly, txt in lines:
                w = vw_of(txt) * size
                if anchor == "middle":
                    left, right = lx - w / 2, lx + w / 2
                elif anchor == "end":
                    left, right = lx - w, lx
                else:
                    left, right = lx, lx + w
                top = ly - size * ASCENT_RATIO
                bot = ly + size * DESCENT_RATIO
                x0, y0 = min(x0, left), min(y0, top)
                x1, y1 = max(x1, right), max(y1, bot)
            if x0 == float("inf"):
                continue
            label = visible if len(visible) <= 26 else visible[:25] + "…"
            els.append(El("text", gid, label, (x0, y0, x1, y1), ok))

        elif tag == "rect":
            x, y = fnum(el.get("x")), fnum(el.get("y"))
            w, h = fnum(el.get("width")), fnum(el.get("height"))
            if w <= 0 or h <= 0:
                continue
            els.append(El("shape", gid, f"rect({w:.0f}×{h:.0f})",
                          (x, y, x + w, y + h), ok))

        elif tag == "circle":
            cx, cy, r = fnum(el.get("cx")), fnum(el.get("cy")), fnum(el.get("r"))
            if r <= 0:
                continue
            els.append(El("shape", gid, f"circle(r={r:.0f})",
                          (cx - r, cy - r, cx + r, cy + r), ok))

        elif tag in ("polyline", "polygon"):
            bb = points_bbox(el.get("points"))
            if bb:
                els.append(El("shape", gid, tag, bb, ok))

        elif tag == "line":
            x1_, y1_ = fnum(el.get("x1")), fnum(el.get("y1"))
            x2_, y2_ = fnum(el.get("x2")), fnum(el.get("y2"))
            sw = fnum(el.get("stroke-width"), 1.0)
            # 轴对齐线退化为零面积 → 按线宽补厚度，避免"线与字相交"漏检
            pad = max(sw / 2.0, 0.5)
            els.append(El("shape", gid, "line",
                          (min(x1_, x2_) - pad, min(y1_, y2_) - pad,
                           max(x1_, x2_) + pad, max(y1_, y2_) + pad), ok))

    return els


# ---------------------------------------------------------------------------
# 重叠判定
# ---------------------------------------------------------------------------

def area(box) -> float:
    x0, y0, x1, y1 = box
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def inter_area(a, b) -> float:
    return max(0.0, min(a[2], b[2]) - max(a[0], b[0])) * \
           max(0.0, min(a[3], b[3]) - max(a[1], b[1]))


def same_family(g1: str, g2: str) -> bool:
    """同组即放行（含两者都无 id 的根级元素）。"""
    return g1 == g2


# ---------------------------------------------------------------------------
# text × shape 的判据：区分「底纹」与「数据标记」
# ---------------------------------------------------------------------------
# 卡内写"同组内文本-图形重叠合法（深色格反白字、色块上的标签）"，
# 但实测发现**跨组**的文本-图形重叠也大量合法，且是刻意设计：
#   · v2/cover-bold：白色标题压在 bold-geometry 的 520×720 蓝色块上（不同组）
#   · bullet/bar：数值标签压在柱体/轨道条上
# 若一律上报，正样本会产生大量误报（实测 T-02 报 3 处、T-04 报 2 处，全为设计意图）。
#
# 真正的病灶是 C-015：**图例线/点**（细笔画标记）压住了轴标签文字。
# 故判据为——**只有"标记类"图形才与文本比对**：
#   · line / circle / polyline / polygon  → 标记类（细笔画、按数据定位）
#   · rect → 仅当面积 < 文本 bbox 面积 × BACKDROP_RATIO 时算标记类；
#            否则视为**底纹/面板**（刻意承载其上文字），放行
BACKDROP_RATIO = 3.0


def is_mark_like(el: El, text_area: float) -> bool:
    """该图形是否属于"标记类"（值得与文本做重叠判定）。"""
    if el.kind != "shape":
        return False
    label = el.label
    if label.startswith("rect("):
        return area(el.box) < text_area * BACKDROP_RATIO
    return True          # line / circle / polyline / polygon 一律算标记类


def check_dir(svg_dir: str, threshold: float, verbose: bool = False):
    files = sorted(glob.glob(os.path.join(svg_dir, "**", "*.svg"), recursive=True))
    findings, stats = [], {"files": 0, "elements": 0, "text": 0, "shape": 0}
    for path in files:
        stats["files"] += 1
        try:
            els = collect(path)
        except ET.ParseError as e:
            findings.append({
                "file": os.path.basename(path), "kind": "PARSE_ERROR",
                "a": str(e), "b": "", "ratio": 1.0,
                "detail": "SVG 解析失败",
            })
            continue
        stats["elements"] += len(els)
        stats["text"] += sum(1 for e in els if e.kind == "text")
        stats["shape"] += sum(1 for e in els if e.kind == "shape")

        for i in range(len(els)):
            for j in range(i + 1, len(els)):
                A, B = els[i], els[j]
                if A.ok or B.ok:
                    continue
                if same_family(A.gid, B.gid):
                    continue
                # 只关心"至少一个是文本"，且不比对 图形×图形
                if A.kind == "shape" and B.kind == "shape":
                    continue
                # text × shape：图形必须是"标记类"；底纹/面板刻意承载文字，放行
                if A.kind == "shape" and not is_mark_like(A, area(B.box)):
                    continue
                if B.kind == "shape" and not is_mark_like(B, area(A.box)):
                    continue
                ia = inter_area(A.box, B.box)
                if ia <= 0:
                    continue
                smaller = min(area(A.box), area(B.box))
                if smaller <= 0:
                    continue
                ratio = ia / smaller
                if ratio <= threshold:
                    continue
                findings.append({
                    "file": os.path.basename(path),
                    "kind": ("text×text" if A.kind == B.kind == "text"
                             else "text×shape"),
                    "groupA": A.gid or "(root)", "a": A.label,
                    "groupB": B.gid or "(root)", "b": B.label,
                    "ratio": round(ratio, 4),
                    "overlap_px2": round(ia, 1),
                    "smaller_px2": round(smaller, 1),
                    "detail": f"{A.gid or '(root)'} × {B.gid or '(root)'}",
                })
    return findings, stats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="跨组重叠检查器（T-FIX5）")
    ap.add_argument("svg_dir", help="待检查的 SVG 目录（如项目的 svg_output）")
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                    help=f"重叠面积/较小者面积 的报警阈值（默认 {DEFAULT_THRESHOLD}）")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("-o", "--out", help="JSON 报告输出路径")
    ap.add_argument("--verbose", action="store_true", help="打印全部命中")
    a = ap.parse_args(argv)

    if not os.path.isdir(a.svg_dir):
        print(f"[ERROR] 目录不存在：{a.svg_dir}", file=sys.stderr)
        return 2

    findings, stats = check_dir(a.svg_dir, a.threshold, a.verbose)
    failed = bool(findings)

    result = {
        "status": "failed" if failed else "passed",
        "threshold": a.threshold,
        "scanned_files": stats["files"],
        "elements": {"total": stats["elements"],
                     "text": stats["text"], "shape": stats["shape"]},
        "findings_count": len(findings),
        "findings": findings,
        "exit_code": 2 if failed else 0,
    }

    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    print(f"\n[Overlap] 扫描 {stats['files']} 个 SVG；"
          f"元素 {stats['elements']}（文本 {stats['text']} / 图形 {stats['shape']}）；"
          f"阈值 {a.threshold:.0%}")
    if failed:
        print(f"[FAIL] 发现 {len(findings)} 处跨组重叠（P1）：")
        shown = findings if a.verbose else findings[:40]
        for f in shown:
            print(f"  [P1] {f['file']}: [{f['groupA']}] {f['a']!r} × "
                  f"[{f['groupB']}] {f['b']!r} — 重叠 {f['ratio']:.0%}")
        if not a.verbose and len(findings) > 40:
            print(f"  … 其余 {len(findings)-40} 处见 JSON 报告")
        print("\n修复：把相撞元素移到不同行/列，或对刻意叠放的元素标注 "
              f'{OK_OVERLAP_ATTR}="true"。')
    else:
        print("[OK] 未发现跨组重叠。")
    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
