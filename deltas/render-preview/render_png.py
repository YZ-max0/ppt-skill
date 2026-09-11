#!/usr/bin/env python3
"""Render a .pptx to per-slide PNGs plus a contact sheet (D-M2A).

Renderer selection (probed in this order, reports what it found):

1. **PowerPoint COM** — ``PowerPoint.Application`` via COM automation.
   On this machine the COM server is provided by **WPS Office** (the ProgID is
   the Office-compatible one; ``Application.Path`` resolves under
   ``...\\WPS Office\\...\\office6``). ``Presentation.Export`` writes one PNG
   per slide. This is the only working renderer here.
2. **LibreOffice headless** — ``soffice --headless --convert-to pdf`` then
   rasterise. Not installed on this machine (probed, absent).
3. Anything else available — reported as unavailable.

Design notes
------------
* WPS names the exported files with localised slide names (``幻灯片N.PNG``).
  The script renames them deterministically to ``slide-NN.png`` so downstream
  tooling never has to deal with non-ASCII names.
* **Encryption caveat**: on this machine the endpoint security product
  transparently encrypts newly written files. A PNG produced by the Windows
  COM process reads back as plain PNG for Windows processes, but shows a
  ``%TSD-Header%`` marker when read from WSL. All image work therefore happens
  in the Windows Python process (Pillow), never in WSL.
* Contact sheets are built with Pillow (already a python-pptx dependency).

Usage (Windows python):
    python render_png.py <deck.pptx> [-o <outdir>] [--dpi-scale 1280x720]
                         [--cols 4] [--no-contact]
"""
from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
CONTACT_COLS = 4
CONTACT_THUMB = (420, 236)   # thumbnail size inside the contact sheet
CONTACT_LABEL = 26           # label strip height under each thumbnail

PS_RENDER = r"""
$ErrorActionPreference = 'Stop'
$src = $args[0]; $out = $args[1]; $w = [int]$args[2]; $h = [int]$args[3]
$pp = New-Object -ComObject PowerPoint.Application
$pres = $pp.Presentations.Open($src, $true, $false, $false)
if (-not (Test-Path $out)) { New-Item -ItemType Directory -Path $out | Out-Null }
$pres.Export($out, "PNG", $w, $h)
$pres.Close(); $pp.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($pp) | Out-Null
Write-Host ("RENDERED " + $pres.Slides.Count)
"""


def _powershell() -> str:
    """Locate the Windows PowerShell executable usable from this process."""
    candidates = [
        r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        "powershell.exe",
    ]
    for c in candidates:
        if os.path.exists(c) or shutil.which(c):
            return c
    raise RuntimeError("PowerShell not found")


def probe_renderers() -> list:
    """Return a list of dicts describing renderer availability."""
    results = []

    # --- 1. PowerPoint / WPS COM ---
    probe = (
        "try { $pp = New-Object -ComObject PowerPoint.Application; "
        "Write-Host ('OK|' + $pp.Version + '|' + $pp.Path); $pp.Quit(); "
        "[System.Runtime.InteropServices.Marshal]::ReleaseComObject($pp)|Out-Null } "
        "catch { Write-Host ('FAIL|' + $_.Exception.Message) }"
    )
    try:
        out = subprocess.run(
            [_powershell(), "-NoProfile", "-Command", probe],
            capture_output=True, text=True, timeout=120,
        ).stdout.strip()
        parts = out.split("|")
        if parts and parts[0] == "OK":
            results.append({
                "name": "PowerPoint COM",
                "available": True,
                "version": parts[1] if len(parts) > 1 else "?",
                "path": parts[2] if len(parts) > 2 else "?",
            })
        else:
            results.append({"name": "PowerPoint COM", "available": False,
                            "error": out[:200]})
    except Exception as exc:                                   # pragma: no cover
        results.append({"name": "PowerPoint COM", "available": False,
                        "error": str(exc)[:200]})

    # --- 2. LibreOffice headless ---
    soffice_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        r"D:\LibreOffice\program\soffice.exe",
    ]
    found = next((p for p in soffice_paths if os.path.exists(p)), None)
    results.append({
        "name": "LibreOffice headless",
        "available": bool(found),
        "path": found or "not found",
    })
    return results


def render_with_com(pptx: Path, outdir: Path, width: int, height: int) -> int:
    """Render every slide to PNG via PowerPoint/WPS COM. Returns slide count."""
    outdir.mkdir(parents=True, exist_ok=True)
    # Clear previous outputs so a re-run never mixes old and new slides.
    for old in outdir.glob("slide-*.png"):
        old.unlink()
    raw = outdir / "_raw"
    if raw.exists():
        shutil.rmtree(raw)
    raw.mkdir(parents=True, exist_ok=True)

    # Write the script to a temp .ps1 and invoke it with -File. Passing the
    # arguments through `-Command ... -args` proved unreliable with this COM
    # server (Presentations.Open raised E_FAIL for paths that work via -File).
    script = raw / "_render.ps1"
    script.write_text(PS_RENDER, encoding="utf-8-sig")
    proc = subprocess.run(
        [_powershell(), "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(script), str(pptx), str(raw), str(width), str(height)],
        capture_output=True, text=True, timeout=1800,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "COM render failed:\nSTDOUT:%s\nSTDERR:%s" % (proc.stdout[-800:], proc.stderr[-800:])
        )

    # Normalise localised filenames -> slide-NN.png (ordered by trailing number)
    # NOTE: on Windows the filesystem is case-insensitive, so globbing "*.PNG"
    # and "*.png" returns the SAME files twice. Collect with a single pattern
    # and de-duplicate by resolved path.
    seen = {}
    for pattern in ("*.PNG", "*.png"):
        for f in glob.glob(str(raw / pattern)):
            seen[os.path.normcase(os.path.abspath(f))] = f
    pngs = list(seen.values())
    def slide_no(p: str) -> int:
        digits = "".join(ch for ch in Path(p).stem if ch.isdigit())
        return int(digits) if digits else 10 ** 6
    pngs.sort(key=slide_no)

    for i, src in enumerate(pngs, start=1):
        shutil.copyfile(src, outdir / ("slide-%02d.png" % i))
    return len(pngs)


def make_contact_sheet(png_dir: Path, out_path: Path, cols: int = CONTACT_COLS) -> tuple:
    """Compose all slide-NN.png into one labelled grid. Returns (w, h, n)."""
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:                                  # pragma: no cover
        raise RuntimeError("Pillow is required for the contact sheet: %s" % exc)

    files = sorted(png_dir.glob("slide-*.png"))
    if not files:
        raise RuntimeError("no slide-*.png found in %s" % png_dir)

    tw, th = CONTACT_THUMB
    rows = (len(files) + cols - 1) // cols
    pad = 18
    W = pad + cols * (tw + pad)
    H = pad + rows * (th + CONTACT_LABEL + pad)

    sheet = Image.new("RGB", (W, H), (250, 250, 248))
    draw = ImageDraw.Draw(sheet)

    for idx, f in enumerate(files):
        r, c = divmod(idx, cols)
        x = pad + c * (tw + pad)
        y = pad + r * (th + CONTACT_LABEL + pad)
        im = Image.open(f).convert("RGB")
        im.thumbnail((tw, th), Image.LANCZOS)
        # centre the thumbnail in its cell
        ox = x + (tw - im.width) // 2
        oy = y + (th - im.height) // 2
        sheet.paste(im, (ox, oy))
        draw.rectangle([x - 1, y - 1, x + tw, y + th], outline=(210, 210, 205))
        draw.text((x + 4, y + th + 6), "slide %02d" % (idx + 1), fill=(10, 10, 10))

    sheet.save(out_path, "PNG")
    return W, H, len(files)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Render .pptx to PNG + contact sheet")
    ap.add_argument("pptx", type=Path, help="source .pptx")
    ap.add_argument("-o", "--outdir", type=Path, default=None,
                    help="output directory (default: <pptx-stem>-render)")
    ap.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    ap.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    ap.add_argument("--cols", type=int, default=CONTACT_COLS)
    ap.add_argument("--no-contact", action="store_true")
    ap.add_argument("--probe-only", action="store_true",
                    help="report renderer availability and exit")
    args = ap.parse_args(argv)

    if args.probe_only:
        for r in probe_renderers():
            print(r)
        return 0

    if not args.pptx.exists():
        print("[ERROR] not found: %s" % args.pptx, file=sys.stderr)
        return 1

    outdir = args.outdir or args.pptx.parent / (args.pptx.stem + "-render")
    outdir.mkdir(parents=True, exist_ok=True)

    n = render_with_com(args.pptx, outdir, args.width, args.height)
    print("[OK] rendered %d slide(s) -> %s" % (n, outdir))

    if not args.no_contact:
        cp = outdir / "contact-sheet.png"
        w, h, cnt = make_contact_sheet(outdir, cp, args.cols)
        print("[OK] contact sheet %dx%d (%d slides) -> %s" % (w, h, cnt, cp))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
