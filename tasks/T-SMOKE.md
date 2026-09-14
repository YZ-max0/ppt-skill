# 任务卡 T-SMOKE · M0 集成冒烟（P1 · 预计 1-2 小时）

指挥官：opencode ｜ 执行者：同一执行者 ｜ 版本：v1.0 ｜ 前置：T-D3D4 已关闭、探针全过

## 目标

在 Windows 侧跑通 vendor 的**确定性代码链路**（不涉及 AI 生成质量），暴露环境级问题。
这是 M0 的收尾验收：证明"生成层可执行"，为 M1 端到端测试清雷。

## 冒烟范围（四个代码路径，逐条执行）

### S1 · SVG → PPTX 导出链路
- 输入：自写一个最小 SVG（1-2 页，16:9，含标题+正文文本+一个矩形图形；或使用 `vendor-ppt-master/templates/tables/*.svg` 做输入参考）
- 命令：先用 `python vendor-ppt-master/scripts/svg_to_pptx.py --help` 查明用法（文档可能在 `scripts/docs/` 下），然后按正确用法转换到临时目录
- 验收：产出可打开的 .pptx；用 python-pptx 读回页数与文本，确认无乱码

### S2 · 备注链路
- 输入：按 `executor-notes` 契约写一个最小 `notes/total.md`（2 页，`# 1_封面` 风格分页，纯文本）
- 命令：`total_md_split.py` 拆分 → 检查拆出的分页文件；如链路允许，继续验证 `svg_to_pptx.py` 的备注写入（或手工核对 CLI 参数存在）
- 验收：拆分产物与页序一一对应，文本编码正确（中文）

### S3 · 质量链路（D-2 对接）
- 用 S1 的产物跑 `deltas/pptx-fill-check/detect_overflow.py` 与 `check_title_consistency.py`
- 验收：检测器在真实 vendor 产物上不崩溃、输出合理分级

### S4 · 批量校验链路
- 对临时项目目录跑 `python vendor-ppt-master/scripts/batch_validate.py <dir>`（空目录亦可）
- 验收：CLI 可执行、输出摘要格式符合预期、无未捕获异常

## 硬约束

1. **vendor 零修改**：一切问题只记录、不修复（修复走后续卡）
2. 临时产物全部放 `C:\Users\<you>\AppData\Local\Temp\opencode\ppt-smoke\`；repo 内不新增 .pptx/SVG 产物
3. 除交付报告外不改 repo 任何文件（报告写成 `docs/smoke-report.md`，唯一 repo 内新增）
4. Windows 侧 python（`python`），git 只用 Windows git

## 交付要求

1. **冒烟报告 `docs/smoke-report.md`**：
   - 每个 S1-S4：命令（原样）、退出码、产物清单、观察结果
   - 「环境问题清单」：按严重度分级（阻断/需绕行/提示）+ 命令级复现步骤
   - 「未验证项」：因缺依赖/权限而未跑通的路径及原因
2. 《建议》附录：对冒烟范围/后续 M1 测试的改进建议
3. 红线自检：vendor 零 diff、临时产物零进 repo、报告为唯一新增

## 验收标准

- [ ] S1-S4 全部执行（未跑通的必须有明确原因与复现命令）
- [ ] 报告结构完整（四段 + 问题清单 + 未验证项）
- [ ] `git status` 差异仅 `docs/smoke-report.md`（在 T-D3D4 两个文件提交之后执行）
