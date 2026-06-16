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

---

## Delta: 001-profile-soul-架构落地与机制验证

> 变更日期: 2026-06-16 | 类型: Profile+Soul 架构 | 状态: 已归档
> 归档来源: docs/archive/001-profile-soul-架构落地与机制验证/design.md

### 核心设计原则

| 原则 | 说明 |
|------|------|
| **零侵入** | 不修改 Hermes Agent 核心代码，所有能力通过 Profile 配置和脚本实现 |
| **完全隔离** | 每个 Profile 独立配置、独立模型、独立 Skill，互不干扰 |
| **声明式驱动** | 所有配置集中在 AGENTS.md，脚本从配置自动生成，不硬编码 |
| **可审计** | 全流程模型使用可追溯、可验证、可复盘 |

### 架构总览

```
AGENTS.md (配置源) → init-profiles.sh (模板化生成) → ~/.hermes/profiles/ (6个Profile)
                                                              │
                                                              ▼
                                              orchestrator.py (状态机调度器)
                                              ├── Kanban 轮询/重试
                                              ├── 内容门禁检查
                                              └── 模型使用审计
```

### Profile 配置

| Profile | 推荐模型 | Provider | Skill |
|---------|---------|----------|-------|
| sdd-po | deepseek-v4-flash | DeepSeek | po-agent + sdd-orchestrator |
| sdd-ba | deepseek-v4-flash | DeepSeek | ba-agent + sdd-orchestrator |
| sdd-architect | deepseek-v4-flash | DeepSeek | architect-agent + sdd-orchestrator |
| sdd-coder | deepseek-v4-flash | DeepSeek | coder-agent + sdd-orchestrator |
| sdd-reviewer | deepseek-v4-pro | DeepSeek | reviewer-agent + sdd-orchestrator |
| sdd-qa | deepseek-v4-flash | DeepSeek | qa-agent + sdd-orchestrator |

### 三层一致性保障

| 层级 | 机制 | 说明 |
|------|------|------|
| L1 | 文档地图 + 递归分块 | 提前生成全局结构/术语/引用；最大 3 级递归拆分 |
| L2 | 上下文锚定 | 每个分块携带完整文档地图 + 相邻上下文 |
| L3 | 一致性审计 | 术语/引用/编号/格式全量检查 |

### 交付物

| 文件 | 说明 |
|------|------|
| `scripts/init-profiles.sh` | 多技能、零硬编码路径的 Profile 初始化脚本 |
| `scripts/validate-*.sh` | 4 个验证脚本 |
| `scripts/templates/profile/` | Profile 配置模板 |
| `scripts/setup-sdd-profiles.sh.deprecated` | 废弃的旧版脚本 |
| `docs/PROFILES-GUIDE.md` | Profile 操作指南 |
| `skills/.../orchestrator.py` | 增强版编排器（轮询 + 内容门禁 + 审计） |
