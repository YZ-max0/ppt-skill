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

**判据：双路径（T-FIX2 引入）**

同一份 deck 内两条路径并行，按 shape 是否有占位符角色分流：

| 路径 | 适用产物 | tier 定义 |
|---|---|---|
| **占位符路径** | template-fill（有 role） | 具体 placeholder 类型：`center_title` / `title` / `subtitle` / `body` / `object` |
| **自由设计路径** | quick / flat（无 role） | **字号聚类分档**：`text@<low>-<high>`，如 `text@48`、`text@27-30` |

> 为何需要双路径：free-design 的文本是普通 `<text>`、无角色信息。早期版本把它们全部归入单一
> `shape:text` tier，导致封面 48pt 与正文 18pt 被判"同级"，在 e2e 产物上产生 **14 项 100% 假报**
> （见 `docs/e2e-01-report.md` C-002）。分档后同一产物 **P1=0**。

**分档规则**：收集全部非占位符标题的 `size_pt`，排序后按 `--size-bucket-gap`（默认 **4.0pt**）
切分——相邻字号差距超过该值即另起一档。同档内执行原有的「同页 spread」与「跨页偏离」检测。

**报告门槛（仅自由设计路径，两条比较路径共用同一门槛）**

无论**同页 spread** 还是**跨页偏离**，bucket tier 都必须先满足"存在明显主导字号"才会报告：

| 情形 | 主导占比 | 判定 |
|---|---|---|
| 同页 28pt + 24pt（每档各 1 个，不同角色共享一档） | 0.50 | **不报**（无可靠"同级"） |
| 同页 28pt×2 + 24pt×1（真漂移） | 0.67 | **报** 24pt 偏离 |
| 跨页 6×28pt + 1×24pt（真漂移） | 0.86 | **报** 24pt 偏离 |

若一档内字号分布均匀（多个不同文本角色挤在同一档），该档没有可靠的"同级/常规字号"，
其差异不报告——否则即为噪声。**占位符路径不受此门槛约束**（role 是 ground truth）。

- 同页同级（同 tier）标题字号差 > **0.5pt** → P1。
- 跨页：某标题字号偏离该 tier 的主导字号 > 0.5pt → P1（无"同页需有 keeper"前置条件）。
- **去重**：同一 shape 若已被同页 spread 报告，不再重复出现在跨页偏离结果中
  （两者同根因，重复报告只会虚增计数）。
- 全部发现为 P1（咨询性）；退出码 `0` = 无发现，`2` = 有发现。

**`--size-bucket-gap` 参数**：调整自由设计路径的分档粒度。
默认 `4.0`（可检测 28→24 这类 4pt 漂移）；调小（如 `1.0`）分档更细、假报更少但可能漏检小幅漂移；
调大则相反。可用它针对特定产物调优。

**`--dominance-min` 参数**：调整自由设计路径的**报告门槛**（默认 `0.6`，取值 0-1）。
调低（如 `0.5`）报告更多（含 1:1 双候选）；调高（如 `0.9`）报告更少。与 `--size-bucket-gap` 配合调优：

```powershell
# 更激进：50/50 分摊也视为可疑
python check_title_consistency.py deck.pptx --dominance-min 0.5
```

**⚠️ 已知局限（分档法的本质边界，不掩饰）**：
- **跨档漂移不可检**：若某页标题被改到**另一个档位**（如 28pt 改成 18pt，差距超过 gap），
  它会落入不同 bucket，**不会被报告**。无角色信息时，无法把"跨档漂移"与"本就是更小的层级"区分开。
  这是分档法的固有边界；需要跨档检测时必须依赖占位符角色（template-fill 路径）或人工核对。
- **主导字号门槛**：档内分布均匀（无主导字号）时该档不报告，可能同时压掉真阳性。
  这是**同页与跨页共用**的门槛；`--dominance-min` 可下调以放宽。
- 标题候选的识别仍是启发式（占位符 role 或"短文本 + 字号 ≥18pt"），不是语义判断。

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
