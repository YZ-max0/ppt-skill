# M2 视觉验证能力报告（T-M2A）

> 执行者：开发工程师 ｜ 日期：2026-09-11 ｜ 卡：`tasks/T-M2A.md`
> 目标：建立第一个**像素级**验证闭环（此前所有验收都是结构级）
> 结论：**渲染链路打通** —— WPS COM 可用，3 份 deck 全部渲染成功（6+6+21 页 + 3 张 contact sheet）

---

## 1. 渲染器可用性矩阵

| 优先 | 渲染器 | 探测命令 | 结果 | 版本/路径 |
|---|---|---|---|---|
| a | **PowerPoint COM** | `New-Object -ComObject PowerPoint.Application` | ✅ **可用** | version `12.0`，`Application.Path` = `D:\WPSOFF~1\1210~1.285\office6` |
| b | LibreOffice headless | `C:\Program Files\LibreOffice\program\soffice.exe --version` 等 3 路径 | ❌ 不可用 | `not found` |
| c | 其他（MS Office / WPS 独立 exe） | `POWERPNT.EXE` / `wpp.exe` 常见路径 | ❌ 不可用 | 均 missing |

### 重要发现：COM 服务器是 WPS 而非 MS Office

虽然 ProgID 是 `PowerPoint.Application`，但 `Application.Path` 指向 **WPS Office 的 office6 目录**
（`D:\WPSOFF~1\1210~1.285\office6`），版本号 `12.0` 是 WPS 提供的 Office 兼容接口版本。
这解释了为什么探针 c 在 MS Office 常见路径上全部落空。

**实践意义**：COM 路径的能力边界取决于 WPS 的实现。本次实测 `Presentation.Export` 工作正常；
但若将来遇到 WPS 不支持的方法（如某些动画/导出参数），需回退到其他路径。

### 渲染能力实测（探针 d）

`Presentation.Export(outdir, "PNG", 1280, 720)` → **成功**，WPS 写出 `幻灯片1..N.PNG`（本地化命名），
尺寸精确 **1280×720**。

---

## 2. 渲染结果（3 deck）

全部产物位于 `C:\Users\EDY\AppData\Local\Temp\opencode\ppt-render\`。

| deck | 源文件 | 页数 | 渲染页数 | contact sheet 尺寸 | 耗时 |
|---|---|---|---|---|---|
| **t01** | `t01-weekly_20260911_133607.pptx` | 6 | ✅ 6 | 1770×578 | ~8 s |
| **t01b** | `t01b-assets_20260911_151935.pptx` | 6 | ✅ 6 | 1770×578 | ~8 s |
| **t03** | `t03-proposal_20260911_153940.pptx` | 21 | ✅ 21 | 1770×1698 | ~25 s |

**文件清单（结构）**：

```text
ppt-render/
├── t01/    slide-01..06.png  + contact-sheet.png  + _raw/
├── t01b/   slide-01..06.png  + contact-sheet.png  + _raw/
└── t03/    slide-01..21.png  + contact-sheet.png  + _raw/
```

每张 PNG：**1280×720**（150 DPI 等效的 16:9 画布）。

### 渲染正确性验证（程序化，因为无法目视——见 §3）

**① 空白检测**（唯一色数统计）：全部 33 页唯一色数 **86 – 2391**，无空白页。

| 范围 | 值 | 说明 |
|---|---|---|
| 最高 | 2391 色（t01b slide-02） | 多卡片 + 文字，内容最密 |
| 最低 | **86 色**（t03 slide-21） | 结尾页仅 2 个文本元素，**符合设计预期**（稀疏页） |
| 深色页 | t01 slide-05 / t03 slide-20 主色为 `(10,10,10)` | 排版确为深色背景页 ✅ |

**② ASCII 结构预览**（把 PNG 降采样为字符图，验证版式与 SVG 设计一致）：

| 页 | 预览观察 | 与 SVG 设计对照 |
|---|---|---|
| t03 slide-01（封面） | 左侧竖色条 + 中部大标题块 + 底部两行小字 | ✅ 与 `cover.svg` 一致 |
| t03 slide-16（budget-4） | 顶部标题 + **4 组「数字 + 说明」** + 底部通栏合计块 | ✅ 与 `budget-4.svg` 一致 |
| t03 slide-20（decision-3） | **整页深色** + 顶部反白标题区 | ✅ 与 `decision-3.svg` 一致（深色页） |

**结论**：渲染**忠实反映**了 SVG 设计意图，非空白、非错位。

---

## 3. ⚠️ 关键环境发现：渲染产物被端点加密软件加密

**现象**：COM 写出的 PNG 在 **Windows 进程**中读取正常（首字节 `89 50 4E 47` = PNG 魔数），
但从 **WSL 进程**读取会看到 `%TSD-Header-###%` 头 —— 即被安全软件透明加密。

**证据**：
```text
WSL 侧:        head -c 16 slide-02.png  →  %TSD-Header-###%
Windows 侧:    [IO.File]::ReadAllBytes →  89 50 4E 47 0D 0A 1A 0A   (PNG 正常)
```

**影响**：WSL 侧工具（包括 agent 的图片查看能力）**无法直接读取渲染产物**，
因此本轮**无法由我目视确认视觉效果**，只能用 Windows 侧 Pillow 做程序化验证
（唯一色数统计 + ASCII 结构预览）。

**绕行方案（已实现）**：所有图片处理一律在 **Windows Python 进程内**完成。
`render_png.py` 的 contact sheet 生成、像素分析、ASCII 预览都走 Pillow（Windows 侧），
不经过 WSL 文件读取。

> **这与 TSD 对 vendor 文件的加密是同一机制**（同一安全软件），
> 但方向相反：vendor 是"Windows 能读、WSL 读密文"；本轮渲染产物也是同一现象。
> 已作为 **W-8** 记录进 `docs/windows-notes.md`（见建议 1）。

---

## 4. 脚本化交付（`deltas/render-preview/`）

| 文件 | 行数 | 内容 |
|---|---|---|
| `render_png.py` | 221 | 渲染器探测 + COM 渲染 + contact sheet 生成 |
| `README.md` | 85 | 渲染器选择逻辑、依赖、4 条兼容性踩坑、W-3/W-6/W-8 注意、已知边界 |

**脚本特性**：
- 独立于 vendor（零依赖 vendor 文件）
- `--probe-only` 报告渲染器矩阵
- 自动规范化本地化文件名（`幻灯片N.PNG` → `slide-NN.png`）
- 重跑清理旧产物（避免新旧混合）
- 可配置尺寸/网格列数/跳过 contact sheet

**修复的 3 个实现缺陷**（均在实测中发现）：
1. `-Command ... -args` 传参导致 `Presentations.Open` 报 `E_FAIL` → 改用 `-File` 调用
2. Windows 大小写不敏感导致 `*.PNG` + `*.png` **重复匹配**（6 页被识别为 12 页）→ 去重
3. 重跑残留旧 `slide-*.png` → 渲染前清理

---

## 5. 未验证项

| 项 | 原因 |
|---|---|
| **人工目视确认视觉质量** | TSD 加密阻止 WSL 侧读取 PNG；本轮仅做程序化验证（色数 + ASCII 结构）。**需要人类在 Windows 上打开 contact sheet 目视** |
| 排版美观度/层级/密度评审 | 属 L3 人工抽检范围，且需目视，本轮未做 |
| LibreOffice 路径 | 本机未安装，未实现该分支（脚本未含 soffice 代码路径） |
| 高 DPI 渲染（1920×1080 等） | 脚本支持 `--width/--height`，但未实测其他尺寸 |
| 动画/过渡的渲染 | 静态 PNG 无法反映动画 |
| 字体回退差异 | 未对比"SVG 设计字体"与"实际渲染字体"是否一致（需目视） |

---

## 6. 《建议》附录

### 建议 1【已执行】把 W-8 写入 `docs/windows-notes.md`

渲染产物加密是新发现的环境事实，且会**阻塞任何 WSL 侧的视觉验证工作流**。
建议记录：现象、证据、绕行方案（图片处理必须走 Windows 进程）。

### 建议 2【优先级高】需要人类目视确认本轮渲染结果

程序化验证（色数、ASCII 结构）只能证明"渲染出了东西且版式大致对"，
**不能证明视觉效果良好**。建议由人类在 Windows 上打开 3 张 contact sheet 快速过目：

```text
C:\Users\EDY\AppData\Local\Temp\opencode\ppt-render\t01\contact-sheet.png    (6 页)
C:\Users\EDY\AppData\Local\Temp\opencode\ppt-render\t01b\contact-sheet.png   (6 页)
C:\Users\EDY\AppData\Local\Temp\opencode\ppt-render\t03\contact-sheet.png    (21 页)
```

这是 M2 视觉闭环的**最后一个缺失环节**。

### 建议 3【优先级中】为"渲染 → 视觉评审"建立自动化基线

一旦目视确认基线，建议把以下指标纳入自动回归（现在已能计算）：
- 每页唯一色数（检测"空白页/渲染失败"）
- 与上一版渲染的**像素级 diff 比例**（检测"改版是否意外影响其他页"）
- contact sheet 作为**人工抽检的标准输入**

当前 `render_png.py` 已能产出输入，diff 与阈值判定可留待后续卡。

### 建议 4【优先级中】渲染器冗余

当前**只有一条渲染路径**（WPS COM），是单点依赖。若 WPS 升级/卸载，视觉验证能力立即归零。
建议评估：
- **LibreOffice**（免费、跨平台、可 headless）：需安装，但能提供第二条路径
- **WPS/Office 的 PDF 导出 + PDF 栅格化**：可作为第三路径（`ExportAsFixedFormat`）

> 卡内要求"不擅自安装软件"，故本轮仅**评估**，未安装。

### 建议 5【优先级低】contact sheet 的分页策略

21 页的 contact sheet 高度已达 1698px，页数再多会影响查看。
建议增加 `--rows-per-sheet` 或自动分片（如每 12 页一张 sheet）。

---

## 红线自检

| 红线 | 结果 |
|---|---|
| vendor 零修改 | ✅ `git diff --stat HEAD -- vendor-ppt-master/` 为空 |
| PNG 产物在临时目录 | ✅ 全在 `C:\Users\EDY\AppData\Local\Temp\opencode\ppt-render\`；repo 无图片新增 |
| 不擅自安装软件 | ✅ 未安装任何软件；LibreOffice 仅评估可行性 |
| 渲染失败如实报告 | ✅ 3 处实现缺陷与 TSD 加密限制均如实记录，未伪造截图 |
| 脚本入库 | ✅ `deltas/render-preview/render_png.py` + `README.md` |
