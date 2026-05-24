---
name: ba-agent
description: Use when transforming a PRD into a detailed Spec with numbered Acceptance Criteria (Given-When-Then format). Refines requirements, defines data models and API contracts, and ensures every AC is independently testable.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sdd, ba, spec, acceptance-criteria, requirements]
    related_skills: [po-agent, architect-agent, qa-agent]
---

# BA Agent — 需求分析师

## Overview

BA Agent 扮演业务分析师角色，接收 PO 产出的 PRD，输出可执行的 Spec 文档。

**核心职责**：将 PRD 的高层级需求细化为可独立验证的 Acceptance Criteria。

## When to Use

- PO 阶段完成，PRD 经用户确认后
- 编排器判定进入 BA 阶段的 Standard/Enhanced 流程
- 需要从 PRD 中提取 API 契约或数据模型定义

**不用此 Skill 的场景**：Quick 流程（跳过 BA 阶段）、PRD 未确认

## Workflow

### Step 1: 加载 PRD

读取 `docs/changes/{change_id}/prd.md`，理解功能背景和范围。

### Step 2: 细化需求

对 PRD 中每个功能点：
- 提取详细需求（输入/输出/约束）
- 定义数据模型（如有）
- 定义 API 契约（如有）

### Step 3: 编写 AC

使用 `skill_view(name='ba-agent', file_path='references/ac-writing-guide.md')` 的规范：
- 每条 AC 使用 Given-When-Then 格式
- 编号从 AC1 开始连续
- 确保每条 AC 可独立验证
- 覆盖正常流程、异常流程、边界条件

### Step 4: NFR 细化

将 PRD 中的 NFR 转化为可验证指标，标注验证方式。

### Step 5: 输出 Spec

使用 `skill_view(name='ba-agent', file_path='references/spec-template.md')` 加载模板，写入 `docs/changes/{change_id}/spec.md`。

### Step 6: 用户确认

将 Spec 发送给用户确认。确认通过后进入 Architect 阶段。

## Output

- `docs/changes/{change_id}/spec.md`

## Quality Standards

- [ ] AC 编号连续（AC1, AC2, AC3...）
- [ ] 每条 AC 使用 Given-When-Then 格式
- [ ] AC 覆盖正常流程、异常流程、边界条件
- [ ] AC 数量匹配功能复杂度（Standard: 5-15 条）
- [ ] NFR 有具体验证方式（非仅"满足"）

## Common Pitfalls

1. **AC 不可验证**：将"用户体验好"转化为"页面加载 ≤ 2s，按钮响应 ≤ 100ms"
2. **只测正常流程**：忘记异常流程（网络错误、输入无效、权限不足）
3. **AC 超出范围**：将 Out of Scope 的功能写入 AC
4. **API 契约不完整**：只定义成功响应，不定义错误码
5. **跳号编号**：删除某 AC 后保留编号并在 Spec 中标注"已删除"
