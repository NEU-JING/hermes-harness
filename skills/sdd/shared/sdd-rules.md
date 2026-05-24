# SDD 通用规则定义

> 版本：V1.0
> 本文档定义 SDD 流程中编排器和各角色 Agent 必须遵守的 10 条通用规则。
> 项目可通过 AGENTS.md 的 `convention_overrides.disable_rules` 禁用部分规则（R3/R6/R8 不可禁用）。

---

### R1: 没有 Spec 不写代码

- **描述**：新功能必须先产出 Spec（Quick 流程除外），无 Spec 不可进入 Implement 阶段
- **触发时机**：编排器在 Implement 阶段启动前
- **执行者**：sdd-orchestrator
- **检查方式**：sdd-structure-lint 交接级检查 — spec.md 是否存在
- **违反处理**：阻断流程，输出 `"无法进入 Implement：spec.md 不存在。请先完成 Spec 阶段。"`
- **Quick 豁免**：✓（Quick 跳过 Spec 阶段）

---

### R2: 编码前 Brainstorming

- **描述**：Standard/Enhanced 流程的 Design 阶段必须执行 Brainstorming（≥2 方案对比）
- **触发时机**：architect-agent 在 Design 阶段启动时
- **执行者**：architect-agent
- **检查方式**：自检 — design.md 中是否包含方案 A、方案 B 两个章节
- **违反处理**：architect-agent 自动返回 Step 2 补充方案对比
- **Quick 豁免**：✓（Quick 跳过 Design 阶段）

---

### R3: TDD 强制

- **描述**：代码实现必须先写测试（RED），后写实现（GREEN），最后重构（REFACTOR）
- **触发时机**：coder-agent 每个 Task 执行时
- **执行者**：coder-agent
- **检查方式**：自检 — 运行测试必须先是 RED（失败），然后 GREEN（通过）
- **违反处理**：coder-agent 退回 Step 1，不允许跳过测试
- **Quick 豁免**：✗（Quick 也必须 TDD）
- **可禁用**：✗（不可禁用，核心原则）

---

### R4: 编码后必须评审

- **描述**：Implement 完成后必须经 Reviewer Agent 三阶段评审
- **触发时机**：编排器在 Implement 阶段后
- **执行者**：sdd-orchestrator → reviewer-agent
- **检查方式**：review-report.md 是否存在且结论为 "通过" 或 "有条件通过"
- **违反处理**：阻断流程，输出 `"无法进入 QA：评审未完成。"`
- **Quick 豁免**：✓（Quick 跳过 Review 阶段）

---

### R5: 前后端契约同步

- **描述**：后端 Schema 字段名必须与前端消费字段名一致；修改 Schema 需同步更新前端引用
- **触发时机**：reviewer-agent Phase 2 审查
- **执行者**：reviewer-agent
- **检查方式**：检查 diff 中 Schema 变更是否伴随前端对应字段更新
- **违反处理**：标记为 CRITICAL，返回 coder-agent 修复
- **项目豁免**：无前端项目在 AGENTS.md 中声明 `disable_rules: ["R5"]`

---

### R6: 测试自包含原则

- **描述**：所有测试必须在全新环境中独立运行（在各自声明的目标环境中），不依赖预置数据
- **触发时机**：QA Agent AC 覆盖验证时
- **执行者**：qa-agent
- **检查方式**：检查测试是否能在 CI 新环境中通过。CI-only 标记的测试仅需在 CI 中通过；本地可运行的测试需在本地也通过（见 R9）
- **违反处理**：标记为环境依赖，在 qa-report.md 的环境差异中记录
- **可禁用**：✗（不可禁用，核心原则）

---

### R7: E2E-AC 一一对应

- **描述**：每个 E2E 用例必须标注对应的 AC 编号；QA 阶段验证完整覆盖
- **触发时机**：QA Agent AC 覆盖验证
- **执行者**：qa-agent
- **检查方式**：提取 spec.md 所有 AC 编号，在 E2E 文件中搜索引用，生成覆盖矩阵
- **违反处理**：缺失覆盖的 AC 标记为失败，QA 报告结论为 "不通过"

---

### R8: Push 前必过 Pre-commit

- **描述**：代码 push 到远程前必须通过本地 pre-commit 检查（format + lint）
- **触发时机**：git push 时（由 pre-commit hook 自动触发）
- **执行者**：pre-commit hook
- **检查方式**：black --check + isort --check-only + ruff check（仅变更文件）
- **违反处理**：push 被阻断，输出具体失败项
- **配置**：由 sdd-init 生成 `.pre-commit-config.yaml`
- **可禁用**：✗（不可禁用，核心原则）

---

### R9: 目标环境通过原则

- **描述**：测试必须在声明的目标环境中通过，不强制所有测试本地+CI 双通。
  - 本地可运行的测试：需在本地和 CI 双环境通过
  - 需要 CI 资源（Docker/GPU/大内存/长超时）的复杂测试：标记为 CI-only，仅需 CI 通过
- **触发时机**：QA Agent 环境差异标记
- **执行者**：qa-agent
- **检查方式**：
  1. 搜索测试文件中的 CI-only 标记（pytest skipif/skip 或自定义 marker），记录跳过原因
  2. 非 CI-only 的测试在本地也需执行并通过
- **违反处理**：
  1. CI-only 测试未标记 → 标记为 REQ，要求补充标记及原因注释
  2. 非 CI-only 测试本地未通过 → 标记为 FAIL
- **配置**：sdd-init 生成 pytest.ini 时自动注册 ci_only marker，本地默认 skip

---

### R10: PR 不直接 push main

- **描述**：涉及 `.github/workflows/` 或新增功能的变更，必须走 PR 流程
- **触发时机**：编排器归档前
- **执行者**：sdd-orchestrator
- **检查方式**：检查变更是否包含 `.github/workflows/` 文件变更
- **违反处理**：输出 `"此变更涉及 CI 配置，请通过 PR 提交。"`

---

## 规则总览

| 编号 | 名称 | 执行者 | Quick 豁免 | 可禁用 |
|:---:|------|------|:---:|:---:|
| R1 | 没有 Spec 不写代码 | sdd-orchestrator | ✓ | ✓ |
| R2 | 编码前 Brainstorming | architect-agent | ✓ | ✓ |
| R3 | TDD 强制 | coder-agent | ✗ | ✗ |
| R4 | 编码后必须评审 | sdd-orchestrator | ✓ | ✓ |
| R5 | 前后端契约同步 | reviewer-agent | ✓ | ✓ |
| R6 | 测试自包含原则 | qa-agent | ✗ | ✗ |
| R7 | E2E-AC 一一对应 | qa-agent | ✓ | ✓ |
| R8 | Push 前必过 Pre-commit | pre-commit hook | ✗ | ✗ |
| R9 | 目标环境通过原则 | qa-agent | ✗ | ✓ |
| R10 | PR 不直接 push main | sdd-orchestrator | ✓ | ✓ |
