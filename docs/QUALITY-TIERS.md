# 质量档位（QUALITY TIERS）

> 一页纸决策表：**不同质量需求 → 走哪条流程**。
> 详细操作步骤见 [`USAGE.md`](USAGE.md)；环境注意见 [`windows-notes.md`](windows-notes.md)。

本 Skill 提供**三档质量**。区别不在"做得更多"，而在**加了几道思考环节与校验门**。
三档共用同一套骨架库（`deltas/layout-assets/`，29 个）与同一套导出链路。

---

## 总览对照

| 档位 | 适用场景 | 额外环节 | 校验门 | 实测耗时 |
|---|---|---|---|---|
| **① 快速出稿** | ≤8 页 / 时效紧 / 素材现成 | 无 | checker（1 道） | **~4 分钟**（6 页） |
| **② 标准** | 常规汇报，内容需组织 | Director 轻量稿 | checker + D-2（2 道） | ~10 分钟 |
| **③ 导演式** | 重要汇报 · 决策者 · ≥10 页 | **A→B→B2→C 四阶段** | checker + D-2 + 渲染 + L3 人工（4 道） | 机器 ~5 分钟，**内容撰写另计** |

> **耗时说明**：机器侧成本几乎与页数无关（实测：6 页 ~1.2 分钟 / 21 页 ~1.3 分钟机器侧）。
> 差异主要来自**内容撰写与思考**——这正是③的价值所在。

---

## ① 快速出稿

**何时用**：素材完备、页数 ≤8、时效紧、你心里已有结构。

**流程**

```text
init --quick-generate → 选骨架 → 替换【槽位】→ checker → 导出
```

**校验**（只此一道）

```powershell
python <vendor>\scripts\svg_quality_checker.py "<proj>" --quick-generate --stage final --json
# 要求：blocking = 0
```
外加：填充后断言产物 `【` 计数 = 0（W-7）。

**不做的**：不写导演稿、不做 D-2 质检、不做渲染验证、不评审视觉。

**推荐配方**（已验证）

```text
P01 cover           封面
P02 bullets         本周完成事项
P03 two-col-compare 风险与对策
P04 timeline        下周计划
P05 three-card      关键数据 / 需要的支持
P06 closing         总结
```

**产物**：`<proj>/exports/<名称>_<时间戳>.pptx`

---

## ② 标准

**何时用**：内容散在脑子里，需要先理成结构，但不要求导演级严谨。

**流程**：① 的全部 + **一层轻量导演稿**（`deltas/director.md` §7）

```text
受众 3 句：给谁听 / 他要什么结果 / 讲述尺度
每页一行：观点标题 + ≤3 要点 + 页型
   ↓
进入 ① 的流程
```

**校验**：① 的 checker + **D-2 后置质检**

```powershell
python deltas\pptx-fill-check\detect_overflow.py "<pptx>" --json
# 判读：P0 = 0 才算过（exit 0）；P1 建议目检
python deltas\pptx-fill-check\check_title_consistency.py "<pptx>" --json
# 判读：P1 为咨询性，人工确认真伪
```

---

## ③ 导演式（最高质量）

**何时用**（`deltas/director.md` §1 裁决规则）

| 输入特征 | 走这条 |
|---|---|
| 仅主题 / 想法 / 材料不完整 | ✅ 导演式 |
| **重要汇报**（决策者 / 管理层 / 评审）**且 ≥10 页** | ✅ 导演式（完整四阶段） |
| 素材完备、≤8 页、时效紧 | ❌ 走 ① |
| 已有成稿 PPTX | ❌ 走 base 的 Enhance Native 路由 |

### 四阶段（**B2 是硬门禁，不得跳过**）

| 阶段 | 做什么 | 产出 | 门禁 |
|---|---|---|---|
| **A · 受众画像** | 听众身份 / 关注点（驱动力排序）/ 演讲目标 / 知识底色 / 禁忌 | 受众卡（**5 字段**） | 无硬门禁；3 句以内钉死视角 |
| **B · 内容打磨** | 每页 **10 字段**：观点标题 / 核心结论 / 页型 / 版式 / 主视觉 / 主视觉内容 / 面积预算 / 上屏文案 / 收束 / 风险 | 逐页导演稿 | 导演稿**禁止写设计语言**（颜色/字体/坐标属设计层） |
| **B2 · 视觉导演优化** | 把内容稿压成"上屏短句" + 写明主视觉**解释什么逻辑**（不是长什么样） | B2 优化稿 | ⛔ **硬门禁：未过 B2 不得进 C** |
| **C · 映射生成** | 导演稿 → 选骨架 → 填充 → 导出 | `.pptx` | base 确认门 |

### 四道校验（全上）

| 层级 | 内容 | 阻断规则 |
|---|---|---|
| **L1 自动校验** | 结构 / 溢出 / 乱码 / 风格漂移 | **失败即阻断（P0）** |
| **L2 自动回归** | golden samples 截图 diff | 日常每次跑 |
| **L3 人工抽检** | 抽关键页（封面 / 目录 / 典型内容 / 图表页），按 3 维度 2 分制打分：信息层级 / 视觉密度 / 风格一致性 | **< 4/6 分 → 该风格进"反例库"** |

外加（本仓库补充的硬约束）：

| 约束 | 出处 |
|---|---|
| 深色页预算 **≤15% 页数** | `deltas/layout-assets/v2/CONTRACT.md` v2-4 |
| 骨架内层级字号差 **≥6pt** | `deltas/layout-assets/v0/CONTRACT.md` 第 7 条 |
| 渲染 + contact sheet **人工目视** | `docs/m2-render-report.md` |

```powershell
# L1 / L2 的自动化门
python <vendor>\scripts\svg_quality_checker.py "<proj>" --quick-generate --stage final --json
# 渲染供 L3 人工抽检
python deltas\render-preview\render_png.py "<pptx>" -o "<输出目录>"
# → slide-NN.png + contact-sheet.png（需在 Windows 上目视，见 W-8）
```

---

## 决策速查

| 你的场景 | 走哪档 |
|---|---|
| 明天的周报，内容心里有数 | **①** |
| 部门季度汇报，要讲清逻辑 | **②** |
| 给决策者的方案提案 / 融资路演 / 评审答辩 | **③** |
| 已有一份 PPT，只想加备注 / 动画 | 不走这三档 → base **Enhance Native** 路由 |
| 有 PPT 模板，只想填新内容 | 不走这三档 → base **Fill Native** 路由 |
| 已有图片页面，想还原成可编辑 PPTX | 不走这三档 → base **Image to PPTX** 路由 |

---

## 质量上限（诚实说明）

即使走 ③，**视觉质量上限受限于骨架库的形态**：

| 限制 | 说明 |
|---|---|
| **图片位已支持** | v3 提供 3 个图片骨架（`image-hero`/`image-split`/`image-grid`）；素材需用户提供或程序生成（见 `docs/image-strategy.md`） |
| **图表是静态 SVG** | 非 PowerPoint 原生数据图表；数据变化需按 `v2/CONTRACT.md` §2 公式手工重算坐标 |
| **无动画/过渡设计** | 可另走 base 的 animations 能力 |
| **单一渲染器** | 本机仅 WPS COM 可用（无 LibreOffice 备选） |
| **视觉评审需人工** | 加密限制使自动化无法目视，contact sheet 必须人类查看 |

> 视觉冲击力评分为 **4/6**（v2 增强后）。需要"大图 / 复杂图表 / 动效"时，当前骨架库是瓶颈。

---

## 三档共享的部分

无论哪一档，以下环节相同：

| 环节 | 说明 |
|---|---|
| 项目初始化 | `init ... --dir "<工作目录>" --quick-generate`（**必须带 `--dir`**，见 W-6） |
| 骨架选择 | 从 `deltas/layout-assets/{v0,v1,v2}/` 按页型选（索引见 `USAGE.md` §3） |
| 占位符替换 | 整段替换 `【槽位名】示例内容`，**不得动坐标 / bounds / 字号** |
| 导出 | `svg_to_pptx.py "<proj>" --quick-generate --no-notes`（要备注换 `--with-notes`） |
| 环境纪律 | 全部命令在 **Windows 侧**用 `python` 执行（见 W-1~W-8） |

---

## 相关文档

| 文档 | 内容 |
|---|---|
| [`USAGE.md`](USAGE.md) | 逐步操作、24 骨架索引、场景配方、请求模板 |
| [`windows-notes.md`](windows-notes.md) | W-1~W-8 环境绕行细节 |
| [`../deltas/director.md`](../deltas/director.md) | ③ 的完整规范（A/B/B2/C、10 字段、区域词清洗） |
| [`../deltas/layout-assets/v0/CONTRACT.md`](../deltas/layout-assets/v0/CONTRACT.md) | 骨架通用硬标准与逐槽位清单 |
| [`../deltas/layout-assets/v2/CONTRACT.md`](../deltas/layout-assets/v2/CONTRACT.md) | 图表族数据映射、锚点族规则、深色页预算 |
| [`../vendor-ppt-master/workflows/routing.md`](../vendor-ppt-master/workflows/routing.md) | base 的四条顶层路由权威 |
