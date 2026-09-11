# 任务卡 T-M2A · 视觉验证能力建设（M2 开门）（P1 · 预计 2-3 小时）

指挥官：opencode ｜ 执行者：同一执行者 ｜ 版本：v1.0 ｜ 前置：M1 已关闭

## 背景

项目至今所有验收都是**结构级**（checker / 溢出 / 乱码 / 占位符）——**从未渲染过一页真实视觉**。
用户的终极目标是"效果更好"，而"效果"只能在像素层验证。本卡建立第一个视觉闭环。

## 步骤

### 1 · 渲染器探针（Windows 侧，按优先序探测）

| 优先 | 渲染器 | 探测方式 |
|---|---|---|
| a | PowerPoint COM | `New-Object -ComObject PowerPoint.Application`（装了 Office 即可用） |
| b | LibreOffice headless | `soffice.exe --version`（常见路径 `C:\Program Files\LibreOffice\program\`） |
| c | 其他可用的 pptx→png 路径 | 自行探测并报告 |

输出**渲染器可用性矩阵**（找到什么/版本/单页渲染耗时）。
**若无可用渲染器**：报告 + 探测 `winget search libreoffice` 等安装可行性 + 给出建议命令，**不擅自安装**。

### 2 · 渲染现有 3 份产物（若渲染器可用）

源产物（临时目录内已存在）：
- `ppt-e2e\...\t01-weekly_20260911_133607.pptx`（首跑 6 页）
- `ppt-e2e\...\t01b-assets_20260911_151935.pptx`（资产库版 6 页）
- `ppt-e2e2\...\t03-proposal_20260911_153940.pptx`（导演式 21 页）

每 deck：全页 PNG（150 DPI 左右）→ **contact sheet 网格图**（每 deck 一张，含页码编号）。
全部存 `C:\Users\EDY\AppData\Local\Temp\opencode\ppt-render\`，给出文件清单（路径 + 尺寸）。

### 3 · 脚本化（进 repo）

`deltas/render-preview/render_png.py` + `README.md`：
- 输入 .pptx → 输出 PNG 目录 + contact sheet
- README：渲染器选择逻辑、依赖、W-3/W-6 注意（路径/工作目录）
- 要求：Windows 侧可重复运行；不依赖 vendor

### 4 · 报告 `docs/m2-render-report.md`

渲染器矩阵 / 3 deck 渲染结果（页数、耗时、文件清单）/ 未验证项 / 《建议》。

## 硬约束

1. vendor 零修改；PNG 产物默认在临时目录（repo 不新增图片）；脚本进 `deltas/render-preview/`
2. 不擅自安装软件；不修改系统配置
3. 渲染失败如实报告（含错误原文），不伪造截图

## 验收标准

- [ ] 渲染器可用性矩阵（含探测命令与结果）
- [ ] 3 deck × 全页 PNG + 3 张 contact sheet（或如实报告不可渲染原因）
- [ ] `deltas/render-preview/` 脚本入库且 README 完整
- [ ] 报告四段完整；vendor 零 diff

## 异议区

如你认为渲染路径有更优选项（如 pptx→PDF→png 的间接路线、或 WPS COM），附对比数据。
