# 渲染预览（visual preview pipeline）

> 位置：`deltas/render-preview/`（repo 定制层，vendor 零依赖、零修改）
> 用途：把 `.pptx` 渲染成**逐页 PNG + 一张 contact sheet**，建立像素级视觉验证能力。
> 状态：本机唯一可用渲染路径 = **WPS Office 提供的 PowerPoint COM**（见 §1）。

## 1. 渲染器选择逻辑与可用性矩阵

脚本按以下优先序探测（`--probe-only` 可单独运行）：

| 优先 | 渲染器 | 本机探测结果 | 说明 |
|---|---|---|---|
| a | **PowerPoint COM** | ✅ **可用** | `New-Object -ComObject PowerPoint.Application` 成功；但 `Application.Path` 指向 `D:\WPSOFF~1\...\office6` —— 即 **COM 服务器由 WPS Office 提供**（版本号 12.0 是 WPS 的 Office 兼容接口版本，非 MS Office） |
| b | LibreOffice headless | ❌ 不可用 | 三个常见路径均无 `soffice.exe` |
| c | 其他 | ❌ 无 | MS Office / WPS 独立可执行文件路径均探测失败（WPS 以 COM 方式注册，无独立 `wpp.exe` 于常见路径） |

**为什么选 COM**：它是本机唯一能真正产出 PNG 的路径。实测 `Presentation.Export(outdir, "PNG", w, h)` 成功导出全部页。

### 关键兼容性注意（实测踩坑）

1. **必须用 `-File` 调用 PowerShell 脚本**
   `powershell -Command "<script>" -args <p1> <p2>...` 的传参方式下，
   `Presentations.Open(...)` 会抛 `HRESULT E_FAIL`；改为把脚本写入 `.ps1` 再用 `-File` 传参即正常。
   脚本已按 `-File` 方式实现。
2. **导出文件名是本地化的**
   WPS 写出的是 `幻灯片N.PNG`（中文）。脚本统一重命名为 `slide-NN.png`，避免下游处理非 ASCII 文件名。
3. **Windows 文件系统大小写不敏感**
   同时 glob `*.PNG` 与 `*.png` 会**重复匹配同一批文件**（曾导致 6 页 deck 被识别为 12 页）。
   脚本改为单次收集后按规范化路径去重。
4. **重跑会残留旧产物**
   脚本在渲染前清空 `slide-*.png` 与 `_raw/`，避免新旧混合。

## 2. 依赖

| 依赖 | 用途 | 来源 |
|---|---|---|
| Windows + PowerShell | 调起 COM | 系统自带 |
| **WPS Office（或 MS Office）** | COM 渲染服务 | 本机已装（WPS） |
| **Pillow** | 拼 contact sheet、图片分析 | python-pptx 的依赖，通常已装 |
| python-pptx | 未使用（本脚本不解析 pptx） | — |

**不依赖 vendor 任何文件**，可独立运行。

## 3. 用法（Windows 侧 python）

```powershell
# 探测渲染器可用性
python deltas\render-preview\render_png.py probe --probe-only

# 渲染一份 deck（输出到 <stem>-render\）
python deltas\render-preview\render_png.py deck.pptx

# 指定输出目录 / 尺寸 / 网格列数 / 跳过 contact sheet
python deltas\render-preview\render_png.py deck.pptx -o C:\out --width 1920 --height 1080 --cols 5
python deltas\render-preview\render_png.py deck.pptx --no-contact
```

**产物结构**：

```text
<outdir>/
├── slide-01.png ... slide-NN.png    # 每页一张，默认 1280x720
├── contact-sheet.png                # 网格图，含 "slide NN" 标签
└── _raw/                            # COM 原始输出与临时 ps1（可删）
```

## 4. 环境注意（W-3 / W-6 / 新增 W-8）

- **W-3（WSL 路径不能传 Windows python）**：所有路径参数必须是 `C:\...` 形式；
  脚本自身也用 `os.path` 处理，不经由 WSL 侧解析。
- **W-6（工作目录陷阱）**：脚本不依赖 CWD，输入输出全部走显式绝对/相对参数。
- **W-8（新增，实测发现）· 渲染产物会被端点加密软件加密**
  本机安全软件对**新写入文件做透明加密**：COM 写出的 PNG 在 Windows 进程中读是正常 PNG
  （`89 50 4E 47`），但从 WSL 读会看到 `%TSD-Header-###%` 头。
  **影响**：WSL 侧工具（含 harness 的图片查看器）**无法直接读取渲染结果**。
  **绕行**：所有图片处理（缩略图、contact sheet、像素分析、ASCII 预览）一律在
  **Windows Python 进程内**完成（Pillow）。本脚本即按此实现。

## 5. 已知边界

- 仅实现了 COM 路径；若某机器只有 LibreOffice，需另写 `soffice --headless --convert-to pdf`
  + PDF 栅格化的分支（本机无 LibreOffice，未实现、未验证）。
- contact sheet 的缩略图尺寸固定（420×236），页数很多时会生成很高的图（21 页 → 1770×1698）。
- 不做视觉质量判断（排版美观度等），只产出图片与基础统计（唯一色数等）。
  真正的视觉评审由人或后续 L3 流程完成。
