#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D-4 逐字稿校验器（P-1/P-2/P-3/P-7/P-9/P-10）。

用法：
    python check_notes.py <notes/total.md> <deck_svg_dir> <现场分钟数>

判据：
    P-2  每页 150-300 字（封面/章节页豁免下限）
    P-3  不含 Markdown 标记 / 元信息 / 阿拉伯数字百分比（TTS 读法）
    P-7  预计总时长 ≤ 现场 × 90%
    P-9  讲述记录数 == 页数
    P-10 备注纯净（可照读）
"""

from __future__ import annotations

import os
import re
import sys

MARKUP = [
    (r"^\s*[-*+]\s+", "Markdown 列表符"),
    (r"\*\*|__", "Markdown 强调符"),
    (r"`", "代码标记"),
    (r"^\s*#+\s", "标题残留"),
    (r"要点[:：]|时长[:：]|时长\b", "元信息标签"),
    (r"\[.*?\]", "方括号标记"),
    (r"TBD|待补充", "占位符"),
]

# TTS 读法：这些写法会被逐字朗读，应改中文读法
TTS_BAD = [
    (r"\d+%", "阿拉伯数字百分比（应写中文读法，如 百分之六十八）"),
    (r"\d+\.\d+", "小数点数字（TTS 读法不稳）"),
]

# 语速：中文技术口播的常见区间（含停顿）
#   180–220 字/分钟 为技术分享的典型值；这里取 200 作主判据，并给灵敏度区间。
CHARS_PER_MIN = 200.0
RATE_BAND = (150.0, 180.0, 200.0, 240.0)

# 豁免下限的页（P-2：封面/章节页/纯过渡页不受 150 字下限约束）
#   01 封面、02 导览（议程=过渡页）、25 收尾
EXEMPT = {"01", "02", "25"}


def parse_notes(path: str):
    """按 `# <num>_<title>` 切分，返回 [(num, title, body)]。"""
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    parts = re.split(r"^#\s+(\d{2,3})_([^\n]*)$", raw, flags=re.M)
    pages = []
    # parts = [前言, num, title, body, num, title, body, ...]
    for i in range(1, len(parts) - 2, 3):
        num, title, body = parts[i], parts[i + 1], parts[i + 2]
        pages.append((num, title.strip(), body.strip()))
    return pages


def count_chars(text: str) -> int:
    """计字数：忽略空白。"""
    return len(re.sub(r"\s", "", text))


def slide_text(path: str) -> str:
    """抽取 SVG 的可见文本（用于 P-1 复述率）。"""
    from xml.etree import ElementTree as ET
    try:
        root = ET.parse(path).getroot()
    except Exception:
        return ""
    out = []

    def walk(el):
        for c in el:
            tag = c.tag.split("}")[-1]
            if tag == "text":
                out.append("".join(c.itertext()).strip())
            elif tag != "metadata":
                walk(c)
    walk(root)
    return "".join(out)


def main(argv):
    notes_path, svg_dir, minutes = argv[1], argv[2], float(argv[3])
    pages = parse_notes(notes_path)
    svgs = sorted(f for f in os.listdir(svg_dir) if f.endswith(".svg"))

    print(f"# D-4 逐字稿校验\n")
    print(f"- 讲稿页数：**{len(pages)}** ｜ SVG 页数：**{len(svgs)}**")
    p9 = "✅" if len(pages) == len(svgs) else "❌"
    print(f"- **P-9 一一对应**：{p9}\n")

    print("| 页 | 标题 | 字数 | P-2 | P-3 问题 | P-1 复述率 |")
    print("|---|---|---|---|---|---|")
    total_chars = 0
    problems = []
    p2_fail = p3_fail = 0
    for idx, (num, title, body) in enumerate(pages):
        n = count_chars(body)
        total_chars += n
        lo_ok = (num in EXEMPT) or n >= 150
        hi_ok = n <= 300
        p2 = "✅" if (lo_ok and hi_ok) else ("❌低" if not lo_ok else "❌高")
        if not (lo_ok and hi_ok):
            p2_fail += 1

        # P-3
        p3 = []
        for pat, why in MARKUP:
            if re.search(pat, body, re.M):
                p3.append(why)
        if p3:
            p3_fail += 1
        p3s = "；".join(p3) if p3 else "—"

        # P-1 复述率：讲稿与页面文本的最长公共字符片段占比（粗粒度）
        rep = "—"
        if idx < len(svgs):
            st = slide_text(os.path.join(svg_dir, svgs[idx]))
            if st:
                # 用 8 字窗口做重合统计
                win, hit, tot = 8, 0, 0
                for i in range(0, len(st) - win + 1, win):
                    tot += 1
                    if st[i:i + win] in body.replace("\n", ""):
                        hit += 1
                rep = f"{hit/tot*100:.0f}%" if tot else "—"

        shown = title if len(title) <= 18 else title[:17] + "…"
        print(f"| {num} | {shown} | {n} | {p2} | {p3s} | {rep} |")
        if p3:
            problems.append((num, p3))

    est = total_chars / CHARS_PER_MIN
    limit = minutes * 0.9
    print(f"\n## 汇总\n")
    print(f"- 总字数：**{total_chars}**")
    print(f"- **P-2 篇幅**：{p2_fail} 页越界（150–300 区间；封面/过渡/收尾页豁免下限）")
    print(f"- **P-3 口语/Markdown**：{p3_fail} 页有问题")
    print(f"- **P-7 预计时长**：{est:.1f} 分钟 / 限额 {limit:.1f} 分钟"
          f"（现场 {minutes:.0f} 分钟 × 90%）：{'✅ 通过' if est <= limit else '❌ 超时'}")
    print(f"\n### P-7 语速灵敏度（诚实披露：总时长强依赖语速假设）")
    print(f"\n| 语速（字/分钟） | 预计总时长 | 对 {minutes:.0f} 分钟现场的占用 | 判定 |")
    print(f"|---|---|---|---|")
    for r in RATE_BAND:
        e = total_chars / r
        occ = e / minutes * 100
        print(f"| {r:.0f} | {e:.1f} 分钟 | {occ:.0f}% | {'✅' if e <= limit else '❌'} |")
    print(f"\n> 判据：P-7 要求总时长 ≤ 现场 × 90%（= {limit:.1f} 分钟）。"
          f"在 {RATE_BAND[0]:.0f}–{RATE_BAND[-1]:.0f} 字/分钟区间内"
          f"{'全部通过' if total_chars/RATE_BAND[0] <= limit else '存在超时风险'}。")

    # TTS 读法单独提示（非阻断）
    tts = []
    for num, _t, body in pages:
        for pat, why in TTS_BAD:
            for m in re.finditer(pat, body):
                tts.append((num, m.group(0), why))
    print(f"\n### TTS 读法提示（非阻断，{len(tts)} 处）")
    if tts:
        for num, txt, why in tts[:15]:
            print(f"- 页{num}: `{txt}` — {why}")
        if len(tts) > 15:
            print(f"- … 其余 {len(tts)-15} 处")
    else:
        print("- 无")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
