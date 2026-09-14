# PPT Skill 工作区

基于 [ppt-master 5.0.0](vendor-ppt-master/)（MIT）基座，叠加**导演式工作流**、**版式骨架资产库**、
**质检工具链**与**视觉渲染管线**的 PPT 制作系统。目标：从"我有一个主题"到"一份可交付的 .pptx"。

## 两条路线（30 秒了解）

| 路线 | 适用 | 特点 |
|---|---|---|
| **快速通道** | ≤8 页、时效紧、内容现成 | 跳过 spec/lock 与确认门，选骨架直接填充 |
| **导演式** | 重要汇报、≥10 页、需要"想清楚" | A 受众卡 → B 逐页导演稿 → **B2 视觉导演（硬门禁）** → C 映射生成 |

路线裁决规则见 `deltas/director.md` §1。

## 快速上手 5 步

1. **发起需求** —— 按六输入项说明主题/受众/页数/时长/素材/风格（模板见 `docs/USAGE.md` §8）
2. **定路线** —— 快速通道还是导演式（`docs/USAGE.md` §1）
3. **写 SVG** —— 从 `deltas/layout-assets/` 选骨架，替换 `【槽位】` 文本
4. **过质量门** —— `svg_quality_checker.py <proj> --quick-generate --stage final --json`
5. **导出并自检** —— `svg_to_pptx.py <proj> --quick-generate --no-notes`，再跑 D-2 质检与渲染

完整命令与逐步说明：**`docs/USAGE.md`**。

## 目录导航

| 路径 | 内容 |
|---|---|
| `vendor-ppt-master/` | ppt-master 5.0.0 基座（MIT，**只读不改**） |
| `deltas/director.md` · `style-lock.md` · `presenter-mode.md` | 定制层：导演工作流 / 版式锁定 / 演讲者模式 |
| `deltas/layout-assets/` | **24 个版式骨架**（v0/v1/v2 三代）+ 填写契约 |
| `deltas/pptx-fill-check/` | 质检工具：出框检测 + 标题一致性 |
| `deltas/render-preview/` | 渲染管线：pptx → PNG + contact sheet |
| `tests/test-sets/v1/` | 测试集 v1（6 个典型输入） |
| `docs/` | 使用手册、环境注意、各阶段报告 |
| `tasks/` · `docs/decisions.md` | 任务卡与裁决记录（维护者用） |

## 环境注意（详见 `docs/windows-notes.md`）

| 编号 | 一句话 |
|---|---|
| W-1 | 导出必须走四步：`init` → lock → checker → `svg_to_pptx` |
| W-2 | PowerShell 控制台中文乱码会误导判定（**看文件字节，别看屏幕**） |
| W-3 | WSL 路径不能传给 Windows python/PowerShell（用 `C:\...`） |
| W-4 | lock 脚手架是 `[fill]` 占位符，必须先填值 |
| W-5 | 手写 SVG 契约速查（bounds / 背景成组 / 单 text 多 tspan） |
| W-6 | `init` 必须带 **`--dir`**（`Set-Location` 不可靠） |
| W-7 | 填充后必须断言占位符 `【` 计数归零 |
| W-8 | 渲染产物被端点加密软件加密 → **图片处理必须走 Windows 进程** |

## 许可

- 基座 `vendor-ppt-master/`：**MIT**（Copyright (c) 2025-2026 Hugo He，原样保留）
- 本地增量（`deltas/`、`docs/`、`tests/`）：吸收自外部 skill 的部分均为**原理重写**，
  逐条登记在 `ABSORPTION-LEDGER.md`（含来源与许可处理）
