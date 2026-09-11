# Windows 侧执行注意（环境绕行手册）

> 来源：T-SMOKE 冒烟实测（`docs/smoke-report.md` 的 P-1/P-3/P-4/P-5）。
> 用途：避免后续执行者在同一批环境坑上重复排查。
> 环境：Windows + PowerShell 5.1 + `python` 3.12.3（WSL 侧仅作文本工具使用）。

## W-1 · 导出必须走四步序列（P-1）

`svg_to_pptx.py` 直接导出必失败两次，这不是缺陷而是设计上的两道质量门：

1. `spec_lock.md is required for release SVG export` —— 缺 lock
2. `requires a passing final SVG quality report for that svg_output/` —— 缺质量报告

固定序列（缺一步都会被拦）：

```powershell
python <vendor>\scripts\project_manager.py init <name> --format ppt169
python <vendor>\scripts\project_manager.py scaffold-lock <proj>   # 然后填掉 [fill] 占位
python <vendor>\scripts\svg_quality_checker.py <proj> --stage final --json
python <vendor>\scripts\svg_to_pptx.py <proj> --no-notes
```

自动化脚本请固化此顺序；不要只调最后一条。

## W-2 · 控制台中文/UTF-8 乱码会误导判定（P-3）

PowerShell 里 `python script.py` 的中文输出常显示为 `��һҳ...`，但**写入文件的字节完全正确**。
现象与数据无关，纯粹是控制台编码。判定乱码必须看文件字节，不能看屏幕。

绕行：让 python 把结果写 UTF-8 文件，再用文本工具读取。

```powershell
$env:PYTHONIOENCODING='utf-8'
python script.py > out.txt   # PS 5.1 的 > 会写成 UTF-16，仍不可读
```

更可靠：

```python
# 脚本内直接写 UTF-8
with io.open(r'C:\...\result.txt', 'w', encoding='utf-8') as fh:
    fh.write(text)
```

本次冒烟中，`notes_slide` 的中文在控制台显示为乱码，但 UTF-8 文件回读确认与原文**逐字一致**。

## W-3 · WSL 路径不能传给 Windows python/PowerShell（P-4）

`/mnt/c/...` 在 PowerShell 中会被解析为 `D:\mnt\c\...`，报 `PathNotFound`；
且脚本可能**仍继续执行**，产出误导性的二次错误。跨侧调用一律使用 Windows 路径：

```powershell
Set-Location -LiteralPath 'C:\Users\...\proj'   # 用 C:\ 而非 /mnt/c/
python 'D:\...\vendor-ppt-master\scripts\svg_to_pptx.py' 'C:\...\proj'
```

## W-4 · lock 脚手架是占位符，必须先填值（P-5）

`scaffold-lock` 产出的 `spec_lock.md` 满是 `[fill]`，直接导出会被质量门拦下。
必须填真实值，另外两条容易被忽略的硬性要求：

- **typography role 要覆盖实际用到的字号**：真实模板里出现的字号（如 18pt 表头）若未在 lock
  声明 role，会以 `typography-size recurrence` 报 blocking。建议按实际角色补行，如 `table_label: 18`。
- **页面 SVG 必须带 `data-pptx-page-role` 根属性**：缺失会以 `introduced` 报错。

> 补充：`batch_validate.py` 期望**父目录**（扫描其下项目）；传单个项目目录会报
> "No projects found"，且该 `[ERROR]` 的退出码仍是 0 —— 自动化不能只靠退出码判定失败。

## W-5 · 手写 SVG 契约速查（quick / free-design 路径）

来源：M1 端到端首跑（`docs/e2e-01-report.md` C-001/C-003）。首轮质量检查 6/6 全部 blocking，
补齐以下四条后一次通过。**建议在写第一页 SVG 前就按这四条做**，可把修正循环从 ~8 分钟压到 1-2 分钟。

**① 每个根级 `<g>` 必须声明 `data-pptx-bounds`**

```xml
<g id="page-title" data-pptx-bounds="80 50 1120 80"> ... </g>
```

缺失会报 blocking：`Detected N visible root-level <g> module(s) without explicit data-pptx-bounds`。
导出器用该边界做模块定位与溢出诊断，因此它必须**真实包住组内所有可见内容**。

**② 整页背景单独成组，不要裸放 `<rect>`**

```xml
<g id="page-bg" data-pptx-bounds="0 0 1280 720">
  <rect width="1280" height="720" fill="#FFFFFF"/>
</g>
```

裸放会报 `ungrouped top-level Slide-local element(s)`；规则是"只把逻辑内容单元放进根级 `<g id>`"。

**③ 多行文本用单个 `<text>` + 多个 `<tspan>`，不要用同级多个 `<text>`**

```xml
<text x="120" y="475" font-size="16" fill="#737373"><tspan x="120" dy="0">第一行</tspan><tspan x="120" dy="25">第二行</tspan></text>
```

同级多个 `<text>` 会被识别为"段落式换行被拆成兄弟 text"，报
`paragraph-like line run(s) split across sibling <text> elements`。
保持单个 `<text>` 后，导出器统一按段落处理，字号/颜色也只需写一次。

**④ bounds 坐标直接取 checker 报出的 `content (...)`**

若 bounds 比实际内容高或低几个像素，会报
`exceeds <g id="..."> data-pptx-bounds on the vertical axis: ... overflow vertical 3.1%`，
并**直接给出精确的内容框**，例如：

```text
<text> (x=120, y=300; text='本周工作汇报') exceeds <g id="cover-title"> data-pptx-bounds
on the vertical axis: content (120.0, 245.6)-(504.0, 322.4), container (120.0, 250.0)-(1160.0, 390.0)
```

> 直接把这组 `content` 坐标（可外扩 2-4px 余量）回填 bounds 即可，不用逐轮估算试探。

**⑤ 观察：多行 `<tspan>` 导出后读回无换行符**

导出日志会出现 `Lowered positional <tspan> using preserve text flow`。
用 python-pptx 读回时，多行内容**不带换行符**（例如"内部"+"联调"会读成"内部联调"）。
PowerPoint 内显示正常，但**下游若做纯文本解析/比对需自行按 tspan 边界处理**，不要假定有 `\n`。

## W-6 · `project_manager.py init` 的目录陷阱（T-M1A / T-E2E2 实测）

`powershell -Command "cd '<dir>'; python project_manager.py init foo"` 这种写法下，
`cd` 与 python 子进程的工作目录传递**不可靠**——项目可能落在**默认 projects 根**
（本机实测为 `C:\Users\EDY\AppData\Local\Temp\opencode\projects\`），而非 `<dir>`。

现象：命令输出 "Project created: ..." 看起来成功，但 `find <dir>` 找不到项目。

可靠写法（二选一）：

```powershell
# 方案 A：用 Set-Location（-LiteralPath 应对含空格/中文路径）
Set-Location -LiteralPath 'D:\...\workdir'
python 'D:\...\vendor-ppt-master\scripts\project_manager.py' init foo --format ppt169 --quick-generate

# 方案 B：不依赖工作目录，接受默认 projects 根并在该根下继续作业
python '...\project_manager.py' init foo --format ppt169 --quick-generate
# 然后用实际输出路径（命令会打印绝对路径）继续后续步骤
```

**建议**：任何自动化脚本都应从 init 的**输出中解析项目绝对路径**，不要假设它落在预期目录。

## W-7 · 填充后必须断言占位符归零

骨架库（`deltas/layout-assets/`）使用 `【槽位名】` 作占位标记。填充后若漏替换，
占位符会**原样进入 PPTX**（checker 不报错，因为它只校验几何与语法）。

因此任何自动化填充流程都应包含断言：

```python
assert '【' not in svg_text, f'{page}: 占位符残留'
```

并在最终读回验证中检查产物：

```python
ph_count = sum(t.count('【') for t in all_text_frames)   # 必须 == 0
```

T-M1A / T-E2E2 两次实测该断言均有效（21 页产物 `【` 计数 = 0）。
