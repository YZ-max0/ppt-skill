#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T-02 骨架填充器：骨架 + 槽位文本 → 页面 SVG。

填充纪律（v0/CONTRACT.md §2）：
  · 整段替换 `【槽位名】示例内容` 整体，不得只替换方括号部分
  · 填充后 `【` 计数必须为 0
  · 骨架是固定几何：替换文本不得显著长于示例文案

实现要点（第一版踩过的坑）：
  v2/cover-bold 把【汇报单位】与【周期】放进**同一个 <text>** 的两个 tspan。
  若按"逐槽位替换"处理，第一个槽位填完后其标记消失，第二个槽位便误判为
  "独占该 <text>"，从而按行覆盖全部 tspan —— 结果是两个槽位互相盖掉。
  因此改为**按 <text> 分组、一次填充整块**：块内出现 ≥2 个槽位时逐个 tspan
  精确替换；只含 1 个槽位时按行整体替换。
"""

from __future__ import annotations

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
if not os.path.isdir(ASSETS):
    ASSETS = os.path.join(HERE, "..", "layout-assets")

_TEXT_RE = re.compile(r"<text\b[^>]*>.*?</text>", re.S)
_TSPAN_RE = re.compile(r"(<tspan\b[^>]*>)(.*?)(</tspan>)", re.S)
_OPEN_RE = re.compile(r"<text\b[^>]*>")
_SLOT_RE = re.compile(r"【([^】]+)】")


def esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def _as_lines(v) -> list:
    return [v] if isinstance(v, str) else list(v)


def _slots_in(block: str) -> list:
    """块内出现的槽位名，按首次出现顺序去重。"""
    seen = []
    for s in _SLOT_RE.findall(block):
        if s not in seen:
            seen.append(s)
    return seen


def _fill_text_block(block: str, slots: dict) -> str:
    names = _slots_in(block)
    if not names:
        return block

    text_open = _OPEN_RE.match(block).group(0)
    body = block[len(text_open):-len("</text>")]
    tspans = list(_TSPAN_RE.finditer(body))

    if len(names) >= 2:
        # 多个槽位共用一个 <text>：逐个 tspan 精确替换
        def repl(m):
            tag, inner, close = m.group(1), m.group(2), m.group(3)
            for nm in names:
                if f"【{nm}】" in inner:
                    return tag + esc(_as_lines(slots[nm])[0]) + close
            return m.group(0)
        new_body = _TSPAN_RE.sub(repl, body)

    elif not tspans:
        new_body = esc(_as_lines(slots[names[0]])[0])

    else:
        # 单槽位独占：按行整体替换
        vals = _as_lines(slots[names[0]])
        counter = {"i": 0}

        def repl(m):
            tag, _inner, close = m.group(1), m.group(2), m.group(3)
            i = counter["i"]
            counter["i"] = i + 1
            return tag + esc(vals[i] if i < len(vals) else "") + close
        new_body = _TSPAN_RE.sub(repl, body)

    return text_open + new_body + "</text>"


def fill_svg(svg: str, slots: dict) -> str:
    out, pos = [], 0
    for m in _TEXT_RE.finditer(svg):
        out.append(svg[pos:m.start()])
        out.append(_fill_text_block(m.group(0), slots))
        pos = m.end()
    out.append(svg[pos:])
    return "".join(out)


def build(skeleton: str, slots: dict, out: str) -> str:
    path = skeleton if os.path.isabs(skeleton) else os.path.join(ASSETS, skeleton)
    with open(path, encoding="utf-8") as f:
        svg = f.read()
    svg = fill_svg(svg, slots)
    left = svg.count("【")
    if left:
        missing = sorted(set(_SLOT_RE.findall(svg)))
        raise AssertionError(f"{out}: 仍有 {left} 个未填充占位符：{missing}")
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    return out


def retag_group(path: str, group_id: str, values: list) -> None:
    """替换某个 <g id="..."> 内**无槽位标记**的示例文案（按出现顺序）。

    骨架里有一部分文字是示例内容而非槽位（如 v2/cover-bold 的 `KB` 品牌标记），
    若不清洗会原样泄漏进产物。
    """
    with open(path, encoding="utf-8") as f:
        svg = f.read()
    gstart = svg.find(f'<g id="{group_id}"')
    if gstart < 0:
        raise KeyError(f"找不到组：{group_id}")
    gend = svg.find("</g>", gstart)
    block = svg[gstart:gend]

    idx = {"i": 0}

    def repl(m):
        i = idx["i"]
        idx["i"] = i + 1
        if i >= len(values):
            return m.group(0)
        tag, _inner, close = m.group(1), m.group(2), m.group(3)
        return tag + esc(values[i]) + close

    new_block = _TSPAN_RE.sub(repl, block)
    if idx["i"] == 0:
        # 组内没有 tspan：逐个 <text> 处理
        def repl2(m):
            i = idx["i"]
            idx["i"] = i + 1
            if i >= len(values):
                return m.group(0)
            open_tag = _OPEN_RE.match(m.group(0)).group(0)
            return open_tag + esc(values[i]) + "</text>"
        new_block = _TEXT_RE.sub(repl2, block)

    with open(path, "w", encoding="utf-8") as f:
        f.write(svg[:gstart] + new_block + svg[gend:])
