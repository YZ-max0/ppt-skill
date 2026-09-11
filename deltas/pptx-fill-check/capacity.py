#!/usr/bin/env python3
"""Compute geometry-accurate text capacity for every text-bearing shape in a
filled .pptx.

D-2 (repo-level delta) capacity extractor. Unlike the vendored template-fill
analyzer, this tool reads the *filled output* directly (no detail.json) and is
used by the post-fill quality check (detect_overflow.py).

For every text shape it records:
  - slide / shape_id / name / placeholder role
  - box_cm: [width_cm, height_cm] (None when degenerate/unmeasurable)
  - font_size_pt: resolved effective size for the first non-empty paragraph
  - autofit: whether PowerPoint is allowed to shrink text on overflow
  - wrap: whether the text frame wraps
  - cpl: approximate visual-width units per line at the resolved size
  - max_lines: estimated number of lines that fit the box height
  - capacity_vw: cpl * max_lines (raw geometry budget, before tolerance)

Visual width units (vw) follow the same convention as the vendored pipeline:
CJK / fullwidth = 1.0, ASCII latin/digit = 0.5, space = 0.35, other = 0.8.
One vw unit is roughly one em at the resolved font size, which lets a simple
width/height budget approximate text fit without a rendering engine.

Implementation is self-written from the D-2 task contract. The vw weighting and
the inheritance-resolution approach are design conventions established by the
Gorden MIT reference; no Gorden text is copied verbatim.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import MSO_AUTO_SIZE

EMU_PER_CM = 360000
PT_PER_CM = 28.3465
# Default text-frame insets used only when a shape exposes no explicit inset.
# PowerPoint body placeholders commonly inset ~0.1-0.25 cm; a single combined
# value keeps the budget conservative without per-shape XML spelunking.
H_INSET_CM = 0.25
V_INSET_CM = 0.08
LINE_HEIGHT = 1.0  # CJK body is effectively single-spaced at this resolution

A_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


def vw_of(text: str) -> float:
    """Visual width of a single line in vw units (no line-break handling)."""
    w = 0.0
    for ch in text:
        if (
            "\u4e00" <= ch <= "\u9fff"
            or "\u3000" <= ch <= "\u303f"
            or "\uff00" <= ch <= "\uffef"
        ):
            w += 1.0
        elif ch == " ":
            w += 0.35
        elif ch.isascii():
            w += 0.5
        else:
            w += 0.8
    return w


def iter_text_shapes(shapes):
    """Yield shapes that have a text frame, recursing into groups."""
    for shape in shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from iter_text_shapes(shape.shapes)
        elif getattr(shape, "has_text_frame", False):
            yield shape


def _def_rpr_size_from_lst_style(el, level):
    """Return a:defRPr@sz (pt) from a:lstStyle/a:lvlNpPr, if present."""
    if el is None:
        return None
    lst = None
    if el.tag.endswith("lstStyle"):
        lst = el
    else:
        lst = el.find(f"{A_NS}lstStyle")
        if lst is None:
            tx_body = el.find(f".//{A_NS}txBody")
            if tx_body is not None:
                lst = tx_body.find(f"{A_NS}lstStyle")
    if lst is None:
        return None
    lvl = lst.find(f"{A_NS}lvl{level + 1}pPr")
    if lvl is None:
        return None
    def_rpr = lvl.find(f"{A_NS}defRPr")
    if def_rpr is not None and def_rpr.get("sz") is not None:
        return int(def_rpr.get("sz")) / 100.0
    return None


def _master_tx_style_size(master, ph_type, level):
    """Return master txStyles title/body/other defRPr size for a level."""
    tx_styles = master._element.find(f"{A_NS}txStyles")
    if tx_styles is None:
        return None
    t = str(ph_type) if ph_type is not None else ""
    if "TITLE" in t or "CENTER_TITLE" in t or "ctrTitle" in t.lower():
        bucket = "titleStyle"
    elif "BODY" in t or "SUBTITLE" in t or "OBJECT" in t:
        bucket = "bodyStyle"
    else:
        bucket = "otherStyle"
    style = tx_styles.find(f"{A_NS}{bucket}")
    if style is None:
        return None
    lvl = style.find(f"{A_NS}lvl{level + 1}pPr")
    if lvl is None:
        return None
    def_rpr = lvl.find(f"{A_NS}defRPr")
    if def_rpr is not None and def_rpr.get("sz") is not None:
        return int(def_rpr.get("sz")) / 100.0
    return None


def resolve_size_pt(shape, paragraph, slide, role=""):
    """Resolve the effective font size (pt) for a paragraph.

    Order:
      1. explicit paragraph/run size (caller usually handles it; kept here for
         a complete API)
      2. placeholder inheritance: layout placeholder -> master placeholder
      3. master txStyles by placeholder type + level
      4. role-name default
      5. box-height heuristic
    """
    try:
        if paragraph.font.size is not None:
            return paragraph.font.size.pt
    except Exception:
        pass

    level = getattr(paragraph, "level", 0) or 0
    ph_type = None
    ph_idx = None
    try:
        if shape.is_placeholder:
            ph_type = shape.placeholder_format.type
            ph_idx = shape.placeholder_format.idx
    except Exception:
        pass

    if ph_idx is not None:
        layout = slide.slide_layout
        master = layout.slide_master
        for container in (layout, master):
            try:
                for ph in container.placeholders:
                    if ph.placeholder_format.idx == ph_idx:
                        sz = _def_rpr_size_from_lst_style(ph._element, level)
                        if sz:
                            return sz
            except Exception:
                pass
        sz = _master_tx_style_size(master, ph_type, level)
        if sz:
            return sz

    r = role or ""
    if "主标题" in r or "页面标题" in r:
        return 32.0
    if "段落标题" in r or "副标题" in r or "小标题" in r:
        return 18.0
    if "正文" in r:
        return 13.0

    try:
        h_cm = shape.height / EMU_PER_CM
        return max(10.0, min(40.0, h_cm * PT_PER_CM / 1.4))
    except Exception:
        return 14.0


def capacity_for(width_cm, height_cm, size_pt, wrap):
    """Return (cpl, max_lines, capacity_vw) raw geometry budget."""
    usable_w_pt = max(0.0, (width_cm - H_INSET_CM)) * PT_PER_CM
    usable_h_pt = max(0.0, (height_cm - V_INSET_CM)) * PT_PER_CM
    if size_pt <= 0:
        size_pt = 14.0
    cpl = max(1, math.floor(usable_w_pt / size_pt))
    max_lines = 1 if not wrap else max(1, math.floor(usable_h_pt / (size_pt * LINE_HEIGHT)))
    return cpl, max_lines, max(1, math.floor(cpl * max_lines))


def _para_size_pt(para):
    """Explicit size of a paragraph or its first run, else None."""
    try:
        if para.font.size is not None:
            return para.font.size.pt
    except Exception:
        pass
    for run in para.runs:
        try:
            if run.font.size is not None:
                return run.font.size.pt
        except Exception:
            pass
    return None


def extract_pptx(path):
    """Extract capacity records for every text shape in the deck."""
    prs = Presentation(str(path))
    records = []
    for slide_index, slide in enumerate(prs.slides, start=1):
        for shape in iter_text_shapes(slide.shapes):
            tf = shape.text_frame
            rec = {
                "slide": slide_index,
                "shape_id": getattr(shape, "shape_id", None),
                "name": getattr(shape, "name", ""),
                "role": "",
                "text": tf.text,
                "box_cm": None,
                "font_size_pt": None,
                "autofit": False,
                "wrap": True,
                "cpl": None,
                "max_lines": None,
                "capacity_vw": None,
                "paragraphs": [],
            }
            try:
                if shape.is_placeholder:
                    rec["role"] = str(shape.placeholder_format.type)
            except Exception:
                pass
            try:
                w_cm = shape.width / EMU_PER_CM
                h_cm = shape.height / EMU_PER_CM
                if w_cm >= 1.0 and h_cm >= 0.3:
                    rec["box_cm"] = [round(w_cm, 2), round(h_cm, 2)]
            except Exception:
                pass

            try:
                wrap = tf.word_wrap
                rec["wrap"] = True if wrap is None else bool(wrap)
            except Exception:
                pass
            try:
                rec["autofit"] = tf.auto_size == MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
            except Exception:
                pass

            para = next((p for p in tf.paragraphs if p.text.strip()), None)
            if para is None:
                records.append(rec)
                continue

            size_pt = _para_size_pt(para)
            if size_pt is None:
                size_pt = resolve_size_pt(shape, para, slide, rec["role"])
            size_pt = round(size_pt * 2) / 2
            rec["font_size_pt"] = size_pt

            if rec["box_cm"] is not None:
                cpl, max_lines, capacity = capacity_for(
                    rec["box_cm"][0], rec["box_cm"][1], size_pt, rec["wrap"]
                )
                rec["cpl"] = cpl
                rec["max_lines"] = max_lines
                rec["capacity_vw"] = capacity

            for p in tf.paragraphs:
                if not p.text.strip():
                    continue
                p_size = _para_size_pt(p) or size_pt
                total_vw = vw_of(p.text)
                need = (
                    max(1, math.ceil(total_vw / rec["cpl"]))
                    if rec["cpl"]
                    else 1
                )
                rec["paragraphs"].append(
                    {
                        "text": p.text,
                        "vw": round(total_vw, 1),
                        "font_size_pt": round(p_size * 2) / 2,
                        "needed_lines": need,
                    }
                )
            records.append(rec)
    return records


def render_text(records):
    """Render a human-readable summary of extracted records."""
    lines = []
    for r in records:
        box = f"{r['box_cm'][0]}x{r['box_cm'][1]}cm" if r["box_cm"] else "unknown-box"
        mode = "autofit" if r["autofit"] else ("nowrap" if not r["wrap"] else "wrap")
        lines.append(
            f"[shape] page {r['slide']} id={r['shape_id']} name={r['name']!r} "
            f"role={r['role'] or '-'} box={box} size={r['font_size_pt']}pt "
            f"mode={mode} cpl={r['cpl']} max_lines={r['max_lines']} "
            f"capacity_vw={r['capacity_vw']}"
        )
        for p in r["paragraphs"]:
            lines.append(
                f"    para: {p['text'][:40]!r} vw={p['vw']} "
                f"size={p['font_size_pt']} need_lines={p['needed_lines']}"
            )
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Extract per-shape text capacity from a filled .pptx (D-2)."
    )
    ap.add_argument("pptx", type=Path, help="filled .pptx to analyze")
    ap.add_argument("-o", "--output", type=Path, help="optional JSON output path")
    args = ap.parse_args(argv)

    if not args.pptx.exists():
        print(f"[ERROR] file not found: {args.pptx}", file=sys.stderr)
        return 2

    records = extract_pptx(args.pptx)
    print(render_text(records))
    if args.output:
        args.output.write_text(
            json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"[INFO] wrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
