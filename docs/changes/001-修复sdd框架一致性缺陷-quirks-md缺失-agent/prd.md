# PRD — SDD 框架全量一致性修复（D1-D9）

> **Product Requirements Document**
> Change ID: `001-修复sdd框架一致性缺陷-quirks-md缺失-agent`
> 版本：2.0（扩展） | 状态：Draft

---

## 1. 背景与目标

### 1.1 问题陈述

SDD 框架经历多个迭代（001-sdd-init → 008-profile-delegation → Profile+Soul 架构落地），积累了 4 个一致性缺陷：

| # | 缺陷 | 现象 | 根因 |
|---|------|------|------|
| **D1** | QUIRKS.md 缺失 | AGENTS.md 项目约束声明 quirks: QUIRKS.md，但根目录不存在该文件 | 001-sdd-init 阶段生成后未持续维护 |
| **D2** | AGENTS.md 版本与模型映射不一致 | Profile 矩阵注释仍引用旧模型 doubao/glm-5.1，实际运行时使用 deepseek | AGENTS.md 在 Profile+Soul 架构落地时未同步 |
| **D3** | AGENTS.md 包含冗余文档内容 | AGENTS.md 包含 Profile 架构概述、Soul 配置、Workspace 规范等 ~120 行文档内容 | 历史原因：文档写入了 AGENTS.md，未按设计分离 |
| **D4** | 归档不完整 | 版本标记 2.3.0，但 archive 最新归档为 008-profile-delegation | Profile+Soul 架构落地后未正式归档 |
| **D5** | 源码 SKILL.md 完全基于 delegate_task | 源码 skills/sdd/sdd-orchestrator/SKILL.md 仍是 v2.1.0，12 处 delegate_task 引用，0 次 kanban 引用 | 修复只打在 installed skill，未同步回 repo |
| **D6** | orchestrator.py 与 SKILL.md 完全脱节 | orchestrator.py 已用 Kanban create，但 SKILL.md 描述仍说 delegate_task | 代码和文档在两个版本线上演进 |
| **D7** | 8 个参考文件缺失 | 源码缺少 kanban-profile-integration.md、profile-soul-architecture.md、4-layer-document-consistency.md 等 | 文件只存在于 installed skill，未提交到 repo |
| **D8** | 6 个参考文件仍引用 delegate_task | delegate-protocol.md（10处）、state-machine.md（11处）、incremental-mode.md、interrupt-recovery.md、skill-maintenance-pattern.md、pr-and-review-flow.md | 基于旧 v2.1.0 架构编写，未随委托机制切换更新 |
| **D9** | Kanban+Profile 子 Agent 上下文丢失 | 当前 task body 只有 change_id + 路径，BA 不知 PO 决策依据，Architect 不知 Spec trade-off | 没有跨阶段上下文传播机制 |
| **D10** | 所有 Profile 配置的 DeepSeek API Key 已过期 | 6 个 sdd-* Profile 均用 `api_key: sk-982...66fc` 发往 `api.deepseek.com`，全部 401 | Profile 创建时使用的 DeepSeek Key 已过期；主配置和工作 Profile 使用不同的 Provider |


### 1.2 目标

修复 SDD 框架的 **9 项一致性缺陷**（D1-D9），核心目标是：让源码 repo 的 `install.sh` 安装出来的就是正确的 Kanban+Profile 版本，确保子 Agent 上下文不丢失。

**量化目标**：
- AGENTS.md 声明的所有文件（CONSTITUTION.md、QUIRKS.md）100% 存在于项目根目录
- AGENTS.md 移除纯文档内容（Profile 架构、Soul 配置、Workspace 规范），缩减行数 >= 50%
- AGENTS.md 中所有模型引用与实际 Profile 配置一致
- 源码 skills/sdd/sdd-orchestrator/SKILL.md 升级至 v2.6.0，零 delegate_task 引用
- 8 个缺失参考文件补全到 repo
- 6 个旧参考文件的 delegate_task 引用全部替换为 Kanban+Profile
- orchestrator task body 包含跨阶段上下文（前置产物的核心决策、关键摘要、约束条件）
- docs/archive/ 新增 Profile+Soul 架构落地的正式归档
- 移除 setup-sdd-profiles.sh.deprecated

---

## 2. 用户场景

### 场景 1：SDD 流程执行时遭遇文件缺失

- **角色**：SDD Orchestrator（流程编排器）
- **前置条件**：变更执行到 L1 门禁检查阶段，`sdd-structure-lint` 被调起
- **操作流程**：
  1. Orchestrator 当前变更进入 L1 门禁
  2. `sdd-structure-lint` 读取项目约束：检查 `AGENTS.md` 声明的所有文件存在
  3. Lint 检查发现存在 `CONSTITUTION.md` 但**不存在** `QUIRKS.md`
  4. Lint 抛出 MAJOR 级别错误，阻塞阶段推进
- **期望结果**：`QUIRKS.md` 存在且内容合规，L1 门禁无阻塞通过

### 场景 2：开发者查阅 AGENTS.md 时发现混乱

- **角色**：SDD 框架维护者（阅读并维护 AGENTS.md）
- **前置条件**：需要理解 SDD 框架的 Profile 映射配置
- **操作流程**：
  1. 维护者打开 AGENTS.md 查看 Profile 映射
  2. 发现 Profile 矩阵注释中引用 `doubao-seed-2.0-pro`，但实际 Profiles 使用 `deepseek-v4-flash`
  3. 发现 AGENTS.md 后半部分包含大量"Profile 架构概述""Soul 模式配置"等文档，而非项目配置
  4. 维护者困惑：这些内容该在 AGENTS.md 还是 docs/current/ 中？
- **期望结果**：AGENTS.md 是**纯配置文件**，无冗余文档内容；所有引用与实际配置一致；Profile+Soul 架构文档在 `docs/current/` 中

### 场景 3：归档健全性检查

- **角色**：SDD Orchestrator（归档阶段） / SDD 框架维护者
- **前置条件**：完整归档检查（R10：归档检查）
- **操作流程**：
  1. R10 门禁检查归档目录完整性
  2. 对比当前 `docs/current/README.md` 中的变更历史与实际 `docs/archive/` 目录
  3. 发现当前基线中的变更条目多于归档目录（Profile+Soul 缺失）
- **期望结果**：`docs/archive/` 包含所有已完成的变更，变更历史与归档目录一致

---

## 3. 功能范围

### In Scope（本次包含）

| 模块 | 变更 | 
|------|------|
| **D1 — QUIRKS.md 创建** | 基于 `templates/QUIRKS.md` 和 `skills/sdd/sdd-init/templates/quirks-template.md`，在项目根目录创建 QUIRKS.md，填充已知的环境怪癖和工具链注意事项 |
| **D2 — AGENTS.md 清理** | 修复 Profile 矩阵中过时的模型注释，确保与实际 Profile 配置（deepseek-v4-flash/deepseek-v4-pro）一致 |
| **D3 — AGENTS.md 精简** | 将 AGENTS.md 中的 Profile 架构概述、Soul 模式配置、Workspace 配置规范等文档内容迁移至 `docs/current/architecture.md`，AGENTS.md 回归纯配置定位 |
| **D4 — 归档补充** | 新增 `docs/archive/001-profile-soul-架构落地与机制验证/` 目录（含 prd.md、spec.md、design.md、tasks.md） |
| **状态更新** | 新增 `.sdd-state.json` 的 `phase_status` 字段，标记当前变更的 Phase 状态 |
| **存量修复** | 修复 `skwrap` 相关错误（修复 `skills/sdd/sdd-orchestrator/SKILL.md` 中的 `skill_vie w` → `skill_view` 拼写错误等） |

### Out of Scope（本次不包含）

- SDD 流程本身的修改（Orchestrator 逻辑、门禁规则）
- Profile 模型配置变更（不修改任何 Profile 的 config.yaml 或 SOUL.md）
- AGENTS.md 中其他章节的重写（仅做注释修复和文档内容移除，不做结构重构）
- 历史归档内容的回溯性修改（仅补充 Profile+Soul 的归档）
- 非 Hermes Harness 项目的 QUIRKS.md 模板更新

---

## 4. 非功能需求（NFR）

| 类别 | 要求 | 指标 |
|------|------|------|
| **一致性** | AGENTS.md 声明的约束文件 100% 存在于预期路径 | L1 门禁 0 阻塞 |
| **可维护性** | AGENTS.md 移除文档内容后行数缩减 | ≤80 行（当前 174 行 → 目标 ≤80 行） |
| **可追溯性** | 归档覆盖所有已完成变更 | docs/archive/ 子目录数量 ≥ docs/current/README.md 变更历史条目数 |
| **兼容性** | 不破坏现有 SDD 流程 | 变更完成后执行 `sdd-structure-lint L1` 无新增错误 |

---

## 5. 验收标准（高层级）

1. **QUIRKS.md 文件创建**：项目根目录存在 QUIRKS.md，内容基于模板但针对 Hermes Harness 项目填充了已知陷阱、环境怪癖和工具链注意事项
2. **AGENTS.md 模型映射纠正**：Profile 矩阵注释中的模型名称与实际 Profile 配置一致（`deepseek-v4-flash`/`deepseek-v4-pro`）
3. **AGENTS.md 文档移除**：不再包含 "Profile 架构概述"、"Soul 模式配置"、"Workspace 配置规范" 等文档章节；这些内容已在 `docs/current/architecture.md` 中
4. **AGENTS.md 行数达标**：总行数 ≤ 80 行（从 174 行缩减）
5. **归档补充完成**：`docs/archive/001-profile-soul-架构落地与机制验证/` 目录存在，包含 prd.md、spec.md、design.md、tasks.md
6. **L1 门禁通过**：`sdd-structure-lint` 执行后 L1 检查无 MAJOR/CRITICAL 错误
7. **AGENTS.md 约束声明有效**：`quirks: "QUIRKS.md"` 指向实际存在的文件

---

## 6. 风险与假设

### 风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|:---:|------|
| 迁移 AGENTS.md 文档内容到 architecture.md 后，Agent 在加载 AGENTS.md 时不再能看到 Profile+Soul 架构描述 | Agent 缺少框架理解上下文 | 中 | 架构文档迁移到 `docs/current/architecture.md` 后，Agent 依然可以通过 `read_file` 访问；Orchestrator 可自行读取 |
| QUIRKS.md 创建后长期无人维护，变成空壳 | 无实际价值 | 高 | 在变更中先填充已知内容（环境怪癖、工具链），并约定后续开发者发现新陷阱时追加 |
| 移除 AGENTS.md 文档内容影响 Kanban Worker 的预加载上下文 | Worker 加载 AGENTS.md 后丢失架构信息 | 低 | AGENTS.md 中的架构内容原本就不属于标准 SDD 配置字段，本次清理是回到设计初衷 |
| 归档补充时找不到 Profile+Soul 架构落地的完整产物 | 归档不完整 | 低 | 从现有 `docs/current/` 中的 design.md、prd.md 提取核心内容即可 |

### 假设

- 项目根目录已存在 `templates/QUIRKS.md` 模板文件
- Profile+Soul 架构落地的设计决策记录可以从 `docs/current/design.md` 中的 "归档来源" 行推断
- AGENTS.md 的缩减不破坏任何现有 Hermes Agent 的解析逻辑（Hermes Agent 使用 AGENTS.md 的 YAML-style fields，忽略之后的标题 Markdown 内容）

---

## 版本更新记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0 | 2026-06-16 | 初始版本：4 项一致性缺陷范围界定 |

