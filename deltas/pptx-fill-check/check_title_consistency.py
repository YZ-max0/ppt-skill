#!/usr/bin/env python3
"""Check same-level title font-size consistency in a filled .pptx (D-2).

Two judgment paths run side by side, chosen per shape:

* **Placeholder path** (template-fill output): a shape's placeholder role
  defines its tier (CENTER_TITLE / TITLE / SUBTITLE / BODY / OBJECT).
* **Free-design path** (quick / flat output, no roles): titles are grouped by
  font-size bucket via ``assign_size_buckets`` (gap configurable with
  ``--size-bucket-gap``), so a 48pt cover title is never compared with 18pt
  body labels. See that function for the known boundary of this method.

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

from capacity import iter_text_shapes, resolve_size_pt, vw_of
from pptx import Presentation

DIFF_PT = 0.5  # allowed same-level spread after 0.5pt grid collapse
TITLE_LEN_MAX = 16
TITLE_SIZE_MIN = 18.0
# Non-placeholder (free-design) titles carry no role information, so they are
# grouped into font-size buckets instead of a single catch-all tier. Two sizes
# belong to the same bucket while neighbouring sorted sizes stay within this gap.
SIZE_BUCKET_GAP_DEFAULT = 4.0
# Free-design (size-bucket) tiers only: a cross-page size deviation is reported
# when the bucket's dominant size covers at least this share of the bucket.
# Below it the bucket has no reliable "regular" size, so its members are treated
# as several distinct text roles sharing one bucket rather than drift.
# Placeholder tiers are role ground truth and skip this prerequisite entirely.
DOMINANCE_MIN = 0.6


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


def _placeholder_tier(role: str) -> str:
    """Same-level key for shapes that expose a placeholder role.

    CENTER_TITLE / TITLE / SUBTITLE are different template tiers and must not be
    compared with each other (their sizes legitimately differ).
    """
    r = role.upper()
    # strip python-pptx enum suffix like "CENTER_TITLE (3)"
    base = r.split("(")[0].strip()
    # SUBTITLE contains TITLE, so match the more specific names first
    for known in ("CENTER_TITLE", "CTRTITLE", "SUBTITLE", "TITLE", "BODY", "OBJECT"):
        if known in base:
            return known.lower()
    return ""


def _is_placeholder_role(role: str) -> bool:
    """True when the role string yields a concrete placeholder tier."""
    return bool(_placeholder_tier(role))


def is_bucket_tier(tier: str) -> bool:
    """True when *tier* came from the free-design size-bucket path."""
    return tier.startswith("text@")


SEQ_MAX_LEN = 4      # "01", "1.", "(3)", "A", "IV"
SHORT_MAX_VW = 5.0   # CJK <=5 chars (or equivalent visual width)


def classify_subtier(text: str) -> str:
    """Classify one free-design title into a text-feature subtier.

    Same-bucket titles with different *roles* were the source of the C-004/C-007
    false positives (a 18pt explanatory sentence compared against a 21pt card
    label). Font size alone cannot separate them, but their shape can:

    ``seq``   — a numbering token: pure digits/letters, length <= SEQ_MAX_LEN
                (``01``, ``1.``, ``(3)``, ``A``). Card/section numbering.
    ``short`` — a non-numbering short label, visual width <= SHORT_MAX_VW
                (``风险``, ``对策``, ``验收标准``). Card titles and tags.
    ``long``  — everything else: subtitles and explanatory sentences.

    The subtier is a *heuristic*, not a semantic role. It deliberately only
    splits within one font-size bucket, so it cannot create or hide a
    cross-bucket finding.
    """
    t = (text or "").strip()
    if not t:
        return "long"
    # --- seq: numbering token ---
    if len(t) <= SEQ_MAX_LEN and not any(ch.isspace() for ch in t):
        stripped = t.strip("()（）[]【】.、,，:：-—_")
        # seq must be an ASCII numbering token. CJK labels like "风险" are also
        # str.isalpha(), so restrict to ASCII digits/letters explicitly.
        if stripped and stripped.isascii() and stripped.isalnum():
            if stripped.isdigit() or stripped.isalpha():
                return "seq"
    # --- short: brief label ---
    if vw_of(t) <= SHORT_MAX_VW:
        return "short"
    return "long"


def subtier_tier_label(low: float, high: float, subtier: str) -> str:
    """Bucket tier label including the text-feature subtier."""
    return f"{bucket_tier_label(low, high)}/{subtier}"


def bucket_tier_label(low: float, high: float) -> str:
    """Return the stable tier label for one closed font-size bucket."""
    def fmt(v: float) -> str:
        return str(int(v)) if float(v).is_integer() else str(v)
    if low == high:
        return f"text@{fmt(low)}"
    return f"text@{fmt(low)}-{fmt(high)}"


def assign_size_buckets(titles, gap: float = SIZE_BUCKET_GAP_DEFAULT) -> None:
    """Assign a size-derived tier to every non-placeholder title, in place.

    The deck's non-placeholder titles are sorted by size and split wherever the
    step to the next size exceeds ``gap``. Each run of neighbouring sizes forms
    one bucket, so a 48/42/30/24/21/18 deck yields several buckets and the
    cover title is never compared with body-size labels. Same-bucket drift
    (e.g. 28 -> 24 with a 4pt gap) stays detectable.

    Each bucket is further split by the text-feature subtier from
    :func:`classify_subtier` (``seq`` / ``short`` / ``long``), so a 18pt
    explanatory sentence is never compared against a 21pt card label even when
    both land in the same font-size bucket.

    Known limitation: a cross-bucket drift (e.g. one 28pt page title rewritten
    to 18pt) lands in a different bucket and is therefore NOT reported. Without
    role information there is no way to tell it apart from a legitimately
    smaller tier; this is the intrinsic boundary of bucket-based grouping.
    """
    non_ph = [t for t in titles if not _is_placeholder_role(t["role"])]
    if not non_ph:
        return
    sizes = sorted({t["size_pt"] for t in non_ph})
    buckets = []
    start = prev = sizes[0]
    for sz in sizes[1:]:
        if sz - prev > gap:
            buckets.append((start, prev))
            start = sz
        prev = sz
    buckets.append((start, prev))

    def bucket_of(size_pt: float):
        for low, high in buckets:
            if low <= size_pt <= high:
                return low, high
        return size_pt, size_pt

    for t in non_ph:
        low, high = bucket_of(t["size_pt"])
        sub = classify_subtier(t.get("text", ""))
        t["subtier"] = sub
        t["tier"] = subtier_tier_label(low, high, sub)


def _tier(role: str) -> str:
    """Return the placeholder-path tier for *role* (empty string when none).

    Retained for the placeholder path; non-placeholder titles get their tier
    from :func:`assign_size_buckets` after collection.
    """
    return _placeholder_tier(role)


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


def collect_titles(pptx_path: Path, size_bucket_gap: float = SIZE_BUCKET_GAP_DEFAULT):
    """Return list of title candidate dicts.

    Placeholder shapes keep their role-derived tier; every non-placeholder
    (free-design) title receives a size-bucket tier via
    :func:`assign_size_buckets`.
    """
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
                    "tier": _placeholder_tier(role) or "",
                    "size_pt": size_pt,
                    "text": para.text.strip(),
                }
            )
    assign_size_buckets(titles, size_bucket_gap)
    return titles


def detect(titles, dominance_min: float = DOMINANCE_MIN):
    """Return list of P1 findings.

    ``dominance_min`` is the minimum share the dominant size must hold in a
    free-design bucket before that bucket's size spread is treated as
    same-level drift. Placeholder tiers ignore it.
    """
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
        if spread <= DIFF_PT:
            continue
        # Same prerequisite as the cross-page path: a free-design (bucket) tier
        # only has a meaningful "same level" when one size dominates it. Two
        # candidates at 28pt and 24pt are distinct text roles sharing a bucket,
        # not a same-level inconsistency. Placeholder tiers are role ground
        # truth and skip this check entirely.
        if is_bucket_tier(tier):
            counts = Counter(t["size_pt"] for t in group)
            dominant_n = counts.most_common(1)[0][1]
            if dominant_n / len(group) < dominance_min:
                continue
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

    # --- cross-page tier deviation ---
    # The tier's dominant (most common) size is the reference "regular" size.
    # A title deviating from it by more than DIFF_PT is flagged, with no
    # same-page keeper prerequisite.
    #
    # De-duplication: a shape already named by a same-page spread finding is
    # skipped here. Both findings share one root cause, and reporting the same
    # title twice inflates the count without adding information.
    reported = {
        (f["slide"], sh["shape_id"])
        for f in findings
        if f.get("kind") == "same_page_tier_spread"
        for sh in f.get("shapes", [])
    }
    tier_sizes = defaultdict(list)
    for t in titles:
        tier_sizes[t["tier"]].append(t["size_pt"])

    for tier, sizes in tier_sizes.items():
        # The dominance prerequisite guards only the free-design bucket path.
        # A placeholder role is ground truth, so its tier is judged exactly as
        # before (a 2-member tier like {28, 30} must still report the 30).
        if is_bucket_tier(tier):
            if len(sizes) < 2:
                continue
            dominant_size, dominant_n = Counter(sizes).most_common(1)[0]
            dominance = dominant_n / len(sizes)
            if dominance < dominance_min:
                continue
        else:
            if not sizes:
                continue
            dominant_size = Counter(sizes).most_common(1)[0][0]
        for (slide, g_tier), group in by_page_tier.items():
            if g_tier != tier:
                continue
            devs = [
                t for t in group
                if abs(t["size_pt"] - dominant_size) > DIFF_PT
                and (slide, t["shape_id"]) not in reported
            ]
            for t in devs:
                findings.append(
                    {
                        "severity": "P1",
                        "slide": slide,
                        "tier": tier,
                        "kind": "off_template_tier_size",
                        "detail": (
                            f"标题 {t['text'][:20]!r} 字号 {t['size_pt']}pt 偏离该级"
                            f"常规 {dominant_size}pt（差 {abs(t['size_pt'] - dominant_size)}pt）"
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
    ap.add_argument(
        "--size-bucket-gap",
        type=float,
        default=SIZE_BUCKET_GAP_DEFAULT,
        help=("font-size clustering gap in pt for free-design (non-placeholder) "
              "titles; larger values merge more tiers (default 4.0)"),
    )
    ap.add_argument(
        "--dominance-min",
        type=float,
        default=DOMINANCE_MIN,
        help=("free-design buckets only: minimum share (0-1) the dominant size "
              "must hold before a spread/deviation is reported; lower values "
              "report more, higher values report less (default 0.6)"),
    )
    args = ap.parse_args(argv)

    if not args.pptx.exists():
        print(f"[ERROR] file not found: {args.pptx}", file=sys.stderr)
        return 1

    titles = collect_titles(args.pptx, args.size_bucket_gap)
    findings = detect(titles, args.dominance_min)

    if args.json or args.output:
        payload = {
            "source": str(args.pptx),
            "size_bucket_gap": args.size_bucket_gap,
            "dominance_min": args.dominance_min,
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
