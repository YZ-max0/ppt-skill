#!/usr/bin/env python3
"""Check same-level title font-size consistency in a filled .pptx (D-2).

Goal (from the D-2 contract, executable form): when a fill run changes text,
it must not silently change the font size of same-level titles. Same-level
means the same placeholder role / layout title tier within a page. The check
reports P1 when same-level titles on the same page differ by more than 0.5 pt
(after collapsing to a 0.5 pt grid), which signals that one title was edited
out of the template's type scale.

Approach:
  - Reuse capacity.py's text-shape iterator + placeholder role reader.
  - A "suspected title" shape is one whose placeholder role contains TITLE /
    CENTER_TITLE / ctrTitle, or a non-placeholder whose first non-empty
    paragraph's resolved size >= 18 pt and text length <= 16 chars.
  - Titles are clustered per page by their placeholder *tier* (title vs
    subtitle-ish) because same-level means same slot tier. For each page, for
    each tier with at least two shapes, the check compares sizes:
        difference > 0.5 pt  -> P1
    It also reports, cross-page, any title tier whose size deviates from the
    page's most common size for that tier (the "template slot size") by more
    than 0.5 pt -> P1 (this catches one-off size edits).

Severity: all findings are P1 (informational advisory) because only a human can
decide whether a deliberate exception is justified. Exit code is 0 when no
inconsistency is found; 2 when any is found.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from capacity import iter_text_shapes, resolve_size_pt
from pptx import Presentation

DIFF_PT = 0.5  # allowed same-level spread after 0.5pt grid collapse
TITLE_LEN_MAX = 16
TITLE_SIZE_MIN = 18.0


def _role_of(shape) -> str:
    try:
        if shape.is_placeholder:
            return str(shape.placeholder_format.type)
    except Exception:
        pass
    return ""


def _is_subtitle_role(role: str) -> bool:
    r = role.upper()
    return "SUBTITLE" in r or "SUB_TITLE" in r


def _is_title_role(role: str) -> bool:
    # SUBTITLE contains TITLE, so subtitles must be excluded first
    r = role.upper()
    return not _is_subtitle_role(r) and ("TITLE" in r or "CTRTITLE" in r)


def _tier(role: str) -> str:
    """Return a same-level key: concrete placeholder kind when possible.

    CENTER_TITLE / TITLE / SUBTITLE are different template tiers and must not
    be compared with each other. Non-placeholder heading-like shapes fall back
    to a shape-role key so only truly same-kind shapes are compared.
    """
    r = role.upper()
    # strip python-pptx enum suffix like "CENTER_TITLE (3)"
    base = r.split("(")[0].strip()
    # SUBTITLE contains TITLE, so match the more specific names first
    for known in ("CENTER_TITLE", "CTRTITLE", "SUBTITLE", "TITLE", "BODY", "OBJECT"):
        if known in base:
            return known.lower()
    return f"shape:{role or 'text'}"


def _first_para(shape):
    tf = shape.text_frame
    return next((p for p in tf.paragraphs if p.text.strip()), None)


def _shape_size_pt(shape, para, slide):
    """Resolved effective font size for a paragraph (0.5 pt grid)."""
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
        size_pt = resolve_size_pt(shape, para, slide, _role_of(shape))
    return round(size_pt * 2) / 2


def _looks_like_title(shape, para, size_pt) -> bool:
    role = _role_of(shape)
    if _is_title_role(role) or _is_subtitle_role(role):
        return True
    # heuristic for non-placeholder heading-like shapes
    text_len = len(para.text.strip())
    return text_len <= TITLE_LEN_MAX and size_pt >= TITLE_SIZE_MIN


def collect_titles(pptx_path: Path):
    """Return list of title candidate dicts."""
    prs = Presentation(str(pptx_path))
    titles = []
    for slide_index, slide in enumerate(prs.slides, start=1):
        for shape in iter_text_shapes(slide.shapes):
            tf = shape.text_frame
            para = _first_para(shape)
            if para is None:
                continue
            role = _role_of(shape)
            size_pt = _shape_size_pt(shape, para, slide)
            if not _looks_like_title(shape, para, size_pt):
                continue
            titles.append(
                {
                    "slide": slide_index,
                    "shape_id": getattr(shape, "shape_id", None),
                    "name": getattr(shape, "name", ""),
                    "role": role,
                    "tier": _tier(role),
                    "size_pt": size_pt,
                    "text": para.text.strip(),
                }
            )
    return titles


def detect(titles):
    """Return list of P1 findings."""
    findings = []

    # --- same-page same-tier spread ---
    by_page_tier = defaultdict(list)
    for t in titles:
        by_page_tier[(t["slide"], t["tier"])].append(t)

    for (slide, tier), group in by_page_tier.items():
        if len(group) < 2:
            continue
        sizes = sorted({t["size_pt"] for t in group})
        if len(sizes) < 2:
            continue
        spread = sizes[-1] - sizes[0]
        if spread > DIFF_PT:
            findings.append(
                {
                    "severity": "P1",
                    "slide": slide,
                    "tier": tier,
                    "kind": "same_page_tier_spread",
                    "detail": (
                        f"同页同级标题字号差 {spread}pt > {DIFF_PT}pt "
                        f"(sizes={sizes})"
                    ),
                    "shapes": [
                        {
                            "shape_id": t["shape_id"],
                            "name": t["name"],
                            "size_pt": t["size_pt"],
                            "text": t["text"][:30],
                        }
                        for t in sorted(group, key=lambda x: -x["size_pt"])
                    ],
                }
            )

    # --- cross-page template-tier deviation ---
    # For each tier, the most common size across pages is the "template" size.
    # Any title whose size deviates from that tier's common size by more than
    # DIFF_PT is flagged, regardless of whether a sibling on the same page keeps
    # the common size (no keeper prerequisite).
    tier_sizes = defaultdict(list)
    for t in titles:
        tier_sizes[t["tier"]].append(t["size_pt"])
    common = {}
    for tier, sizes in tier_sizes.items():
        if sizes:
            common[tier] = Counter(sizes).most_common(1)[0][0]

    for (slide, tier), group in by_page_tier.items():
        if tier not in common:
            continue
        baseline = common[tier]
        devs = [t for t in group if abs(t["size_pt"] - baseline) > DIFF_PT]
        if devs:
            for t in devs:
                findings.append(
                    {
                        "severity": "P1",
                        "slide": slide,
                        "tier": tier,
                        "kind": "off_template_tier_size",
                        "detail": (
                            f"标题 {t['text'][:20]!r} 字号 {t['size_pt']}pt 偏离该级"
                            f"常规 {baseline}pt（差 {abs(t['size_pt'] - baseline)}pt）"
                        ),
                        "shape_id": t["shape_id"],
                        "size_pt": t["size_pt"],
                        "text": t["text"][:40],
                    }
                )
    return findings


def render(findings):
    if not findings:
        return "[OK] 未发现同级标题字号不一致。"
    lines = []
    for f in findings:
        lines.append(f"[P1] 页{f['slide']} {f['tier']}: {f['detail']}")
        if f.get("shapes"):
            for s in f["shapes"]:
                lines.append(
                    f"      - {s['name']!r} (id={s['shape_id']}) "
                    f"{s['size_pt']}pt: {s['text']!r}"
                )
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Check same-level title font-size consistency (D-2)."
    )
    ap.add_argument("pptx", type=Path, help="filled .pptx to check")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("-o", "--output", type=Path, help="optional JSON output path")
    args = ap.parse_args(argv)

    if not args.pptx.exists():
        print(f"[ERROR] file not found: {args.pptx}", file=sys.stderr)
        return 1

    titles = collect_titles(args.pptx)
    findings = detect(titles)

    if args.json or args.output:
        payload = {
            "source": str(args.pptx),
            "title_count": len(titles),
            "p1_count": len(findings),
            "findings": findings,
            "titles": titles,
        }
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.output:
            args.output.write_text(text, encoding="utf-8")
        if args.json:
            print(text)
    else:
        print(render(findings))
        print(f"=== 摘要: {len(findings)} 处 P1（标题一致性） ===")
    return 2 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
