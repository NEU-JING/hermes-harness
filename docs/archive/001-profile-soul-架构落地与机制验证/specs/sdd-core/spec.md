# SDD Core Specification — Delta: 001-profile-soul

> **Delta 操作**: ADDED
> **变更日期**: 2026-06-16
> **变更类型**: Profile+Soul 双层差异化架构落地
> **归档来源**: docs/archive/001-profile-soul-架构落地与机制验证

---

## ADDED Requirements

### Requirement: Profile 声明式配置系统

**概述**: 通过 AGENTS.md 中的声明式映射定义各角色使用的 Profile，实现零代码的模型差异化配置。

#### Scenario AC24: 角色 Profile 映射
- **WHEN** AGENTS.md 包含 `sdd_config.role_to_profile` 映射表
- **AND** 包含 `profile_enabled: true`
- **THEN** orchestrator 读取映射，按角色创建 Kanban 任务时使用对应 Profile

#### Scenario AC25: Profile 不存在回退
- **WHEN** role_to_profile 中的 Profile 不存在于 `~/.hermes/profiles/`
- **THEN** orchestrator 打印警告并回退到无 Profile 模式

#### Scenario AC26: AGENTS.md 段边界隔离
- **WHEN** convention_overrides 段包含与 role_to_profile 相同的 key（如 `po:`）
- **AND** orchestator 解析 AGENTS.md 的 role_to_profile
- **THEN** 只匹配 role_to_profile 段内的角色键，不误抓其他段

#### Scenario AC27: 声明式配置优先
- **WHEN** AGENTS.md 和 orchestrator 默认都在 role_to_profile 中定义了 po
- **THEN** AGENTS.md 的配置覆盖默认值

### Requirement: 4 层一致性保障机制

**概述**: 解决模型输出长度截断问题，通过文档地图、上下文锚定、递归分块和一致性审计，不依赖特定模型的输出能力。

#### Scenario AC28: L1 文档地图生成
- **WHEN** BA/Architect Agent 需要生成长文档（>200 行）
- **THEN** 先生成完整大纲、术语表、引用注册表、命名约定（≤200 行）
- **AND** 所有分块生成时携带该地图

#### Scenario AC29: L2 上下文锚定
- **WHEN** 文档被拆分为多个分块
- **THEN** 每个分块携带前一章节最后 3 段 + 后一章节大纲
- **AND** 确保章节衔接自然不断裂

#### Scenario AC30: L3 递归分块
- **WHEN** 单个章节仍超过模型输出限制
- **THEN** 递归拆分为小节，最大深度 3 级
- **AND** Agent 自动判断是否需要拆分

#### Scenario AC31: L4 一致性审计
- **WHEN** 所有分块生成完成后
- **THEN** 执行标题层级检查、重复内容清理、过渡语优化、引用编号修正、术语一致性校验

### Requirement: 异构评审模式

**概述**: Reviewer 角色使用独立 Provider 提供完全不同的视角。

#### Scenario AC32: 异构 Provider 隔离
- **WHEN** Reviewer Agent 被调度
- **AND** sdd-reviewer Profile 配置了与开发角色不同的 Provider
- **THEN** Reviewer 使用自己 Profile 的 Provider 和模型执行评审

#### Scenario AC33: 模型使用审计
- **WHEN** 项目验收或复盘
- **THEN** 能追溯每个阶段实际使用的模型和 Provider
- **AND** 审计日志记录阶段名、模型名、Provider、Kanban 任务 ID

---
