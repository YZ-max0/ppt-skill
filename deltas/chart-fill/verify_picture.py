#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读回验证（修正版）：递归统计 Picture shape。

**踩坑记录（T-IMG1 Part A.3）**：
首版只扫 `slide.shapes` 顶层，得到"0 个 picture"——但图片其实**存在**，
只是被包在 `<g>` 对应的 group shape 里（本仓库骨架的根级 `<g>` 都会成组）。
必须**递归进 group** 才能读到。这个假阴性差点被误判为"图片链路不通"。
"""
from __future__ import annotations

import io
import sys
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from PIL import Image

EMU_PER_PX = 9525  # 96 dpi


def iter_pictures(shapes):
    """递归产出所有 Picture shape（含 group 内）。"""
    for sh in shapes:
        if sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
            yield sh
        elif sh.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from iter_pictures(sh.shapes)


def main(pptx_path: str) -> int:
    prs = Presentation(pptx_path)
    n_slides = len(prs.slides._sldIdLst)
    print(f"slides: {n_slides}")
    total = 0
    ratios = []
    for si, slide in enumerate(prs.slides, 1):
        pics = list(iter_pictures(slide.shapes))
        print(f"\n--- slide {si}: {len(pics)} picture shape(s) [递归] ---")
        for i, pic in enumerate(pics, 1):
            total += 1
            w_px, h_px = pic.width / EMU_PER_PX, pic.height / EMU_PER_PX
            x_px, y_px = pic.left / EMU_PER_PX, pic.top / EMU_PER_PX
            r_disp = w_px / h_px
            print(f"  [{i}] {pic.name!r}  位置=({x_px:.1f},{y_px:.1f})  "
                  f"显示={w_px:.1f}x{h_px:.1f}  显示比例={r_disp:.4f}")
            blob = pic.image.blob
            if blob:
                im = Image.open(io.BytesIO(blob))
                rw, rh = im.size
                print(f"      内嵌={len(blob)}B  位图={rw}x{rh}  "
                      f"位图比例={rw/rh:.4f}  格式={im.format}")
                ratios.append((r_disp, rw / rh))
            else:
                print("      !! blob 空 -> 仅链接未内嵌")
    print(f"\nTOTAL picture shapes = {total}")
    # 显示比例 vs 位图比例：slice 裁剪时二者本就不同（这是预期的），故只报告不做断言
    if ratios:
        print("\n显示比例 vs 位图比例（slice 裁剪下允许不同，meet/none 下应一致）：")
        for d, r in ratios:
            print(f"  {d:.4f}  vs  {r:.4f}   {'一致' if abs(d-r) < 1e-3 else '不同(被裁剪)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
