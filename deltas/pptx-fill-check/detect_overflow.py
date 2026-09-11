#!/usr/bin/env python3
"""Post-fill overflow detector for a filled .pptx (D-2).

Reads the physical geometry of every text shape in the finished deck and
estimates whether the placed text fits its box. This complements the vendored
template-fill `check-plan` (pre-fill budget): it checks the actual filled
product and catches cases where the pre-fill budget said "fits" but the real
geometry/autofit state still risks overflow.

Judgment (unified with the Gorden MIT reference tolerance; the 1.2
default below is overridable via --tolerance):

  usage = total paragraph vw / box capacity_vw        (both from capacity.py)
    usage <  1.0            -> OK (raw geometry fits)
    1.0 <= usage <= 1.2     -> OK (within the 20% model slack) when autofit is
                               off; reported as P1 informational when the text
                               is long enough to be worth a human glance
    usage >  1.2            -> P0 (likely overflow) when autofit is off
    any autofit=on overflow -> soft-pass note: PowerPoint will shrink text, so
                               it is informational, not a P0 blocker

Severity mapping used by the CLI exit code:
  exit 0 = no P0
  exit 2 = at least one P0
(exit 1 reserved for runtime errors)

The px-based remedy ladder is advisory copy only:
  <=40px 微调 / 40-90 压间距 / 90-160 压标题 / 160+ 换版式.
It is intentionally not computed from pixel rendering (no renderer is used);
it is guidance text for the author.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from capacity import (
    capacity_for,
    extract_pptx,
    iter_text_shapes,
    resolve_size_pt,
    vw_of,
)
from pptx import Presentation
from pptx.enum.text import MSO_AUTO_SIZE

TOLERANCE = 1.2  # 20% model slack, matches the vendored calibration


def para_vw(text: str) -> float:
    """Visual width of a single paragraph line set (sum over its visual lines)."""
    # We intentionally count each explicit line break as a separate line later;
    # here return raw width of the whole paragraph (caller splits on "\n").
    return vw_of(text)


def needed_lines_for(text: str, cpl: int) -> int:
    """Approximate line count for a paragraph given chars-per-line budget."""
    if not text:
        return 0
    if not cpl or cpl <= 0:
        return 1
    segs = text.split("\n") or [text]
    return sum(max(1, math.ceil(vw_of(seg) / cpl)) for seg in segs)


def first_para_text(shape) -> str:
    tf = shape.text_frame
    for p in tf.paragraphs:
        if p.text.strip():
            return p.text
    return tf.text


def diagnose(shape, slide_index, size_pt, capacity, text, wrap, autofit,
             tolerance: float = TOLERANCE):
    """Return a dict describing one text shape's fit diagnosis."""
    cpl, max_lines, capacity_vw = capacity
    segs = text.split("\n") or [text]
    # demand measured against the *raw* capacity (pre-tolerance)
    demand = sum(max(1, math.ceil(vw_of(seg) / cpl)) for seg in segs)
    usage = demand / max_lines if max_lines else float("inf")

    # ---- decide severity ----
    if autofit:
        severity = "OK"  # soft pass; note below explains auto-shrink
        code = "autofit"
        note = "autofit on: PowerPoint may shrink text automatically"
    else:
        if usage <= 1.0:
            severity, code = "OK", "fits"
            note = ""
        elif usage <= tolerance:
            # within the 20% slack: fits by the model, but flag for a human look
            severity, code = "P1", "tight"
            note = "within model slack but worth a visual check"
        else:
            severity, code = "P0", "overflow"
            note = "exceeds box capacity by >20%; expected to overflow"

    # paragraph summary (first 24 chars, single line)
    one_line = text.replace("\n", " ")
    if len(one_line) > 24:
        summary = one_line[:24] + "…"
    else:
        summary = one_line

    return {
        "slide": slide_index,
        "shape_id": getattr(shape, "shape_id", None),
        "name": getattr(shape, "name", ""),
        "text": text,
        "summary": summary,
        "severity": severity,
        "code": code,
        "note": note,
        "font_size_pt": size_pt,
        "box_cm": (
            [round(shape.width / 360000, 2), round(shape.height / 360000, 2)]
            if shape.width and shape.height
            else None
        ),
        "wrap": wrap,
        "autofit": autofit,
        "cpl": cpl,
        "max_lines": max_lines,
        "demand_lines": demand,
        "usage": round(usage, 2) if math.isfinite(usage) else None,
        "remedy": remedy_hint(usage, autofit),
    }


def remedy_hint(usage, autofit):
    """Advisory remedy ladder (copy only; no pixel measurement)."""
    if autofit:
        return "PowerPoint auto-shrink is enabled; confirm visual result"
    if usage <= 1.0:
        return ""
    if usage <= 1.2:
        return "建议删减字数或微调（≤40px 量级）"
    if usage <= 1.6:
        return "建议压缩间距/删减内容（40-90px 量级）"
    if usage <= 2.2:
        return "建议压标题或换行控制（90-160px 量级）"
    return "建议更换版式或拆分内容（160px+ 量级）"


def run_detect(pptx_path: Path, tolerance: float = TOLERANCE):
    """Return (diagnoses, p0_count, p1_count, ok_count)."""
    prs = Presentation(str(pptx_path))
    diagnoses = []
    for slide_index, slide in enumerate(prs.slides, start=1):
        for shape in iter_text_shapes(slide.shapes):
            tf = shape.text_frame
            if not tf.text.strip():
                continue
            # per-shape resolved size (first non-empty para)
            para = next((p for p in tf.paragraphs if p.text.strip()), None)
            if para is None:
                continue
            size_pt = None
            try:
                if para.font.size is not None:
                    size_pt = para.font.size.pt
            except Exception:
                pass
            if size_pt is None:
                for run in para.runs:
                    try:
                        if run.font.size is not None:
                            size_pt = run.font.size.pt
                            break
                    except Exception:
                        pass
            if size_pt is None:
                role = ""
                try:
                    if shape.is_placeholder:
                        role = str(shape.placeholder_format.type)
                except Exception:
                    pass
                size_pt = resolve_size_pt(shape, para, slide, role)
            size_pt = round(size_pt * 2) / 2

            wrap = True
            try:
                w = tf.word_wrap
                wrap = True if w is None else bool(w)
            except Exception:
                pass
            autofit = False
            try:
                autofit = tf.auto_size == MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
            except Exception:
                pass

            w_cm = None
            h_cm = None
            try:
                w_cm = shape.width / 360000
                h_cm = shape.height / 360000
            except Exception:
                pass
            if w_cm is None or h_cm is None or w_cm < 1.0 or h_cm < 0.3:
                # degenerate/group child/unmeasurable: skip silently
                continue
            cap = capacity_for(w_cm, h_cm, size_pt, wrap)
            text = tf.text
            diag = diagnose(shape, slide_index, size_pt, cap, text, wrap,
                             autofit, tolerance)
            diagnoses.append(diag)
    p0 = [d for d in diagnoses if d["severity"] == "P0"]
    p1 = [d for d in diagnoses if d["severity"] == "P1"]
    ok = [d for d in diagnoses if d["severity"] == "OK"]
    return diagnoses, len(p0), len(p1), len(ok)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Detect text overflow in a filled .pptx (D-2 post-fill check)."
    )
    ap.add_argument("pptx", type=Path, help="filled .pptx to check")
    ap.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON diagnostics instead of human text",
    )
    ap.add_argument("-o", "--output", type=Path, help="optional JSON output path")
    ap.add_argument(
        "--tolerance",
        type=float,
        default=TOLERANCE,
        help="overflow tolerance multiplier (default 1.2, matches vendored calibration)",
    )
    args = ap.parse_args(argv)

    if not args.pptx.exists():
        print(f"[ERROR] file not found: {args.pptx}", file=sys.stderr)
        return 1

    diagnoses, p0_n, p1_n, ok_n = run_detect(args.pptx, args.tolerance)

    if args.json or args.output:
        payload = {
            "source": str(args.pptx),
            "p0_count": p0_n,
            "p1_count": p1_n,
            "ok_count": ok_n,
            "items": diagnoses,
        }
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.output:
            args.output.write_text(text, encoding="utf-8")
        if args.json:
            print(text)
    else:
        for d in diagnoses:
            line = (
                f"[{d['severity']}] 页{d['slide']} 形状:{d['summary']} | "
                f"需求 {d['demand_lines']} 行，容量 {d['max_lines']} 行 "
                f"(cpl={d['cpl']}, {d['font_size_pt']}pt)"
            )
            if d["code"] == "autofit":
                line += f" | autofit 软放行: {d['note']}"
            elif d["code"] == "overflow":
                line += f" | 超出容量 >20% (usage={d['usage']})"
            elif d["code"] == "tight":
                line += f" | 接近上限 (usage={d['usage']})"
            if d.get("remedy"):
                line += f" | 建议: {d['remedy']}"
            print(line)
        print(f"=== 摘要: {p0_n} 处 P0 / {p1_n} 处 P1 / {ok_n} 处 OK ===")

    return 2 if p0_n > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
