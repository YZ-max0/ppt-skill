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
