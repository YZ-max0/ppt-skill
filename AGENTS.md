# AGENTS.md

本仓库是一个 **PPT 制作 skill**。入口文件是 [`SKILL.md`](SKILL.md)。

> **请先读 `SKILL.md`**，它以 frontmatter + 加载顺序定义了完整协议。
> 本文件只是转发入口，不重复其内容。

---

## 给 agent 的最短路径

1. 读 [`SKILL.md`](SKILL.md) —— 路径纪律、强制加载顺序、路由表、执行纪律
2. 读 [`deltas/intake-guide.md`](deltas/intake-guide.md) —— **发起引导协议**（怎么问用户、怎么定路线）
3. 按 `SKILL.md` §2 的路由表，只读当前分支需要的文档
4. 无论走哪个分支，**质检都必须跑**（`SKILL.md` §4.2）

## 三条最容易踩的规则

| 规则 | 说明 |
|---|---|
| **路径纪律** | 用"包含 `SKILL.md` 的绝对目录"展开所有路径；不要 `cd`，不要假设 CWD |
| **先问一句** | 「这份 PPT：是要快，还是要尽可能做好？」（默认：尽可能好）；用场景语言，禁内部术语 |
| **质检不可省** | 四道自动闸 + 渲染目视；对已过检文件做任何改动后**必须重跑** |

## 环境

Windows + PowerShell。用 `python`（不是 `python3`）；`init` 必须带 `--dir`。
详见 `SKILL.md` §5 与 [`docs/windows-notes.md`](docs/windows-notes.md)。

## 只读目录

`vendor-ppt-master/` 是 MIT 基座，**只读，禁止修改**。新增能力写在 `deltas/`。
