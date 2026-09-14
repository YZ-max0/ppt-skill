#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""骨架卫生检查器 · 拦截"骨架示例内容泄漏进交付物"（T-FIX4 R3）。

背景（C-011）：
    骨架里有一部分文本**没有 `【槽位】` 标记**（示例数据、品牌字、示意标签）。
    填充时只替换带标记的元素 → 这些无标记的示例内容原样进入交付物，而
    `svg_quality_checker`（管几何）与 D-2（管出框/标题）**都拦不住**
    —— 它们几何完全合法，属"内容泄漏"而非结构错误。
    唯一可靠的发现方式是渲染后人工看图。本检查器把它变成自动断言。

判据（关键设计点）：
    仓库的占位约定是 `【槽位名】示例内容`。检查器的两个使用场景判据不同：

    **A. 交付物模式（默认）** —— 检查"已填充的产物目录"
      填充后所有槽位标记都被真实内容替换，**再无标记可依据**；此时唯一可靠信号是
      **示例词表**（词表里是"只可能来自骨架示例"的短语，真实内容不会恰好命中）。
      此模式**不做启发式**——否则会把 `2024`、`全年净增 18 人` 这类合法内容误判。

    **B. 骨架模式（--skeleton-mode）** —— 扫描 `deltas/layout-assets/` 找未标记示例
      骨架里标记仍在，故按**元素粒度**判定：
        · 元素内含 `【` → 槽位，其示例内容必被替换，**非风险**（跳过）
        · 元素内无 `【` → 机械填充碰不到它，**是风险**，再叠加词表 + 启发式
      启发式：像内容（中文≥2 字 / 数字+单位 / 2-4 位大写品牌字），放行结构性白名单。

用法：
    python check_hygiene.py <svg_dir>                     # 交付物模式（词表）
    python check_hygiene.py <layout-assets> --skeleton-mode  # 骨架模式（+启发式）
    python check_hygiene.py <svg_dir> --json -o report.json

退出码：0 = 干净 ｜ 2 = 发现泄漏（P0）
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
# 全库示例词表（T-FIX4 R1 扫描汇总 · 见 HYGIENE.md §2）
# ---------------------------------------------------------------------------
DEFAULT_TERMS = [
    # —— v2/cover-bold（C-011 源头：T-03 知识库平台方案）——
    "知识库平台建设方案", "知识库", "KB",
    # —— v0/kpi-hero 初版裸示例值 ——
    "99.4%",
    # —— v2/evidence-wall 示例证据 ——
    "软件、实施、硬件与培训四项合计", "按找资料与返工工时折算",
    "按上述节省口径推算得出", "两项风险均有明确对策",
    # —— v1/budget-4 示例条目说明 ——
    "平台软件与许可", "账号打通与数据迁移工作量",
    # —— v1/process-steps 示例步骤 ——
    "支持按标题与正文检索", "仅返回有权查看的资料",
    # —— v2/donut-chart 示例说明 ——
    "软件与实施占预算四分之三",
    # —— v2/line-chart 示例说明 ——
    "累计净投入随节省逐年下降",
    # —— v1 知识库语境示例 ——
    "统一检索层", "权限控制与知识沉淀",
]

# 结构性白名单：骨架的固有设计元素，不算泄漏
STRUCTURAL_OK = {
    "对策", "目标", "说明", "备注", "结论", "小计", "合计",
    "01", "02", "03", "04", "05", "06", "1", "2", "3", "4", "5", "6",
    "“", "”", "‘", "’", "—", "·", "-", "/", "%",
}

_SLOT_RE = re.compile(r"【[^】]*】")

# 通用启发式
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_NUM_UNIT_RE = re.compile(
    r"\d[\d,.]*\s*(?:万|亿|千|百|%|％|年|月|日|天|人|次|个|元|块|pt|px|秒|分钟|小时|倍)")
_BRAND_RE = re.compile(r"^[A-Z]{2,4}$")


def s(tag: str) -> str:
    return tag.split("}")[-1]


def collect_texts(path: str):
    """返回 [(元素无标记? , 文本, 行号)]（行号尽力而为：按文本在源文件中定位）。"""
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    root = ET.fromstring(raw)
    out = []

    def walk(el):
        for c in el:
            tag = s(c.tag)
            if tag == "text":
                txt = "".join(c.itertext()).strip()
                if not txt:
                    continue
                has_slot = bool(_SLOT_RE.search(txt))
                # 行号：用原文首次出现定位（同一文本可能多次，取首次即可）
                ln = raw.find(txt)
                ln = raw[:ln].count("\n") + 1 if ln >= 0 else 0
                out.append((has_slot, txt, ln))
            elif tag in ("metadata",):
                continue
            else:
                walk(c)
    walk(root)
    return out


def judge(txt: str, terms: list):
    """对单个"无标记"文本判定；返回 (风险, 依据) 或 None。"""
    if txt in STRUCTURAL_OK:
        return None
    if re.fullmatch(r"[\W_]+", txt):
        return None

    for t in terms:
        if t and t in txt:
            return ("P0", f"命中示例词表 {t!r}")

    if _BRAND_RE.match(txt):
        return ("P0", "无标记的 2-4 位大写品牌字（C-011 同类）")

    if _NUM_UNIT_RE.search(txt):
        return ("P0", "无标记的示例数值（含数字+单位）")

    # 裸数值（≥3 位）：带单位的情形已被上一条覆盖；骨架的轴刻度等结构性数字
    # 请加入 STRUCTURAL_OK 或 --wordlist 放行（当前 24 骨架无此类误报）
    if re.fullmatch(r"\d{3,}(?:[.,]\d+)?", txt):
        return ("P0", "无标记的裸示例数值（≥3 位）")

    if _CJK_RE.search(txt) and len(_CJK_RE.findall(txt)) >= 2:
        return ("P1", "无标记的中文内容（≥2 字），疑为示例内容")

    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="骨架卫生检查（示例内容泄漏）")
    ap.add_argument("svg_dir", help="待检查目录（项目 svg_output 或 layout-assets）")
    ap.add_argument("--wordlist", help="自定义词表（每行一词，# 为注释）")
    ap.add_argument("--skeleton-mode", action="store_true",
                    help="骨架模式：对无标记元素启用启发式（扫描 layout-assets 用）")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("-o", "--out", help="JSON 报告输出路径")
    a = ap.parse_args(argv)

    terms = list(DEFAULT_TERMS)
    if a.wordlist:
        with open(a.wordlist, encoding="utf-8") as f:
            terms = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    files = sorted(glob.glob(os.path.join(a.svg_dir, "**", "*.svg"), recursive=True))
    if not files:
        print(f"[ERROR] 目录内没有 SVG：{a.svg_dir}", file=sys.stderr)
        return 2

    findings = []
    unmarked_total = 0
    slot_elems = 0
    for p in files:
        for has_slot, txt, ln in collect_texts(p):
            # —— 词表命中（两种模式都查；骨架模式下也只查无标记元素）——
            if a.skeleton_mode and has_slot:
                slot_elems += 1
                continue                      # 槽位元素：整段会被替换，非风险
            if not a.skeleton_mode:
                # 交付物模式：不做元素粒度过滤，词表命中即报
                for t in terms:
                    if t and t in txt:
                        findings.append({
                            "file": os.path.basename(p), "line": ln,
                            "text": txt[:60], "risk": "P0",
                            "reason": f"命中示例词表 {t!r}",
                        })
                continue

            unmarked_total += 1
            r = judge(txt, terms)
            if r:
                lvl, why = r
                findings.append({
                    "file": os.path.basename(p), "line": ln,
                    "text": txt[:60], "risk": lvl, "reason": why,
                })

    p0 = [f for f in findings if f["risk"] == "P0"]
    p1 = [f for f in findings if f["risk"] == "P1"]
    failed = bool(p0)

    result = {
        "status": "failed" if failed else "passed",
        "mode": "skeleton" if a.skeleton_mode else "artifact",
        "scanned_files": len(files),
        "wordlist_size": len(terms),
        "unmarked_text_elements": unmarked_total,
        "slot_text_elements": slot_elems,
        "p0": len(p0), "p1": len(p1),
        "findings": findings,
        "exit_code": 2 if failed else 0,
    }

    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    mode = "骨架模式" if a.skeleton_mode else "交付物模式"
    print(f"\n[Hygiene/{mode}] 扫描 {len(files)} 个 SVG；词表 {len(terms)} 词"
          + (f"；槽位元素 {slot_elems}，无标记元素 {unmarked_total}" if a.skeleton_mode else ""))
    if failed:
        print(f"[FAIL] 发现示例内容泄漏：P0={len(p0)}"
              + (f"，P1={len(p1)}" if a.skeleton_mode else ""))
        for f in p0[:40]:
            print(f"  [P0] {f['file']} L{f['line']}: {f['text']!r} — {f['reason']}")
        print("\n修复：把该文本改为骨架槽位（`【槽位名】示例内容`）或中性化，再重新生成。")
    else:
        print("[OK] 未发现示例内容泄漏。")
    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
