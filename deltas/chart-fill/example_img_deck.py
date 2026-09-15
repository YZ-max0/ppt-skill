#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T-IMG1 Part C · 图片骨架端到端小样（6 页）。

验证目标：
  · v3 三个图片骨架各至少用一次（image-hero / image-split / image-grid）
  · 图片全部来自 PIL 程序生成的测试图（**无任何外部素材**）
  · 四道质检全过 + 读回 Picture shape 正确 + 渲染可读

题材：沿用 T-05 的 BP 结构做"图片增强小样"——用图片骨架替换文字页。
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import fill_skeleton as deckfill      # noqa: E402
import fill_chart                     # noqa: E402

deckfill.ASSETS = os.environ.get(
    "LAYOUT_ASSETS",
    os.path.abspath(os.path.join(HERE, "..", "layout-assets")),
)


def main(outdir: str) -> int:
    os.makedirs(outdir, exist_ok=True)
    P = lambda n: os.path.join(outdir, f"P{n:02d}.svg")   # noqa: E731
    done = []

    def skel(page, skeleton, slots):
        deckfill.build(skeleton, slots, P(page))
        done.append(P(page))

    # P01 图片主视觉封面（image-hero）
    skel(1, "v3/image-hero.svg", {
        "主标题": "让每一次客户对话都值得信任",
        "副标题": "AI 客服 SaaS · A 轮融资路演",
        "图片说明": "配图：团队办公场景（本小样使用程序生成的占位图）",
    })

    # P02 左图右文：产品界面（image-split）
    skel(2, "v3/image-split.svg", {
        "页面标题": "左图右文：产品界面承担核心论据",
        "栏目标题": "三个关键能力",
        "要点一标题": "首月覆盖七成高频问题",
        "要点一说明": ["接入企业自有知识库与工单历史，", "首月即可覆盖七成高频问题。"],
        "要点二标题": "低置信度自动转人工",
        "要点二说明": ["转人工时附带已收集的上下文，", "客户不必把同一件事讲三遍。"],
        "要点三标题": "回答可回溯到知识出处",
        "要点三说明": ["每条回答都能回溯到知识出处，", "满足金融医疗的合规审计要求。"],
        "图片说明": "配图：产品对话界面截图（占位图）",
        "说明补充": "界面示意，实际以交付版本为准",
    })

    # P03 图网格：团队（image-grid）
    skel(3, "v3/image-grid.svg", {
        "页面标题": "六人核心团队：覆盖产品、算法与商业化",
        "图一标题": "产品负责人",
        "图一说明": "十年客服产品经验",
        "图二标题": "技术负责人",
        "图二说明": "检索增强方向专家",
        "图三标题": "算法负责人",
        "图三说明": "对话系统八年经验",
        "图四标题": "销售负责人",
        "图四说明": "SaaS 从零到一亿",
        "图五标题": "交付负责人",
        "图五说明": "两百余个项目交付",
        "图六标题": "合规负责人",
        "图六说明": "金融行业合规背景",
    })

    # P04 市场规模（沿用 base 图表，作为对照：图表页不受图片改造影响）
    with open(P(4), "w", encoding="utf-8") as f:
        f.write(fill_chart.RENDERERS["area"]({
            "title": "目标市场未来四年翻倍，渗透率仍处早期",
            "subtitle": "中国智能客服市场规模（亿元）",
            "categories": ["2025", "2026", "2027", "2028"],
            "series": [{"name": "市场规模", "values": [286, 372, 468, 585]}],
            "note": "数据来源：模拟第三方行业研究口径。",
        }))
    done.append(P(4))

    # P05 单位经济学（waterfall，对照）
    with open(P(5), "w", encoding="utf-8") as f:
        f.write(fill_chart.RENDERERS["waterfall"]({
            "title": "单坐席月毛利已达 70%，规模降本空间明确",
            "subtitle": "单坐席月度收入到毛利的桥式拆解（元）",
            "unit": "元",
            "items": [
                {"label": "月度收入", "delta": 180, "is_total": True},
                {"label": "推理成本", "delta": -24},
                {"label": "算力运维", "delta": -18},
                {"label": "客户成功", "delta": -12},
                {"label": "规模降本", "delta": 18},
                {"label": "目标毛利", "delta": 144, "is_total": True},
            ],
            "note": "口径：模拟财务模型。",
        }))
    done.append(P(5))

    # P06 收尾（纯文字锚点，对照：无图页仍然成立）
    skel(6, "v2/quote-hero.svg", {
        "引文第一行": ["让中小企业也用得起", "可审计的智能客服。"],
        "出处": "图片骨架小样 — 收尾对照页",
    })

    for p in done:
        print("[OK]", os.path.basename(p))
    print(f"total pages: {len(done)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "./deckimg"))
