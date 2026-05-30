# PRD: Hermes Harness 通用化优化

> 变更 ID: 005-harness-generalization  
> 创建日期: 2026-05-30  
> 流程级别: Quick

---

## 1. 背景

hermes-harness 是一个**通用 SDD 技能包**，但当前部分 reference 文档中捆绑了 AILP（AI Learning Platform）项目的特定场景，违反 Skill 通用性原则（R5）。同时存在孤立文件未被 SKILL.md 引用。

### 1.1 全面扫描发现的文件清单

经过逐个文件扫描，发现以下 **7 个文件**包含 AILP/003/004 特定场景引用：

| # | 文件路径 | 问题描述 | 严重程度 |
|---|----------|----------|----------|
| 1 | `sdd-orchestrator/references/pr-and-review-flow.md` | 包含"003-git-and-docs变更""本次 003 变更""SDD 003"等特定引用；且未被 SKILL.md 引用 | **CRITICAL** |
| 2 | `qa-agent/references/phase-qa.md` | 示例中使用"002-ailp-v4-refactor"作为变更 ID | MAJOR |
| 3 | `reviewer-agent/references/phase-review.md` | 示例中使用"002-ailp-v4-refactor"作为变更 ID | MAJOR |
| 4 | `shared/sdd-state-schema.md` | 多个 JSON 示例中使用"003-git-and-docs"和"002-ailp-v4-refactor" | MAJOR |
| 5 | `sdd-orchestrator/SKILL.md` | 状态文件示例中使用"002-ailp-v4-refactor" | MAJOR |
| 6 | `sdd-orchestrator/references/incremental-mode.md` | 多处使用"002-ailp-v4-refactor"作为示例，包含 AILP 特定模块名称 | MAJOR |
| 7 | `shared/git-workflow.md` | 分支命名示例中使用"003-git-and-docs"和"004-typo-in-readme" | MINOR |

### 1.2 孤立文件问题（完整扫描发现）

经过完整扫描所有 21 个 references 文件，发现 **3 个文件未被任何 SKILL.md 引用**：

| # | 文件路径 | 问题描述 | 风险等级 |
|---|----------|----------|----------|
| 1 | `qa-agent/references/phase-qa.md` | 仅被同名目录下的 `SKILL.md` 正文提及，但 frontmatter 无引用声明 | **CRITICAL** |
| 2 | `reviewer-agent/references/phase-review.md` | 仅被同名目录下的 `SKILL.md` 正文提及，但 frontmatter 无引用声明 | **CRITICAL** |
| 3 | `sdd-orchestrator/references/pr-and-review-flow.md` | 完全未被任何 `SKILL.md` 引用（孤立文件） | **CRITICAL** |

### 1.3 系统性问题：Frontmatter References 缺失

扫描发现 **全部 9 个 SKILL.md 的 frontmatter 均无 `references:` 列表**，这是导致孤立文件难以发现的根本原因。

需要修复的 SKILL.md 清单：

| # | 文件路径 | 需要添加的 references |
|---|----------|----------------------|
| 1 | `sdd-init/SKILL.md` | 待确定（该 skill 无 references 目录） |
| 2 | `sdd-orchestrator/SKILL.md` | `pr-and-review-flow.md`, `incremental-mode.md`, `sdd-workflow-activation-check.md`, `quick-flow-phase-gates.md` |
| 3 | `architect-agent/SKILL.md` | `brainstorming-guide.md`, `design-template.md`, `handoff-to-coder.md`, `tasks-template.md` |
| 4 | `ba-agent/SKILL.md` | `ac-writing-guide.md`, `spec-template.md` |
| 5 | `reviewer-agent/SKILL.md` | `review-checklist.md`, `severity-guide.md`, `phase-review.md` |
| 6 | `po-agent/SKILL.md` | `prd-template.md` |
| 7 | `sdd-structure-lint/SKILL.md` | 待确定（该 skill 无 references 目录） |
| 8 | `qa-agent/SKILL.md` | `ci-only-guide.md`, `circuit-breaker.md`, `e2e-ac-mapping-template.md`, `qa-report-template.md`, `phase-qa.md` |
| 9 | `coder-agent/SKILL.md` | `convention-checklist.md`, `nfr-checklist.md`, `task-completion-report-template.md`, `tdd-workflow.md` |

---

## 2. 目标

- [ ] 通用化 7 个 AILP 捆绑文件（移除 AILP/003/004 特定引用）
- [ ] 为全部 9 个 SKILL.md 添加 frontmatter `references:` 列表
- [ ] 确保所有 references 文件在对应 SKILL.md 中被正确声明

## 3. 非目标

- 不修改 Skill 核心逻辑
- 不删除文件，仅通用化示例和占位符
- 不新增 references 文件

## 4. 验收标准

### 4.1 AILP 通用化（AC1）

- [ ] 7 个文件中无"ailp""002-ailp""003-git-and-docs""本次 003""SDD 003"等特定引用
- [ ] 所有示例使用占位符格式（如"[你的变更ID]"）

### 4.2 Frontmatter References 完整性（AC2）

- [ ] 全部 9 个 SKILL.md 的 frontmatter 包含 `references:` 列表
- [ ] 每个 references 列表包含该 skill 目录下所有 `.md` 文件
- [ ] 孤立文件 `phase-qa.md`, `phase-review.md`, `pr-and-review-flow.md` 被正确引用
