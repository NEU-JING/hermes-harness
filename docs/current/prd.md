# PRD — Hermes Harness（SDD 通用开发机制）

> **Product Requirements Document**
> 版本：1.0 | 最后更新：2026-05-25

---

## 1. 背景与目标

### 1.1 问题陈述

AI Agent 编码存在三个系统性缺陷：

| 问题 | 现象 | 根因 |
|------|------|------|
| **流程缺失** | Agent 跳过 Spec、忽略测试、直接 push main | 无结构化流程约束 |
| **质量不稳** | 写完即忘，同一坑反复踩 | 无跨会话记忆、无强制 Review/QA |
| **不可追溯** | 需求→代码之间无审计链 | 产物散落、格式不统一 |

这些"捷径"在原型阶段无伤大雅，但在生产级项目中累积为技术债，且**不同项目重复踩同样的坑**。

### 1.2 目标

构建一套**跨项目可复用的 Agentic 开发流程引擎**（Hermes Harness），将软件工程最佳实践编码为 Agent 可执行的 Skill，让 AI Agent 像一支工程团队一样工作。

**三个层次**：
1. **通用层** — 流程骨架 + 角色 Skill + 共享规范，一次开发多项目复用
2. **项目层** — 每个项目通过 `AGENTS.md` 声明技术栈、路径、自定义规则
3. **实例层** — 每次变更的产物（PRD→Spec→Design→Tasks→Review→QA），归档到 `docs/archive/`

### 1.3 核心原则

> **流程通用化、角色 Skill 化、项目配置化**

- SDD 不做 Agent 的替代品——它做 Agent 的**工程规范层**
- 所有流程描述在 Skills 中，项目配置（AGENTS.md）只声明"我是谁、用哪套流程、有什么约束"

---

## 2. 目标用户与场景

### 2.1 用户画像

| 角色 | 场景 |
|------|------|
| **独立开发者** | 用 AI Agent 开发个人项目，需要流程约束防止偷工减料 |
| **技术负责人** | 管理 AI Agent 辅助的团队开发，需要统一流程标准和产物格式 |
| **平台产品负责人** | 在组织内推广 AI Agent 开发模式，需要可复制的流程框架 |

### 2.2 典型工作流

```
用户："/sdd start 用户登录功能"

编排器：
  1. 判定流程级别 → Standard
  2. PO Agent → 产出 prd.md → 用户确认
  3. BA Agent → 产出 spec.md（含 AC） → 用户确认
  4. Architect Agent → Brainstorming ≥2 方案 → design.md + tasks.md → 用户确认
  5. Coder Agent → TDD 逐 Task 实现 → 代码 + 测试
  6. Reviewer Agent → 三阶段评审 → review-report.md
  7. QA Agent → AC 覆盖矩阵 + 测试执行 → qa-report.md
  8. 用户验收 → 分类打回或确认通过
  9. 归档 → 基线融合 + 变更移入 archive/
```

---

## 3. 功能范围

### 3.1 核心能力

| 模块 | 功能 | 优先级 |
|------|------|:--:|
| **流程编排** | 判定流程级别（Quick/Standard/Enhanced）、调度角色、门禁检查 | P0 |
| **角色系统** | 8 个角色 Skill（PO/BA/Architect/Coder/Reviewer/QA/Init/Lint） | P0 |
| **项目初始化** | `sdd-init`：新项目交互式搭建 + 存量项目无痛升级 | P0 |
| **结构验证** | `sdd-structure-lint`：三级验证（文件/产物/内容）| P0 |
| **用户门禁** | PO/BA/Architect 后用户确认、验收通过后归档 | P0 |
| **闭环回退** | Reviewer↔Coder（2 轮）、QA↔Coder（4 轮）→ 熔断 | P0 |
| **基线维护** | `docs/current/` 作为融合后的生产全貌，非变更日志堆砌 | P1 |
| **Git 工作流** | Feature 分支 + PR（merge 在验收后）+ R10 合规检查 | P1 |
| **中断恢复** | `.sdd-state.json` 状态持久化，重启后从断点继续 | P1 |

### 3.2 流程级别

| 级别 | 适用场景 | 阶段 |
|------|---------|------|
| **Quick** | Bug 修复、配置变更 | Architect 轻量 → Coder → QA 轻量 |
| **Standard** | 常规功能开发（默认） | PO→BA→Architect→Coder→Reviewer→QA→验收→归档 |
| **Enhanced** | 安全/性能关键 | Standard + 安全审查 + 性能测试 + 灰度验证 |

### 3.3 不在范围内

- 代码质量工具本身（black/isort/ruff 属于项目配置，非 SDD 框架）
- CI/CD 流水线实现（SDD 只定义 CI-only marker 规范，不实现具体 CI 配置）
- 项目管理（Issue 跟踪、Sprint 规划等）

---

## 4. 非功能需求

| 需求 | 说明 |
|------|------|
| **通用性** | Skills 不依赖特定项目路径、技术栈、数据库 |
| **可安装性** | 一键安装（`./install.sh`），支持 `--force` 覆盖更新 |
| **Token 效率** | 角色 SKILL.md ~70 行，references 按需加载 |
| **可扩展性** | 项目可通过 AGENTS.md `convention_overrides` 添加/禁用规则 |

---

## 5. 风险与假设

| 风险 | 缓解措施 |
|------|---------|
| Skills 内容密度过高导致 Agent 遵循度下降 | 角色 SKILL.md 控制在 ~70 行，复杂逻辑拆到 references |
| 不同 Agent 平台对 Skill 格式兼容性差异 | 纯 Markdown 格式，YAML frontmatter，零平台锁定 |
| 存量项目升级时丢失自定义配置 | `sdd-upgrade` 先分析后计划，用户确认前不执行任何写操作 |
| git-workflow 规范本身成为违反对象 | 通过 R10 在归档前强制检查，SDD 项目自身也遵守 |

### 5.1 假设

- 目标项目使用 Git 版本控制
- 用户愿意在每个阶段确认门禁（PO/BA/Architect 后各一次）
- Agent 运行环境支持 skill_view 文档地图机制（Hermes Agent v2.0+）

---

## 6. 成功指标

- 一个全新项目通过 `sdd-init` 在 2 分钟内完成骨架搭建
- 一个存量项目（如 AILP）通过 `sdd-upgrade` 无丢失接入 SDD
- 3 个不同技术栈的项目（Python/Go/JS）用同一套 Skills 走通完整 SDD 流程
- README.md 的流程图 + 门禁表能让人 1 分钟理解 SDD 流程
