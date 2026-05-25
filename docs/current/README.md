# Hermes Harness — 项目基线

> 最后更新：2026-05-25
> 当前版本：参考 `main` 分支最新 commit
> 本文档由 SDD 归档流程自动维护（sdd-orchestrator Phase 8.1）

---

## 项目状态

- **SDD 流程**：Standard（8 阶段：PO → BA → Architect → Coder → Reviewer → QA → 验收 → 归档）
- **角色 Skill**：8 个（po-agent, ba-agent, architect-agent, coder-agent, reviewer-agent, qa-agent, sdd-orchestrator, sdd-init）
- **辅助 Skill**：1 个（sdd-structure-lint）
- **已归档变更**：3（001-sdd-init, 002-project-onboarding, 003-git-and-docs）

---

## 架构概览

Hermes Harness 是一个 Agentic SDD 开发框架，结构如下：

```
用户项目
  ├── AGENTS.md               ← SDD 配置（项目入口）
  ├── CONSTITUTION.md          ← 不可违背的核心原则
  ├── QUIRKS.md                ← 陷阱与怪癖记录
  └── docs/
      ├── changes/             ← 进行中的 SDD 变更
      ├── current/             ← 当前基线（本文件）
      └── archive/             ← 已归档变更

Hermes Agent
  └── ~/.hermes/skills/sdd/    ← 8 角色 Skill + shared/
      ├── sdd-orchestrator/    ← 编排器（Phase 0-8）
      ├── po-agent/            ← PRD 产出
      ├── ba-agent/            ← Spec + AC
      ├── architect-agent/     ← Design + Tasks
      ├── coder-agent/         ← TDD 实现
      ├── reviewer-agent/      ← 三阶段评审
      ├── qa-agent/            ← 测试验证
      ├── sdd-init/            ← 项目初始化/升级
      ├── sdd-structure-lint/  ← 结构检查
      └── shared/              ← 共享规则与规范
```

---

## Skill 清单

| Skill | 阶段 | 职责 |
|------|:---:|------|
| [sdd-orchestrator](../skills/sdd/sdd-orchestrator/SKILL.md) | 编排 | 流程判定、阶段调度、门禁检查、归档 |
| [po-agent](../skills/sdd/po-agent/SKILL.md) | 定义 | 产出 PRD，明确用户场景与范围 |
| [ba-agent](../skills/sdd/ba-agent/SKILL.md) | 定义 | 产出 Spec，细化 AC（Given-When-Then） |
| [architect-agent](../skills/sdd/architect-agent/SKILL.md) | 设计 | Brainstorming + Design + Tasks 拆分 |
| [coder-agent](../skills/sdd/coder-agent/SKILL.md) | 实现 | 按 Tasks 逐步实现，TDD 强制 |
| [reviewer-agent](../skills/sdd/reviewer-agent/SKILL.md) | 评审 | 三阶段评审（Spec 合规/代码质量/架构一致性） |
| [qa-agent](../skills/sdd/qa-agent/SKILL.md) | 测试 | AC 覆盖矩阵、测试执行、环境差异、熔断 |
| [sdd-init](../skills/sdd/sdd-init/SKILL.md) | 基础设施 | 项目初始化 + 升级（init/upgrade 双模式） |
| [sdd-structure-lint](../skills/sdd/sdd-structure-lint/SKILL.md) | 基础设施 | 文件结构合规检查（3 级：文件/产物/内容） |

---

## 共享规范

| 文档 | 说明 |
|------|------|
| [sdd-rules.md](../skills/sdd/shared/sdd-rules.md) | 10 条通用规则（R1-R10） |
| [flow-level-rules.md](../skills/sdd/shared/flow-level-rules.md) | Quick/Standard/Enhanced 判定逻辑 |
| [handoff-protocol.md](../skills/sdd/shared/handoff-protocol.md) | Agent 间交接协议 |
| [convention-overrides.md](../skills/sdd/shared/convention-overrides.md) | 项目级规则覆盖机制 |
| [git-workflow.md](../skills/sdd/shared/git-workflow.md) | Git 分支/PR/合并策略规范 |

---

## 变更历史

| 变更 ID | 标题 | 影响范围 | 归档日期 |
|------|------|------|------|
| 001-sdd-init | SDD 项目初始化 | 8 个角色 Skill + shared/ | 2026-05-24 |
| 002-project-onboarding | 项目上手体验 | README + INSTALL + install.sh + templates/ + sdd-init 修改 | 2026-05-25 |
| 003-git-and-docs | Git 工作流 + 基线维护 + README | git-workflow.md + orchestrator Phase 8 + docs/current/ + README 升级 | 2026-05-25 |

---

## 核心文档

| 文档 | 说明 |
|------|------|
| [prd.md](prd.md) | 产品需求文档 — 目标、用户、功能范围、成功指标 |
| [spec.md](spec.md) | 规格说明 — 9 大需求、30+ AC、Given-When-Then 格式 |
| [design.md](design.md) | 技术设计 — 三层架构、文件格式、数据流、关键决策 |
