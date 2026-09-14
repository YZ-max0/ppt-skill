# 任务卡 T-D2 · 填充质检（出框检测 + 标题字号一致性）（P1 · 预计 2-4 小时）

指挥官：opencode ｜ 执行者：待指派 ｜ 版本：v1.0

## 背景

基座 `vendor-ppt-master` 的 **Fill Native PPTX 路由**（OOXML 克隆填补）没有"填完量一量"的后置质检。
同类能力在 Gorden（MIT 源码）已验证有效：按文本框容量估计溢出。本任务实现后置检测器，
挂在 Fill 路由的质量门（不入 vendor，作为 deltas/ 增量）。

集成契约（写死）：`deltas/` 是本 repo 的定制层；基础不被依赖（只读 vendor），只挂不嵌。

## 输入（只读）

| 参考 | 路径 | 用途 |
|---|---|---|
| Gorden 容量计算 | `C:\Users\<you>\.workbuddy\skills\GordenPPTSkill\scripts\compute_capacity.py` | vw 视觉宽度单位（CJK=1.0/拉丁=0.5/空格=0.35）、字号继承解析（`_master_txstyle_sz`/`_defRPr_sz_from_lststyle`）、`capacity_for()` |
| Gorden 溢出检查 | ...`scripts\build_pptx.py`（`check_overflow`/`_visual_width`） | 溢出判据：**优先 vw 总宽 vs 行宽预算；再按行数预算**；容忍度与"1.2x+ 真实溢出"的档位 |
| Gorden 渲染审查 | ...`scripts\render_slides.py` | 渲染 PNG 的辅助思路（本任务不要求，M2 才做） |
| 基座质量门 | `D:\OpenCode_Spaces\PPT skill制作\vendor-ppt-master\workflows\template-fill-pptx.md` | 找它现有校验步骤，确定挂载点（执行者找到后在 README 写明"应于哪一步后运行"） |
| 基座输出风格 | `vendor-ppt-master\scripts\batch_validate.py` | 输出风格对齐：status/errors/warnings 的分级与摘要 |
| 同级标题规则 | `C:\Users\<you>\.workbuddy\skills\GordenPPTSkill\references\workflow.md` | 用 grep 找"标题字号"/"一致性"规则原文，抄原理不抄文 |

## 交付物（全部新建在 `deltas/pptx-fill-check/`）

1. `capacity.py` —— 给定一个 .pptx，提取每个文本 shape 的：盒尺寸(cm)、解析后字号(pt)、是否 autofit、每行容量(vw/行)、行数预算。**不依赖 detail.json，直接从 .pptx shape 读尺寸**（比 Gorden 更通用）。
2. `detect_overflow.py` —— CLI：入参 `python detect_overflow.py <filled.pptx>`，输出每处文本的：
   `[P0|P1|OK] 页N 形状:段落摘要 | 需求X/Y 行 vw，容量 Z 行 | 建议(删减字数/降字号/换版式)`
   - 判档：可用 < 80% → OK；80-125% → P1（提示）；>125% 或 autofit 有 shrink 仍不够 → P0（阻断建议）
   - 溢出修正阶梯提示（guizang 实测经验）：≤40px 微调 / 40-90 压间距 / 90-160 压标题 / 160+ 换版式（仅建议文案）
3. `check_title_consistency.py` —— 同级标题字号一致性：对每页"疑似同级标题"（按字号集群+role），差异 > 该集群中位值 × 1.2 → 报 P1；与 Gorden 的规则对照（规则定性、实现自写）。
4. `README.md` —— 用法、依赖声明（只允许：python-pptx + 标准库；若 python-pptx 不在 base requirements.txt，注明并单独 pip install 说明）、挂载点结论、输出格式示例。

## 硬约束（违反即退回）

1. **只写 `deltas/pptx-fill-check/`**；vendor-ppt-master 内任何文件禁止修改
2. 许可：Gorden 源码 MIT（LICENSE 明确 script 层 MIT；templates 非商用已确认）。实现从源码理解后**自写**；不得把 Gorden 的 docstring/注释整段粘贴；不得引入 Gorden `templates/` 或任何 .pptx 资产进 repo（验收样例在 repo 外）
3. 平台：Windows PowerShell；命令行用 `python` 而非 `python3`
4. 语言：README 中文；代码注释中文或英文均可（保持单一语言）
5. 验收用例：你自己用 python-pptx 在 `C:\Users\<you>\AppData\Local\Temp\opencode\ppt-fill-check\` 构造 3 个样张（不溢出/溢出 P1/溢出 P0+标题不一致），跑通三个脚本并截取输出存到临时目录；**验收产物不得进 repo**
6. 代码风格：函数+docstring+可复用的新函数；CLI 走 argparse；退出码：0=无 P0，2=P0

## 验收标准（自检全 Yes 才交付）

- [ ] 三脚本 + README 全部产出，路径正确
- [ ] 三个验收用例全部通过，输出符合分包格式（含 P0/P1/OK 等级）
- [ ] 无新依赖（除 python-pptx），vendor 无改动（`git status` 无 vendor 路径）
- [ ] README 写明在 template-fill-pptx.md 的哪个步骤之后运行（挂载点结论）

## 异议区（交付时附上，可选）

对以下任何决策有更好方案请写《建议》：1) 判档百分比（80/125）是否合理；2) 只有"后置检测"，要不要做"填充前预算选择"（Gorden compute_capacity 的另一个用途）；3) 标题一致性规则的定义是否足够。
