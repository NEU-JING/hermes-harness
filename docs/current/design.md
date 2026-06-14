# Design Baseline

> **归档来源**: change 003-openspec-improvements
> **归档时间**: 2026-06-14T13:47:24+08:00

---

## 变更摘要

**目标**: 基于 OpenSpec 规范对 SDD 流程进行 4 项改进：探索模式、Spec 格式统一、Baseline 迁移 + Delta Spec、Telemetry。

### 关键决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 探索模式实现 | 独立 Skill | 独立职责、可复用、低耦合 |
| Spec 格式 | OpenSpec 单一格式（WHEN/THEN + AND 链） | 简洁、标准统一、与社区对齐 |
| 基线结构 | docs/specs/<capability>/ 多文件 | 可按能力域独立演进 |
| Delta 操作方式 | ## 操作头（ADDED/MODIFIED/REMOVED/RENAMED） | 直观、Git 友好、易于自动化解析 |
| Telemetry 存储 | NDJSON 文件 | 追加高效、无锁、支持流式处理 |
| Telemetry 默认 | 关闭 | 隐私优先原则 |

### 架构变更

1. **新增模块**: explore-agent（独立 Skill，/explore 触发）
2. **增强模块**: ba-agent（OpenSpec 格式产出）、sdd-orchestrator（归档6步流程、telemetry 记录）
3. **新建结构**: docs/specs/ 多文件基线体系
4. **新建子系统**: telemetry（~/.hermes/telemetry/ 本地存储）

### 变更文件清单

| 文件 | 变更类型 |
|------|:--------:|
| skills/sdd/explore-agent/SKILL.md | 新增 |
| skills/sdd/explore-agent/references/explore-guide.md | 新增 |
| skills/sdd/ba-agent/SKILL.md | 修改 |
| skills/sdd/ba-agent/references/spec-template.md | 修改 |
| skills/sdd/sdd-structure-lint/SKILL.md | 修改 |
| skills/sdd/sdd-init/SKILL.md | 修改 |
| skills/sdd/sdd-orchestrator/SKILL.md | 修改 |
| skills/sdd/sdd-orchestrator/references/delta-spec.md | 新增 |
| skills/sdd/sdd-orchestrator/references/design-baseline.md | 新增 |
| skills/sdd/sdd-orchestrator/references/telemetry.md | 新增 |
