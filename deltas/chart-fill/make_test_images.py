#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T-IMG1 Part A.3 · 生成测试用占位图（PIL，无外部素材）。

产出 3 张不同比例的标注图，每张带：比例文字、像素尺寸、对角线、四角标记、中心十字、
以及 1px 网格 —— 目的是导出后在 contact sheet 上**一眼看出**是否被裁剪/拉伸/变形。
"""

from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont

# (文件名, 宽, 高, 主色)
SPECS = [
    ("hero-16x9.png", 1920, 1080, (0, 47, 167)),
    ("split-4x3.png", 1200, 900, (26, 92, 138)),
    ("grid-1x1.png", 900, 900, (140, 60, 30)),
]


def font(size: int):
    """尽量取系统等宽/黑体；取不到则用 PIL 位图字体。"""
    for name in ("msyh.ttc", "msyhbd.ttc", "simhei.ttf", "arial.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def make(path: str, w: int, h: int, rgb) -> None:
    img = Image.new("RGB", (w, h), rgb)
    d = ImageDraw.Draw(img)

    # 1px 网格（每 100px），用于检查缩放/裁剪
    grid = tuple(min(255, c + 38) for c in rgb)
    for x in range(0, w, 100):
        d.line([(x, 0), (x, h)], fill=grid, width=1)
    for y in range(0, h, 100):
        d.line([(0, y), (w, y)], fill=grid, width=1)

    # 四角标记（若被裁剪，角标会先消失）
    m = max(18, w // 22)
    for (cx, cy, dx, dy) in ((0, 0, 1, 1), (w - 1, 0, -1, 1),
                             (0, h - 1, 1, -1), (w - 1, h - 1, -1, -1)):
        d.line([(cx, cy), (cx + dx * m, cy)], fill=(255, 255, 255), width=6)
        d.line([(cx, cy), (cx, cy + dy * m)], fill=(255, 255, 255), width=6)

    # 对角线 + 中心十字（检查是否被非等比拉伸）
    d.line([(0, 0), (w - 1, h - 1)], fill=(255, 255, 255), width=3)
    d.line([(w - 1, 0), (0, h - 1)], fill=(255, 255, 255), width=3)
    cx, cy = w // 2, h // 2
    d.line([(cx - w // 10, cy), (cx + w // 10, cy)], fill=(255, 220, 0), width=8)
    d.line([(cx, cy - h // 10), (cx, cy + h // 10)], fill=(255, 220, 0), width=8)

    # 中央大字号标注
    ratio = f"{w} x {h}"
    ratio_txt = f"{w/h:.4g}:1" if w != h else "1:1"
    f_big, f_mid = font(max(28, w // 16)), font(max(18, w // 34))
    d.text((cx, cy - h // 6), ratio, font=f_big, fill=(255, 255, 255),
           anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
    d.text((cx, cy + h // 12), f"ASPECT {ratio_txt}", font=f_mid,
           fill=(255, 255, 255), anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
    d.text((cx, cy + h // 5), os.path.basename(path), font=f_mid,
           fill=(255, 255, 255), anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))

    img.save(path, "PNG", optimize=True)


def main(outdir: str) -> int:
    os.makedirs(outdir, exist_ok=True)
    for name, w, h, rgb in SPECS:
        p = os.path.join(outdir, name)
        make(p, w, h, rgb)
        sz = os.path.getsize(p)
        print(f"[OK] {name:18s} {w}x{h}  ratio={w/h:.4f}  {sz/1024:.1f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "./imgs"))
