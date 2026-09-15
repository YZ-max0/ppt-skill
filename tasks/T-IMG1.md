# 任务卡 T-IMG1 · 图片位骨架专项（P1 · 预计 4-6 小时）

指挥官：opencode ｜ 执行者：同一执行者 ｜ 版本：v1.0 ｜ 前置：T-E2E6 收官

## 目标

补上"效果更好"的最后大缺口：**26 骨架无图片位**。本卡 = 链路研究 + 3 图片骨架 + 端到端实测 + 素材策略。

## Part A · 链路研究（只读，先做）

1. 读 `vendor-ppt-master/references/svg-image-embedding.md` + `image-layout-patterns.md` +
   `image-layout-spec.md` → 输出**图片嵌入契约摘要**：SVG 引用图片的路径规则 / 尺寸比例规范 /
   与项目 `images/` 目录的关系 / 打包（导出 PPTX）时的行为
2. 读 `scripts/image_search.py` + `image_gen.py` 入口 → **素材可行性矩阵**：
   哪些离线可用、哪些需要 API key / 外部服务（列出所需环境变量名，不申请、不硬编码）
3. **首次验证图片链路**（T-SMOKE 未验证项之一）：用 PIL 程序生成 3 张测试图（不同比例：16:9 / 4:3 / 1:1，
   带尺寸标注纹理），放入一个测试项目的 `images/`，在 SVG 中引用 → checker → 导出 → 读回验证
   （python-pptx：`Picture` shape 数量/尺寸/宽高比）；顺带确认 TSD 环境下图片文件的读写路径

## Part B · 3 个图片位骨架（进 `deltas/layout-assets/v3/`）

| 骨架 | 用途 | 布局 |
|---|---|---|
| `image-hero.svg` | 大图 + 标题浮层 | 满幅/大面积图（16:9 或 3:2），标题区覆盖或置下 |
| `image-split.svg` | 左图右文（含反向变体说明） | 图 1:1 或 4:3，文侧标准槽位 |
| `image-grid.svg` | 2×2 / 2×3 图网格 + 图注 | 等高图 + 每格图注；比例统一 4:3 |

- 图片位规范：引用路径 `images/<name>.png`（占位写法）+ **比例契约**（槽位比例固定，图片按 cover 裁剪适配）
- 沿用全部骨架硬标准（bounds/字号差 ≥6pt/卫生标记/占位标记）+ 过 checker 零 blocking
- 图注/文字槽位用 `【槽位】` 标记；**图片引用位用显式注释标记**（如 `<!-- IMAGE: images/hero.png 16:9 -->`）

## Part C · 端到端验证（对照实验）

用 T-05 产物做一版**图片增强小样**（或新建 5-6 页小 deck）：
- 至少 2 页使用 v3 图片骨架（如团队页 → `image-grid`，封面变体 → `image-hero`）
- 测试图用 Part A 的 PIL 占位图（**不得引入任何外部图片素材**；真实素材策略见 Part D）
- 全链路：checker → 导出 → 四道质检（含 overlap/hygiene）→ **读回验证**（图片 shape 正确）→ 渲染
- 交付 contact sheet 路径（指挥官读图）

## Part D · 素材策略文档（`docs/image-strategy.md`）

1. 三种素材来源矩阵：用户提供（推荐）/ 程序生成 / base 搜图与生图（API key 需求与离线限制）
2. 图片规范：比例（16:9/3:2/4:3/1:1）、最小分辨率、文件大小上限、命名规则
3. 与骨架的配合表：哪种页型用哪种图、图文比例建议
4. 已知限制（TSD 环境、PPTX 内嵌图片与链接图片的区别等）

## 顺带小修（已裁决，几分钟）

- `deltas/director.md` §2 登记 **B3 评审卡阶段**（B2 后、C 前）+ §8 对应措辞
- `docs/USAGE.md` 增补："任何返修后必须重跑质检流程"（C-028 教训）

## 验收标准

- [ ] 图片嵌入契约摘要 + 素材可行性矩阵 + 首次链路验证报告（含读回数据）
- [ ] 3 骨架零 blocking 入库 v3
- [ ] 端到端小样：≥2 页图片骨架、四道质检全过、读回图片 shape 正确、渲染图可读
- [ ] `docs/image-strategy.md` 四段完整
- [ ] 顺带小修落地
- [ ] 交付 `docs/img1-report.md`；提交：`feat(assets): image layout skeletons v3 + image pipeline (T-IMG1)`
- [ ] vendor 零 diff

## 异议区

如 base 图片链路实际要求与假设（项目 images/ + 相对引用）不同，以官方文档为准执行并记录；
如你判断图片位应改用其他骨架组合（2 个或 4 个），附设计对比再定。
