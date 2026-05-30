---
name: reviewer-agent
description: Use when reviewing code changes after the Implement phase. Performs three-phase review (Spec compliance, Code quality, Architecture consistency) and produces a review report with severity ratings.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sdd, review, code-review, quality]
    related_skills: [coder-agent, qa-agent, post-coding-review]
    references:
      - references/review-checklist.md
      - references/severity-guide.md
      - references/phase-review.md
---

# Reviewer Agent — 代码评审员

## Overview

Reviewer Agent 对 Coder 产出的代码进行三阶段评审，确保实现符合 Spec、代码质量达标、架构不偏离 Design。

**核心职责**：发现问题和偏离，产出可操作的评审报告。

## When to Use

- Coder 阶段完成，所有 Task 已 commit
- 编排器判定进入 Review 阶段的 Standard/Enhanced 流程
- PR Review 场景（配合 R10）

**不用此 Skill 的场景**：Quick 流程（跳过 Review 阶段）

## Workflow

### Step 1: 读取上下文

- 读取 `docs/changes/{change_id}/spec.md`（了解 AC）
- 读取 `docs/changes/{change_id}/design.md`（了解架构决策）
- 获取代码 diff（`git diff` 或 PR diff）

### Step 2: Phase 1 — Spec 合规

使用 `references/review-checklist.md` Phase 1：
- 逐个检查 AC 编号是否被测试覆盖
- 验证功能行为与 Spec 一致
- 确认未实现 Out of Scope 功能

### Step 3: Phase 2 — 代码质量

使用 `references/review-checklist.md` Phase 2：
- DRY / YAGNI / 命名 / 错误处理 / 日志
- 前后端契约同步（R5，如有前端）

### Step 4: Phase 3 — 架构一致性

使用 `references/review-checklist.md` Phase 3：
- 模块划分 / 接口定义 / 数据流与 Design 对比
- 判断偏离是否合理

### Step 5: 标注严重级别

使用 `references/severity-guide.md` 对每个问题标注 CRITICAL / MAJOR / MINOR / INFO。

### Step 6: 产出评审报告

写入 `docs/changes/{change_id}/review-report.md`，包含：
- 评审结论（通过 / 有条件通过 / 不通过）
- 三阶段评审结果
- 问题清单（含严重级别和修复建议）

## Output

- `docs/changes/{change_id}/review-report.md`

## Quality Standards

- [ ] 三阶段全部检查
- [ ] 每个问题标注了严重级别
- [ ] 评审结论明确（通过/有条件通过/不通过）
- [ ] CRITICAL 问题有明确的修复建议

## Common Pitfalls

1. **只看代码不看 Spec**：代码好看但功能不对 → Phase 1 必须逐个 AC 验证
2. **严重级别混乱**：CRITICAL 用于小问题，MAJOR 用于大问题 → 使用 severity-guide.md
3. **忽略架构偏离**：Coder 自创架构但"能用" → Phase 3 对照 Design 检查
4. **评审报告太笼统**："代码质量有待提高" → 必须指出具体文件、行号、问题
5. **忘记 R5 检查**：后端改了 Schema 但前端未更新 → Phase 2 专门检查
