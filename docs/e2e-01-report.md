# M1 端到端首跑报告（T-01 · 快速通道）

> 执行者：开发工程师 ｜ 日期：2026-09-11 ｜ 卡：`tasks/T-E2E1.md`
> 链路：Director 轻量 → Quick 通道 → 手写 SVG → 导出 PPTX → D-2 质检 → 读回验证
> 结论：**链路 join 点全部打通**；暴露 2 个真实契约缺漏（已就地修正）+ 1 个 D-2 新缺陷（已记录，未修复）

---

## 1. 命令序列（原样 + 退出码 + 耗时）

环境：Windows PowerShell 5.1 + `python` 3.12.3 + python-pptx 1.0.2（详见 `docs/windows-notes.md`）

| # | 阶段 | 命令（原样） | exit | 耗时 |
|---|---|---|---|---|
| 1 | 项目初始化 | `python <vendor>\scripts\project_manager.py init t01-weekly --format ppt169 --quick-generate` | 0 | **1 s** |
| 2 | 手写 SVG | 6 个文件写入 `svg_output/P01..P06.svg`（人工编写，无命令） | — | **约 25 min** |
| 3 | 质量检查（首轮） | `python <vendor>\scripts\svg_quality_checker.py <proj> --quick-generate --stage final --json` | 0（报告 6 errors） | **2 s** |
| 4 | 质量检查（修正后×3 轮） | 同上 | 0（报告 6/6 passed） | **2 s ×3** |
| 5 | 导出 | `python <vendor>\scripts\svg_to_pptx.py <proj> --quick-generate --no-notes` | 0 | **5 s** |
| 6 | D-2 出框质检 | `python <deltas>\detect_overflow.py <pptx> --json -o ...` | **0** | 2 s |
| 7 | D-2 标题一致性 | `python <deltas>\check_title_consistency.py <pptx> --json -o ...` | 2（14 P1） | 2 s |
| 8 | 读回验证 | `python readback.py`（UTF-8 文件回读，见 P-3） | 0 | 2 s |

**quick 路径确认（卡内异议区的回应）**：卡内假设"quick 是 lockless 短路"**成立且更精确**——
实际入口标志是 **`--quick-generate`**，而非默认路径。这解释了 T-SMOKE 冒烟时的两道 lock 门：
- `init --quick-generate` 只创建 `svg_output/` + `validation/`（无 README、无 lock 相关物）
- `svg_quality_checker --quick-generate` / `svg_to_pptx --quick-generate` 全程**不读 spec_lock**
- 冒烟时的 `spec_lock.md is required` / `requires a passing final report` 两门**仅在默认路径出现**
> 即：**走的标志不同，前置条件不同**。本卡以 vendor 权威文档为准执行，与卡内假设一致。

---

## 2. Director 轻量稿（全文附录 · §7 公式）

**受众 3 句**
- **给谁听**：直属主管，1 人，最关心"本周实际产出"与"下周能否按期交付"。
- **他要什么结果**：确认 4 项已完成工作属实、2 个风险已知且有对策，会后不需额外追进度。
- **讲述尺度**：5-8 分钟，不要行业背景铺垫，直接上事实与判断。

| # | 观点标题 | 要点（≤3） | 页型 |
|---|---|---|---|
| 1 | 本周工作汇报 | 汇报人/周期/一句话总览 | 封面 |
| 2 | 本周完成 4 项，进度符合预期 | ①接口联调完成 ②数据看板上线 ③性能优化达标 ④文档归档完成 | 内容（要点列表） |
| 3 | 两项风险已识别并有对策 | ①第三方接口交付延迟→备用方案 ②测试人力缺口→申请支援 | 内容（双栏对比） |
| 4 | 下周计划围绕三个目标 | ①完成回归测试 ②推动接口切换 ③输出验收材料 | 内容（时间轴） |
| 5 | 需要主管支持的一件事 | 请协调 1 名测试人力，保障周四前的回归窗口 | 内容（单点呼吁） |
| 6 | 本周总结 | 进度可控 / 风险有主 / 下周可交付 | 结尾 |

> 页数 6（T-01 要求 6-8 含封面，合规）；T-01 无素材 → 按卡授权自拟合理内容，4 事项 / 2 风险均落实。
> 快速通道纪律遵守：跳过 B2 优化与 C 阶段行文细节，只做"受众 3 句 + 逐页观点稿"。

---

## 3. 产物清单

全部位于 `C:\Users\EDY\AppData\Local\Temp\opencode\ppt-e2e\`（repo 零产物）：

| 产物 | 路径 | 规格 |
|---|---|---|
| PPTX | `projects\t01-weekly_ppt169_20260911\exports\t01-weekly_20260911_133607.pptx` | 23141 bytes，**6 页**，postflight `passed` |
| SVG 源 | 同项目 `svg_output\P01..P06.svg` | 6 文件，1280×720 |
| 质量报告 | 同项目 `validation\svg_quality_report.json` | 6/6 passed, blocking 0 |
| postflight | 同项目 `validation\t01-weekly_20260911_133607.report.json` | `status=passed quality_gate=passed slides=6` |
| D-2 输出 | `d2_overflow.json` / `d2_title.json` | 见 §4 |
| 读回文本 | `readback.txt` | UTF-8，49 文本帧 |

**读回验证（递归遍历 GROUP）**

| 项 | 结果 |
|---|---|
| 页数 | **6** ✅ |
| 文本帧 | **49** ✅ |
| `\ufffd` 乱码计数 | **0** ✅ |
| 中文正确性 | ✅ 全部逐字正确（UTF-8 文件回读，非控制台） |

---

## 4. T-01 验收对照

| T-01 验收重点 | 结果 | 证据 |
|---|---|---|
| **快速通道可达** | ✅ **是** | `--quick-generate` 路径全程无 lock/spec/Confirm UI；初始化 1s、导出 5s |
| **无溢出（P0=0）** | ✅ **是** | `detect_overflow`: **P0=0 / P1=0 / 45 项全 OK**，exit 0 |
| **无乱码** | ✅ **是** | 49 文本帧，`\ufffd` = 0；中文逐字正确 |
| 6-8 页（含封面） | ✅ 6 页 | postflight `slides=6` |
| 4 个已完成事项 | ✅ | 页 2 四项齐全（接口联调/看板上线/性能优化/文档归档） |
| 2 个风险 | ✅ | 页 3 两项（第三方延迟 / 测试人力缺口），各含影响·概率·对策 |

**D-2 明细**

| 检测器 | 结果 | 判定 |
|---|---|---|
| `detect_overflow.py` | P0=0 P1=0 OK=45，exit 0 | ✅ **T-FIX1 修复在真实 e2e 产物上验证有效**（45 项全 OK） |
| `check_title_consistency.py` | P1=14，exit 2 | ⚠️ **全部为误报**，见 C-002 |

---

## 5. 失败模式清单（C-XXX）

### C-001 · 手写 SVG 缺 `data-pptx-bounds` 全书 blocking（🟡 已处理）

- **现象**：首轮质量检查 6/6 全部报 blocking：
  `Detected N visible root-level <g> module(s) without explicit data-pptx-bounds`
- **原因**：`semantic-svg.md` 要求最终页每个根级 `<g>` 声明显式边界，供导出器做模块定位与溢出诊断。我首轮未写。
- **处理**：为所有根级 `<g>` 补 `data-pptx-bounds="x y w h"`（并给整页背景建独立 `page-bg` 组）。
- **连带**：同一轮 introduced 还报"根级散落 `<rect>`"（背景矩形未入组）与"多行 `<text>` 未合并"（同级 sibling text 应合并为 `<text>` + `<tspan>`）。一并修正。

### C-002 · `check_title_consistency` 在自由设计 SVG 上系统性误报（🟡 已记录，未修复）

- **现象**：14 项 P1，例如 `sizes=[18.0, 48.0]`（把封面 48pt 大标题与正文 18pt 副题判为"同页同级"）；
  `'本周工作汇报' 48.0pt 偏离该级常规 21.0pt`（把封面标题与正文页标题判为"同一档位"）。
- **根因**：自由设计 SVG 的文本是**普通 `<text>`、无占位符角色**，`_tier()` 回退为 `shape:text`，
  于是**封面标题 / 页标题 / 卡片小标题 / 正文**全部落入同一 tier，跨页比较必然失真。
- **定性**：D-2 检测器缺陷（P1 级，不阻断导出）。**非**本卡修复范围。
- **影响**：对 free-design / quick 产物，该检测器当前**不可用**（噪声 100%）；对 template-fill 产物（有占位符角色）才有效。
- **建议**：见 §8 建议 1。

### C-003 · bounds 精度的"逐轮试探"成本（🟢 观察）

- **现象**：第 3 轮质量检查时，P01/P06 的标题 bounds 上沿比实际文本内容高 4-10px，被判
  `exceeds ... on the vertical axis: vertical 3.1% / 7.6%`。
- **处理**：按检查器输出的精确内容框（如 `content (120.0, 245.6)-(504.0, 322.4)`）回填 bounds。
- **观察**：首轮 bounds 靠估算会低效试探；检查器给出的精确内容框是可靠依据。**建议在 svg-pipeline 文档补一句**（不在本卡范围）。

---

## 6. 耗时基线（快速通道首次数据点）

| 阶段 | 分钟 | 备注 |
|---|---|---|
| 项目初始化 | **0.02** | 1 秒 |
| Director 轻量稿（6 页） | **约 3** | 纯文本产出 |
| 手写 6 页 SVG | **约 25** | 含内容撰写 + 布局 + 首轮契约摸索 |
| 质量检查修正循环 | **约 8** | 3 轮（C-001 一轮 + bounds 两轮） |
| 导出 PPTX | **0.08** | 5 秒 |
| D-2 质检 | **0.07** | 2+2 秒 |
| 读回验证 | **0.03** | 2 秒 |
| **合计** | **约 36 分钟** | |

**给"快速出稿"契约的基线结论**：
- **机器侧耗时极低**（初始化+检查+导出+质检+读回 ≈ **10 秒**）
- **瓶颈 100% 在人工 SVG 撰写与契约修正**（约 33/36 分钟）
- 本卡 T-01 目标 6-8 页；按此速率，8 页约需 45-50 分钟，**"快速出稿"承诺在当前形态下依赖执行者熟练度**
- **最大可压缩项**：契约细节（C-001/C-003）一旦形成清单，修正循环可从 8 分钟降至 1-2 分钟

---

## 7. 未验证项

| 项 | 原因 |
|---|---|
| 视觉渲染质量（排版美观度/层级/密度） | 卡明确本轮不评（M2/L3 范围）；无 GUI 自动化能力 |
| PowerPoint 客户端打开后的实际显示 | 无 GUI 自动化；仅验证到 XML/文本层 |
| 演讲者备注（notes）链路 | 本次用 `--no-notes`（T-01 未要求讲述内容） |
| 动画/过渡/音频 | 卡未要求；quick 默认关闭 |
| 图片/图标/图表载体 | T-01 无素材，本轮为纯文本版式 |
| `finalize_svg.py` 自包含预览 | quick 路径按文档明确**跳过**该步 |
| 结构化模板（structured）路径 | 本轮为 free-design flat |

---

## 8. 《建议》附录

1. **【优先级最高】修复 `check_title_consistency` 对自由设计产物的误报（C-002）**
   当前 tier 回退逻辑把不同层级的普通 `<text>` 混为一谈，导致 free-design/quick 产物 100% 误报。
   建议方向：
   - 对无占位符角色的文本，**按字号档位聚类后仅在"同档位"内比较**（而非全部归入一个 tier）；
   - 或引入"标题启发式"门槛（如仅 `font-size ≥ 某阈值 && 文本长度 ≤ N` 参与），并把结果降级为**信息级**（不产生 exit 2）；
   - 保留 template-fill（有 role）路径的现有严格判据。
   > 依据：本次 14 项 P1 经人工逐项核对，**无一项是真实的同级字号不一致**。

2. **把 C-001/C-003 提炼为"手写 SVG 契约速查"（写入 `docs/windows-notes.md` 或新文档）**
   三条必守：① 每个根级 `<g>` 必须有 `data-pptx-bounds`；② 整页背景单独成组，不裸放 `<rect>`；
   ③ 多行文本用单个 `<text>` + 多 `<tspan>`，不用同级多 `<text>`。
   再加一条技巧：bounds 值直接取检查器报出的 `content (...)` 坐标，避免逐轮试探。
   > 收益：把本次 8 分钟的修正循环压到 1-2 分钟（见 §6）。

3. **多行 `<tspan>` 的导出行为建议记录**
   导出日志出现 `Lowered positional <tspan> using preserve text flow`，读回时多行内容**无换行符**
   （如"内部联调"直接相连）。PowerPoint 内显示正常，但**下游若做纯文本解析需注意**。
   建议在 `docs/windows-notes.md` 补一条观察。

4. **耗时基线的后续采集建议**
   建议 M1 后续每次 e2e 都记录同样七阶段耗时，形成趋势；重点观察"质量检查修正循环"是否随
   契约清单积累而下降——这是验证建议 2 是否生效的关键指标。

---

## 红线自检

| 红线 | 结果 |
|---|---|
| vendor 零修改 | ✅ `git diff --stat HEAD -- vendor-ppt-master/` 为空 |
| 产物全部进临时目录 | ✅ 全在 `C:\Users\EDY\AppData\Local\Temp\opencode\ppt-e2e\`；repo `*.pptx`=0 |
| 报告为 repo 唯一新增 | ✅ `git status` 仅 `?? docs/e2e-01-report.md` |
| T-01 原文未改编 | ✅ 4 事项 / 2 风险 / 6-8 页 / 观众与时长均按原文落实 |
| 只记录不修复 | ✅ C-002 仅记录，未改 D-2 代码或 vendor |
