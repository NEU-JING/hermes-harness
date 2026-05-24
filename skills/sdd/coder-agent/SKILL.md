---
name: coder-agent
description: Use when implementing Tasks from tasks.md following TDD (RED-GREEN-REFACTOR). Writes failing tests first, implements minimal code to pass, refactors, and produces task completion reports.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sdd, coder, tdd, implementation]
    related_skills: [architect-agent, reviewer-agent, test-driven-development]
---

# Coder Agent — 开发者

## Overview

Coder Agent 执行 Tasks 文档中的每个 Task，严格遵循 TDD 流程。

**核心职责**：把 Tasks 文档转化为可工作的代码，每个 Task 都经过 RED→GREEN→REFACTOR。

## When to Use

- Architect 阶段完成，Design + Tasks 经用户确认后
- 编排器判定进入 Implement 阶段
- 任何流程级别（Quick/Standard/Enhanced）都需要 Coder Agent

**不用此 Skill 的场景**：纯文档更新（无代码变更）

## Workflow（每 Task）

### Step 1: RED — 写失败测试

参考 `references/tdd-workflow.md`：
1. 根据 AC 编写测试
2. 运行测试确认失败
3. 记录失败原因

### Step 2: GREEN — 最小实现

1. 写刚好让测试通过的代码
2. 运行测试确认通过
3. 不写任何测试未覆盖的代码（YAGNI）

### Step 3: REFACTOR — 重构

1. 消除重复
2. 改善命名
3. 提取公共逻辑
4. 运行全量测试确认通过

### Step 4: NFR 自检

使用 `references/nfr-checklist.md` 检查性能、安全、错误处理、可维护性。

### Step 5: 编码约定自检

使用 `references/convention-checklist.md` 检查代码风格、命名、文档。

### Step 6: 产出完成报告

使用 `references/task-completion-report-template.md` 记录：
- 修改文件
- 测试结果
- TDD 确认
- 未覆盖的 AC

### Step 7: Commit

```bash
git add {files}
git commit -m "feat({scope}): T{n} {描述}"
```

## Output

- 代码变更（Git commits）
- Task 完成报告（每 Task 一个）

## Quality Standards

- [ ] 每个 Task 经过 RED→GREEN→REFACTOR
- [ ] 测试覆盖正常流程、异常流程、边界条件
- [ ] NFR checklist 全部通过
- [ ] 编码约定全部通过
- [ ] commit message 格式正确

## Common Pitfalls

1. **跳过 RED 阶段**：先写代码再补测试 → 违反 R3（TDD 强制）
2. **过度实现**：写了 AC 未覆盖的代码 → YAGNI 违规
3. **跳过 REFACTOR**：代码能跑就不管 → Review 阶段会被打回
4. **忽略 NFR**：功能对但性能差/不安全 → QA 阶段会被标记
5. **一个 commit 包含多个 Task**：难以回滚和评审 → 每 Task 一个 commit
6. **测试依赖外部状态**：测试在 CI 失败但在本地通过 → 违反 R6
