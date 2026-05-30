# Spec: Hermes Harness 通用化优化

> 变更 ID: 005-harness-generalization  
> 创建日期: 2026-05-30  
> 对应 PRD: [prd.md](./prd.md)

---

## 功能概述

将 hermes-harness SDD 技能包中的 AILP（AI Learning Platform）项目特定引用通用化，并为全部 SKILL.md 添加 frontmatter references 声明，确保技能包符合通用框架标准。

---

## 详细需求

### 需求 1：AILP 特定引用移除

**描述**：移除 7 个文件中所有 AILP 项目特定的变更 ID、场景描述和模块名称。

**输入**：
- 包含 AILP 引用的 7 个文件（详见文件清单）
- 替换规则映射表

**输出**：
- 通用化后的文件内容
- 无 AILP 特定字符串残留

**约束**：
- 不得修改文件核心逻辑和 workflow
- 仅替换示例、占位符和场景描述
- 使用占位符格式 `[你的变更ID]`

### 需求 2：Frontmatter References 完整性

**描述**：为全部 9 个 SKILL.md 添加 frontmatter `metadata.hermes.references` 列表，引用其目录下所有 references 文件。

**输入**：
- 9 个 SKILL.md 文件
- 各 skill 目录下的 references 文件清单

**输出**：
- 更新后的 SKILL.md（包含完整 references 列表）
- 孤立文件被正确引用

**约束**：
- 保持现有 frontmatter 其他字段不变
- references 路径格式为 `references/{filename}.md`
- 列表顺序不影响功能

---

## 文件清单

### AILP 引用文件（7个）

| # | 文件路径 | 主要问题 |
|---|----------|----------|
| 1 | `sdd-orchestrator/references/pr-and-review-flow.md` | "003-git-and-docs变更""本次 003 变更" |
| 2 | `qa-agent/references/phase-qa.md` | "002-ailp-v4-refactor" |
| 3 | `reviewer-agent/references/phase-review.md` | "002-ailp-v4-refactor" |
| 4 | `shared/sdd-state-schema.md` | "003-git-and-docs""002-ailp-v4-refactor" |
| 5 | `sdd-orchestrator/SKILL.md` | "002-ailp-v4-refactor" |
| 6 | `sdd-orchestrator/references/incremental-mode.md` | "002-ailp-v4-refactor"、Phase 1-6 课程系统 |
| 7 | `shared/git-workflow.md` | "003-git-and-docs""004-typo-in-readme" |

### 需添加 References 的 SKILL.md（9个）

| # | Skill | References 数量 | 需添加的孤立文件 |
|---|-------|----------------|-----------------|
| 1 | sdd-init | 0 | 无 |
| 2 | sdd-orchestrator | 4 | pr-and-review-flow.md |
| 3 | architect-agent | 4 | 无 |
| 4 | ba-agent | 2 | 无 |
| 5 | reviewer-agent | 3 | phase-review.md |
| 6 | po-agent | 1 | 无 |
| 7 | sdd-structure-lint | 0 | 无 |
| 8 | qa-agent | 5 | phase-qa.md |
| 9 | coder-agent | 4 | 无 |

---

## Acceptance Criteria（验收标准）

| 编号 | 场景 | Given | When | Then |
|:---:|------|-------|------|------|
| AC1 | AILP 字符串移除验证 | 7 个目标文件已完成通用化替换 | 执行 `grep -r "ailp\|002-ailp\|003-git-and-docs\|本次 003\|SDD 003" skills/sdd/` | 命令返回空结果（无匹配） |
| AC2 | 占位符格式验证 | 检查替换后的文件内容 | 搜索变更 ID 示例 | 所有示例使用 `[你的变更ID]` 或 `[变更ID]` 格式 |
| AC3 | sdd-orchestrator references | sdd-orchestrator/SKILL.md 已更新 | 检查 frontmatter | `metadata.hermes.references` 包含 `pr-and-review-flow.md` |
| AC4 | qa-agent references | qa-agent/SKILL.md 已更新 | 检查 frontmatter | `metadata.hermes.references` 包含 `phase-qa.md` |
| AC5 | reviewer-agent references | reviewer-agent/SKILL.md 已更新 | 检查 frontmatter | `metadata.hermes.references` 包含 `phase-review.md` |
| AC6 | 全部 SKILL.md references | 所有 SKILL.md 已更新 | 执行验证脚本检查 frontmatter | 9 个 SKILL.md 均有非空 `metadata.hermes.references` 列表 |
| AC7 | 向后兼容 | 完成所有修改 | 对比修改前后 SKILL.md 核心逻辑 | Workflow 描述、规则检查、阶段定义均无变化 |
| AC8 | 无文件删除 | 完成所有修改 | 检查文件列表 | 原 21 个 references 文件均存在，无删除 |

---

## 替换规则映射

| 原字符串 | 替换为 | 适用文件 |
|----------|--------|----------|
| `002-ailp-v4-refactor` | `[你的变更ID]` | 所有 |
| `003-git-and-docs` | `[你的变更ID]` | 所有 |
| `004-typo-in-readme` | `[你的变更ID]` | 所有 |
| `本次 003` | `本次 [变更ID]` | pr-and-review-flow.md |
| `SDD 003` | `SDD [变更ID]` | pr-and-review-flow.md |
| `003-git-and-docs变更` | `[变更ID]变更` | pr-and-review-flow.md |
| `Phase 1-6 课程系统` | `多阶段课程系统` | incremental-mode.md |
| `用户登录功能` | `用户认证功能` | incremental-mode.md（如存在） |

---

## 非功能需求细化

| 类别 | 原始 NFR | 细化指标 | 验证方式 |
|------|---------|---------|---------|
| 一致性 | 所有示例使用统一占位符格式 | 100% 的变更 ID 示例使用 `[你的变更ID]` | grep 检查 |
| 完整性 | 无孤立 references 文件 | 21 个 references 文件均被 SKILL.md 引用 | 脚本验证 frontmatter |
| 向后兼容 | 不破坏现有功能 | SKILL.md 核心逻辑零变更 | diff 对比 |

---

## 前置条件

- [x] PRD 已确认
- [ ] **用户确认 Spec（当前）**

## 后置条件

- [x] spec.md 已创建
- [ ] 用户确认 Spec
- [ ] 可进入 Phase 3 (Architect)
