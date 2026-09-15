# PPT Skill 工作区

**这是什么**：一套用 AI 把"一个主题"变成"一份可交付 PPT"的工作区。
它不生成花哨的模板，而是帮你把内容先想清楚（谁听、讲什么、每页要证明什么），再落到 29 个
已验证合规的版式骨架上，最后通过质量门与视觉自检交付原生 `.pptx`。
**你只需要说一句话**——"要快还是要尽可能做好"由引导协议接管。

**解决什么问题**：汇报 PPT 的两个老问题——"内容没想清楚就排版"和"排完了没人验证效果"。
本工作区把前者固化为可执行的导演流程，把后者固化为可脚本化的质检与渲染管线。

基于 [ppt-master 5.0.0](vendor-ppt-master/)（MIT）基座，叠加导演工作流、版式骨架资产库、
质检工具链与视觉渲染管线。

> 🤖 **给 AI agent**：入口是 [`SKILL.md`](SKILL.md)（含路径纪律、加载顺序、路由表、执行纪律）。
> 按 `AGENTS.md` 约定发现的 agent 会被转发到同一入口。

## 两条路线（30 秒了解）

| 路线 | 适用 | 特点 |
|---|---|---|
| **快速通道** | ≤8 页、时效紧、内容现成 | 跳过 spec/lock 与确认门，选骨架直接填充 |
| **导演式** | 重要汇报、≥10 页、需要"想清楚" | A 受众卡 → B 逐页导演稿 → **B2 视觉导演（硬门禁）** → C 映射生成 |

> 💡 **不知道该选哪条？不用自己选。** 说一句"要做什么"就行，
> 执行者会问一句"要快还是要尽可能做好"，再按
> [`deltas/intake-guide.md`](deltas/intake-guide.md) 的引导协议自动定路线。
> 默认按**"尽可能做好"**执行。

按**质量需求**选流程（三档 + 耗时对照 + 校验门）→ **`docs/QUALITY-TIERS.md`**

路线裁决规则见 `deltas/director.md` §1。

## 快速上手 5 步

1. **发一句话就够** —— 例如"下周要给分管领导汇报平台建设方案"。
   执行者会先问你"要快，还是要尽可能做好？"，然后按引导协议推进
   （协议见 [`deltas/intake-guide.md`](deltas/intake-guide.md)）。
   需要一次把信息给全时，用**精确模式模板**：`docs/USAGE.md` §8.2
2. **定路线** —— 快速通道还是导演式（`docs/USAGE.md` §1）
3. **写 SVG** —— 从 `deltas/layout-assets/` 选骨架，替换 `【槽位】` 文本
4. **过质量门** —— `svg_quality_checker.py <proj> --quick-generate --stage final --json`
5. **导出并自检** —— `svg_to_pptx.py <proj> --quick-generate --no-notes`，再跑 D-2 质检与渲染

完整命令与逐步说明：**`docs/USAGE.md`**。

## 目录导航

| 路径 | 内容 |
|---|---|
| `SKILL.md` · `AGENTS.md` | **AI agent 入口**（路径纪律 / 加载顺序 / 路由 / 纪律） |
| `vendor-ppt-master/` | ppt-master 5.0.0 基座（MIT，**只读不改**） |
| `deltas/intake-guide.md` | **发起引导协议**（二分入口 / 质量协议 / 4 原则 / 2 示例对话） |
| `deltas/director.md` · `style-lock.md` · `presenter-mode.md` | 定制层：导演工作流 / 版式锁定 / 演讲者模式 |
| `deltas/chart-fill/` · `table-fill/` | 图表 / 表格生成器（含 v2 图表坐标重算） |
| `deltas/layout-assets/` | **29 个版式骨架**（v0/v1/v2/v3 四代）+ 填写契约 + 卫生/重叠检查器 |
| `deltas/pptx-fill-check/` | 质检工具：出框检测 + 标题一致性 |
| `deltas/render-preview/` | 渲染管线：pptx → PNG + contact sheet |
| `tests/test-sets/v1/` | 测试集 v1（6 个典型输入） |
| `docs/QUALITY-TIERS.md` | **质量档位选择**（快速/标准/导演式，含校验门与耗时） |
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

- **本仓库**：MIT，见 [`LICENSE`](LICENSE)（版权名待填入）
- **基座** [`vendor-ppt-master/`](vendor-ppt-master/)：MIT，Copyright (c) 2025-2026 Hugo He，
  来源 [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)，**原样保留**
- **第三方致谢与吸收声明**：见 [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md)
  （8 个来源的名称 / 许可 / 吸收方式）
- **吸收审计凭证**：逐条来源、改写方式与许可处理见 [`ABSORPTION-LEDGER.md`](ABSORPTION-LEDGER.md)
