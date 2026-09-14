# 任务卡 T-E2E1 · M1 端到端首跑（测试集 T-01 · 快速通道）（P1 · 预计 2-3 小时）

指挥官：opencode ｜ 执行者：同一执行者 ｜ 版本：v1.0 ｜ 前置：M0 已关闭

## 目标

用测试集 **T-01 原文**（不得改编）真实跑一次完整链路，首次面对"生成质量"而非"环境问题"：

```
Director 轻量版 → base Quick 通道 → SVG 手写 → 导出 PPTX → D-2 质检 → 读回验证
```

这是 M1 首跑：**验证链路 join 点 + 建立快速通道耗时基线**。视觉精美度本轮不评（那是 M2/L3 的事），但结构、无 P0、无乱码必须达标。

## 输入（只读）

| 材料 | 路径 | 用途 |
|---|---|---|
| T-01 测试输入 | `tests/test-sets/v1/inputs.md`（找 T-01 节） | 唯一需求源，原样执行 |
| Director 轻量公式 | `deltas/director.md` §7 | 快速通道的导演步骤 |
| Quick 执行权威 | `vendor-ppt-master/workflows/profiles/quick-generate.md` | **按它走**（Quick 是 lockless、跳过 spec/lock/Confirm） |
| SVG 规范 | `vendor-ppt-master/references/semantic-svg.md` + `scripts/docs/svg-pipeline.md` | 手写 SVG 的必守契约（`data-pptx-page-role` 等） |
| 环境绕行 | `docs/windows-notes.md` | W-1~W-4（导出序列/编码/路径/lock） |
| D-2 工具 | `deltas/pptx-fill-check/detect_overflow.py` + `check_title_consistency.py` | 后置质检 |

## 执行步骤（记录每步：命令原样 / 退出码 / 耗时 / 产物 / 观察）

1. **Director 轻量**（§7）：受众 3 句 → 逐页导演稿（观点标题 + ≤3 要点 + 页型）。
   入卡附录（报告里全文收录）。T-01 无素材 → 允许自拟合理内容，但必须满足 T-01 的四事项/两风险要求。
2. **项目初始化 + 手写 SVG**：6-8 页（含封面），16:9；按 quick-generate.md 的 lockless 路径执行。
3. **导出 PPTX**：按 quick 的导出/检查路径（遇额外门禁按 W-1/W-4 处理，记录实际踩线）。
4. **D-2 质检**：`detect_overflow.py` + `check_title_consistency.py`（默认参数）。
5. **读回验证**：递归遍历 GROUP 的文本帧、页数、中文无乱码（`\ufffd`=0）、UTF-8 文件回读（P-3，不看控制台）。
6. **失败模式编号**：任何卡点按 CONTRACT 规则编 `C-XXX` 并写入报告。

## 交付物

`docs/e2e-01-report.md`（唯一 repo 新增），结构：
1. 命令序列（原样 + 退出码 + 耗时）
2. Director 轻量稿全文（附录）
3. 产物清单（临时目录路径 + 页数/文本帧数/质检结果）
4. T-01 验收对照：快速通道可达 ✅？无溢出（P0=0）？无乱码 ✅？
5. 失败模式清单（C-XXX 编号 + 现象 + 处理）
6. 耗时基线（各阶段分钟数；这是"快速出稿"契约的首次数据点）
7. 未验证项（视觉渲染等）
8. 《建议》附录

## 硬约束

1. T-01 文本原样，不得偷换需求；页数 6-8 不得缩水
2. vendor 零修改；产物全部进临时目录 `C:\Users\<you>\AppData\Local\Temp\opencode\ppt-e2e\`；repo 仅报告
3. Windows 侧 python；中文验证走 UTF-8 文件回读
4. 只记录不修复（发现 vendor/D-2 问题 → 报告 + C-XXX，修复走后续卡）

## 验收标准

- [ ] 6-8 页 deck 产出且可打开；D-2 两脚本运行完毕
- [ ] 无 P0 假/真溢出（P0 若 >0 必须逐项说明真伪）
- [ ] 读回验证：页数/文本帧/乱码 0
- [ ] 报告八段完整；耗时基线有数据
- [ ] vendor 零 diff；git status 仅报告一处新增

## 异议区

如 quick-generate.md 的实际流程与本卡假设（lockless 短路）不符，以权威文档为准执行并在报告说明差异。
