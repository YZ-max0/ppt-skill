# D-2 填充质检（出框检测 + 标题字号一致性）

> 位置：repo 定制层 `deltas/pptx-fill-check/`（与 `vendor-ppt-master/` 平级，**不进入 vendor**）。
> 用途：`template-fill-pptx` 路由 **apply 之后 / 交付之前** 的后置物理质检，与 base 的 `check-plan`（填充前预算）互补。
> 平台：Windows + `python`（本机为 `C:\Users\EDY\AppData\Local\Programs\Python\Python312\python.exe`）。

## 为什么需要它

- base `check-plan` 是**填充前**的文字容量预算（读 `slide_library.json` 的几何/字号估算）。
- 实际填充后，字号继承、autofit、换行、文本插入都可能让"预算放得下"变成"产物溢出"。
- 本目录三个脚本直接读**产物 .pptx**（不依赖 detail.json），做**后置**估算与一致性检查。

## 依赖

只允许 `python-pptx` + Python 标准库。`python-pptx` 已包含在 base `vendor-ppt-master/requirements.txt`；独立安装：

```powershell
python -m pip install python-pptx
```

## 文件与用法

```text
deltas/pptx-fill-check/
├── capacity.py                 # 提取每个文本 shape 的容量数据（也可独立运行）
├── detect_overflow.py          # CLI：出框检测（P0/P1/OK）
├── check_title_consistency.py  # CLI：同级标题字号一致性（P1）
└── README.md
```

### 1) capacity.py —— 容量提取

```powershell
python deltas/pptx-fill-check/capacity.py <filled.pptx> [-o out.json]
```

对每个文本 shape 输出：页 / shape_id / 名称 / role / 盒尺寸(cm) / 解析后字号(pt) / autofit / wrap / cpl（每行容量 vw）/ max_lines / capacity_vw。

### 2) detect_overflow.py —— 出框检测

```powershell
python deltas/pptx-fill-check/detect_overflow.py <filled.pptx>
python deltas/pptx-fill-check/detect_overflow.py <filled.pptx> --json [-o out.json]
```

**判档（阈值统一 1.2×；判据按 wrap 分轴）**：

阈值语义（`--tolerance`，默认 1.2）：

| 用量 | 判定 |
|---|---|
| ≤ 1.0 | OK |
| 1.0 – `--tolerance`（默认 1.2） | P1（接近上限，建议目检） |
| > `--tolerance` | **P0**（阻断建议） |

**判据分两轴——这是 T-FIX1 修复的核心，不可混用**：

| `wrap` | 判据轴 | 度量 | 适用原因 |
|---|---|---|---|
| `True` | **垂直轴** | 折行需求行数 / 盒子行容量（`demand / max_lines`） | 文本在盒内折行，行数是有意义的约束 |
| `False` | **水平轴** | 最长单段视觉宽度 / 每行容量（`longest_vw / cpl`） | 文本**不折行**，行容量恒为 1、无信息量；溢出只可能发生在水平方向 |

> 历史缺陷（T-FIX1 修复）：早期版本对 `wrap=False` 仍用行数判据，导致任何多字符标签恒得
> `usage ≥ 2.0` → 系统性假 P0（真实 vendor 产物上 32 处误报）。现已按上面的分轴修复。

**自动软放行（与判据轴无关）**：以下两种 auto-size 都消除真实溢出风险，一律判 OK 并附说明：

| `auto_size` | 语义 | 处理 |
|---|---|---|
| `TEXT_TO_FIT_SHAPE` | PowerPoint 自动缩小文字以适应盒子 | OK（软放行） |
| `SHAPE_TO_FIT_TEXT` | **盒子随文字缩放**，量到的盒尺寸即文字实际范围 | OK（软放行；SVG→PPTX 分组文本默认走此模式） |

输出每处（按轴显示不同度量）：

```text
[P0] 页2 形状:XX平台数据中台架构说明…… | 垂直: 需求 4 行 / 容量 3 行 (18pt) | 超出容量 >20% (usage=1.6) | 建议: 建议压缩间距/删减内容（40-90px 量级）
[P0] 页3 形状:TARGET PROGRESS DETAIL | 水平: 最长段宽度比 3.57 (每行容量 3 字当量) (14pt) | 水平超宽 >20% (usage=3.57) | 建议: 建议换更宽的槽位或大幅缩短文字（>90px 量级）
=== 摘要: 1 处 P0 / 2 处 P1 / 5 处 OK ===
```

**`--tolerance` 参数**：覆盖默认 1.2（乘数，非百分比）。
`--tolerance 1.0` = 关闭 20% 松弛（严格几何判据）；`--tolerance 1.5` = 更宽松。
例如同一份 `usage=1.2` 的样张：默认下判 P1（exit 0），`--tolerance 1.0` 下判 P0（exit 2）。

**退出码**：`0` = 无 P0；`2` = 存在 P0（供 CI/脚本阻断）。

**修正阶梯提示（建议文案，非像素实测）**：≤40px 微调 / 40-90 压间距 / 90-160 压标题 / 160+ 换版式。

### 3) check_title_consistency.py —— 标题字号一致性

```powershell
python deltas/pptx-fill-check/check_title_consistency.py <filled.pptx>
python deltas/pptx-fill-check/check_title_consistency.py <filled.pptx> --json [-o out.json]
```

**判据（已裁决：0.5pt 差异，更严格）**：

- 同页同级（同 placeholder tier：title/subtitle）标题字号差 > **0.5pt** → P1。
- 跨页：某标题字号偏离该 tier 的常规档位（多数页所用字号）> 0.5pt，且同页仍有同级标题保持常规档 → P1。
- 全部发现为 P1（咨询性）；退出码 `0` = 无发现，`2` = 有发现。

## 挂载点结论

应插入 `vendor-ppt-master/workflows/template-fill-pptx.md`：

```text
Step 6 apply（产出 exports/*.pptx）之后
        ↓
[本 D-2 质检] detect_overflow.py <filled.pptx>    # P0 阻断
[本 D-2 质检] check_title_consistency.py <filled.pptx>  # P1 咨询
        ↓
Step 7 validate（read-back 校验）
```

实现上本目录文件不改动 vendor；上述挂载点作为流程约定记录在此（是否把命令写进 vendor 工作流文档由 D-6 路由/指挥官另行决定——按 DELTAS 定制规则，vendor 只允许追加挂载条款，本 README 不修改 vendor）。

## 与 check-plan 的关系

| 阶段 | 工具 | 输入 | 性质 |
|---|---|---|---|
| 填充前 | base `check-plan` | slide_library + fill_plan | 预算估算，警告可接受 |
| 填充后 | 本目录 `detect_overflow.py` | 产物 .pptx | 物理几何后置检测，P0 阻断建议 |
| 填充后 | 本目录 `check_title_consistency.py` | 产物 .pptx | 标题档位一致性，P1 咨询 |

## 局限（诚实声明）

- 本工具是**几何估算**，不是 PowerPoint 渲染引擎：autofit 实际缩字量、字体回退、禁则处理等以 PowerPoint 实际渲染为准。
- 水平轴的 `cpl` 由盒宽减去固定内缩（0.25cm）估算；真实文本框可能带自定义 `margin_left/right`，此时宽度预算会偏保守或偏宽松。
- `usage` 分母是 `max_lines × cpl`（含行高假设 1.0）；多段落按行数累加需求，不模拟单词级换行。
- 修正阶梯中的 px 数值为参考文案，不来自真实像素测量。
- 只支持文本溢出估算；图片/表格/图表溢出不在 D-2 范围。

## 验收记录（T-D2）

- 样例文件（不溢出 / 溢出 P1 / 溢出 P0 + 标题不一致）在临时目录构造并用 Windows `python` 跑通；样例不进入 repo。
- `git status` 确认无 vendor 路径改动（T-D2 只新增本目录 4 文件）。
