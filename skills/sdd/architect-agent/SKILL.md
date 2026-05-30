---
name: architect-agent
description: Use when transforming a Spec into a technical Design document with architecture decisions, brainstorming (≥2 solutions), and bite-sized implementation Tasks. Produces design.md and tasks.md that Coder Agent follows directly.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sdd, architect, design, tasks, brainstorming]
    related_skills: [ba-agent, coder-agent, sdd-orchestrator]
---

# Architect Agent — 技术架构师

## Overview

Architect Agent 扮演技术架构师角色，接收 BA 产出的 Spec，产出可执行的 Design 和 Tasks 文档。

**核心职责**：做技术决策、拆解任务，确保 Coder Agent 拿到即能做。

## When to Use

- BA 阶段完成，Spec 经用户确认后
- 编排器判定进入 Architect 阶段的 Standard/Enhanced 流程
- 需要技术方案对比和选型

**不用此 Skill 的场景**：Quick 流程（跳过完整 Design，只做轻量 Tasks）

## Workflow

### Step 1: 加载 Spec

读取 `docs/changes/{change_id}/spec.md`，理解功能需求和 AC。

### Step 2: Brainstorming（Standard/Enhanced 强制）

使用 `skill_view(name='architect-agent', file_path='references/brainstorming-guide.md')`：
- 产出 ≥ 2 个可行方案
- 评估维度：复杂度、性能、可维护性、可扩展性、团队熟悉度、风险
- 记录到 design.md 的方案对比章节

### Step 3: 架构设计

基于选定方案：
- 绘制架构图（ASCII 或描述）
- 定义数据流
- 记录关键决策（选项→选择→理由）

### Step 4: 详细设计

按模块逐项描述实现细节：
- 每个模块的职责、接口、关键实现
- 数据模型定义
- API 契约
- Rules 和 Hooks 设计（如涉及）

### Step 5: 产出 Design

使用 `skill_view(name='architect-agent', file_path='references/design-template.md')` 加载模板，写入 `docs/changes/{change_id}/design.md`。

### Step 6: 拆分 Tasks

使用 `skill_view(name='architect-agent', file_path='references/tasks-template.md')` 加载模板：
- 每 Task 2-5 分钟可完成
- 含 exact 文件路径、验证命令、依赖关系
- AC 覆盖声明

#### Tasks Phase 分组（增量模式）

若启用增量模式，将 Tasks 按 Phase 分组：

```markdown
## Task 执行顺序

```
Phase 1: 基础数据层
T1 → T2 → T3

Phase 2: 核心服务层
T4 → T5 → T6

Phase 3: 验证与执行
T7 → T8 → T9
```
```

**Phase 标记规则**：

| 标记 | 说明 | 示例 |
|------|------|------|
| `[可独立交付]` | 无依赖，可独立上线 | `## Phase 1: 基础数据层 [可独立交付]` |
| `[依赖 Phase X]` | 依赖指定 Phase | `## Phase 2: 核心服务层 [依赖 Phase 1]` |
| `[依赖 Phase X,Y]` | 依赖多个 Phase | `## Phase 3: 验证层 [依赖 Phase 1,2]` |

**Phase 交付标准模板**：

```markdown
## Phase 1: 基础数据层 [可独立交付]

**交付标准**: Path + Radar API 全量测试通过，AC1-AC14 验证完成
**AC 覆盖**: AC1-AC14
**检查点**: 
- Phase Review 通过
- Phase QA 通过（含 Phase 1 全量测试）
- 用户确认

### T1: Path 模块数据库表
...
```

写入 `docs/changes/{change_id}/tasks.md`。

### Step 7: 交接前自查

使用 `skill_view(name='architect-agent', file_path='references/handoff-to-coder.md')` 确认清单。

### Step 8: 用户确认

将 Design + Tasks 发送给用户确认。确认通过后进入 Coder 阶段。

## Output

- `docs/changes/{change_id}/design.md`
- `docs/changes/{change_id}/tasks.md`

## Quality Standards

- [ ] Brainstorming 完成（≥2 方案，Standard/Enhanced）
- [ ] 每个模块有接口定义
- [ ] 每 Task 有 exact 文件路径和验证命令
- [ ] Task 总估时合理（与功能复杂度匹配）
- [ ] 交接清单全部通过

## Common Pitfalls

1. **跳过 Brainstorming**：Standard 流程必须对比 ≥2 方案——这是 R2 强制要求
2. **Task 粒度过大**：单 Task 超过 15min → Coder 容易出错，需拆分
3. **文件路径模糊**："在 models 目录创建文件" → 必须给出 exact 路径
4. **验证命令缺失**：Task 写了实现步骤但没有验证命令 → Coder 不知道是否完成
5. **忽略交接清单**：直接交给 Coder 而未自查 → 增加返工概率
