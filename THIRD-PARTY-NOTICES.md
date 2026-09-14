# Third-Party Notices

本仓库包含或吸收了下列第三方作品的成果。逐条列明来源与许可处理方式。
完整审计凭证（每条吸收的改写方式、落盘文件、许可依据）见 [`ABSORPTION-LEDGER.md`](ABSORPTION-LEDGER.md)。

---

## 1. 内置基座（原样保留）

### ppt-master 5.0.0

- **位置**：`vendor-ppt-master/`（**原样保留**，除本仓库登记的 3 处最小改动外未修改）
- **许可**：MIT
- **版权**：Copyright (c) 2025-2026 Hugo He
- **来源**：https://github.com/hugohe3/ppt-master
- **本仓库对其的登记改动**（3 处，均为最小挂载）：
  1. `workflows/routing.md` 末尾追加 §8 Director Pre-spec Input Stage
  2. `workflows/index.md` §2 追加 director 一行登记
  3. 未引入 `.env`（仅保留上游 `.env.example`）

---

## 2. 吸收致谢（原理级借鉴）

以下作品的**思路**被本仓库吸收，用于 `deltas/` 下的定制层。
**改写方式**说明本仓库如何使用其成果（`原理重写` = 只吸收设计原理，不复制任何文本或代码）。

| 来源作品 | 许可 | 吸收方式 | 落点 |
|---|---|---|---|
| **ppt-director** | 无 LICENSE（默认保留版权） | **原理重写**（阶段划分、交付文档结构、页面导演稿字段） | `deltas/director.md`、`references/registry` 设计 |
| **guizang-ppt-skill**（op7418） | **AGPL-3.0** | **原理重写**（P0-P3 检查分级、版式锁定哲学、演讲者契约） | `deltas/style-lock.md`、`deltas/presenter-mode.md` |
| **dashi-ppt** | 无 LICENSE（内部包 MIT） | **原理重写**（schema 设计理念、内容/视觉分离） | `schemas/` 设计依据 |
| **GordenPPTSkill** | MIT（源码）；`templates/` 非商用 | **改写**（读源码自写容量计算与出框判据）；**模板目录零接触** | `deltas/pptx-fill-check/` |
| **html-ppt** | MIT | **改写**（演讲者模式：逐字稿 3 规则） | `deltas/presenter-mode.md` |
| **frontend-slides**（Zara Zhang） | MIT | **改写**（固定舞台规则、内容密度模式） | 设计参考 |
| **beautiful-html-templates**（Zara Zhang） | MIT | **仅学结构**（模板包索引组织方式） | 设计参考 |
| **ppt-master** | MIT | **基座**（见上节） | `vendor-ppt-master/` |

### 关于 AGPL 与无许可来源的合规声明

`guizang-ppt-skill`（AGPL-3.0）与 `ppt-director`、`dashi-ppt`（无 LICENSE）三类来源，
本仓库**一律按"原理重写"处理**：

- **不复制**其任何源代码、文本、表格结构或资产文件
- 只吸收可独立表述的**设计原理**（如"检查项应分级"、"版式应先登记后使用"）
- 逐条记录在 `ABSORPTION-LEDGER.md`，并标注"按原理重写"

**GordenPPTSkill 的 `templates/` 目录**（非商用许可）**零接触**：本仓库未引入其任何模板资产。

---

## 3. 资产许可

本仓库**不包含**第三方字体、图标、图片或模板资产。
版式骨架（`deltas/layout-assets/`）为纯 SVG 几何与文本，由本仓库自行编写。

---

## 4. 顶层许可

本仓库自身（除上述第三方部分外）采用 **MIT**，见 [`LICENSE`](LICENSE)。

> ⚠️ 使用前请注意：`vendor-ppt-master/` 遵循其自身的 MIT 条款（Copyright (c) 2025-2026 Hugo He），
> 上述"吸收致谢"中标注为 **AGPL-3.0 / 无许可** 的来源仅作为**设计参考**，
> 其原始作品的使用需另行遵守其各自条款。
