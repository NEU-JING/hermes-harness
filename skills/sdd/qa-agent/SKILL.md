---
name: qa-agent
description: Use when verifying that implemented changes pass all tests and meet Acceptance Criteria. Generates AC coverage matrix from E2E tests, checks CI-only marker compliance (R9), and enforces circuit-breaker for fix loops.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sdd, qa, testing, ac-coverage, e2e]
    related_skills: [reviewer-agent, coder-agent, sdd-orchestrator]
---

# QA Agent — 测试工程师

## Overview

QA Agent 验证实现是否通过所有测试，AC 是否全覆盖，以及环境差异是否符合规范。

**核心职责**：运行测试、生成覆盖矩阵、检查 CI-only 标记、执行熔断逻辑。

## When to Use

- Review 阶段完成（结论为通过或有条件通过）
- 编排器判定进入 QA 阶段
- 用户验收前的最后质量关卡

**不用此 Skill 的场景**：Review 结论为不通过（需先修复 CRITICAL 问题）

## Workflow

### Step 1: 运行测试

根据项目配置运行测试：

```bash
# 单元测试
pytest tests/unit/ -v

# 集成测试（如有，可能在 CI-only）
pytest tests/integration/ -v -m "not ci_only"

# E2E 测试（CI 环境）
npx playwright test
```

### Step 2: AC 覆盖矩阵

使用 `references/e2e-ac-mapping-template.md`：
1. 提取 `spec.md` 所有 AC 编号
2. 在 E2E 测试文件中搜索引用
3. 生成覆盖矩阵
4. 标记缺失覆盖的 AC

### Step 3: CI-only 标记检查（R9）

使用 `references/ci-only-guide.md`：
1. 搜索所有 `ci_only` / `skipif.*CI` 标记
2. 验证每个标记有原因注释
3. 验证本地运行时 CI-only 测试被 skip
4. 标记无注释的 CI-only 测试为 REQ

### Step 4: 环境差异记录

记录测试在不同环境的差异：
- 本地跳过但 CI 通过的测试（正常）
- 本地通过但 CI 失败的测试（需排查）
- CI-only 测试的覆盖范围

### Step 5: 修复循环管理

使用 `references/circuit-breaker.md`：
- 首次发现问题 → 标记，返回 Coder（轮次 1）
- 二次发现问题 → 标记，返回 Coder（轮次 2）
- 三次发现问题 → 触发熔断，通知用户

### Step 6: 产出 QA 报告

使用 `references/qa-report-template.md` 写入 `docs/changes/{change_id}/qa-report.md`。

## Output

- `docs/changes/{change_id}/qa-report.md`

## Quality Standards

- [ ] 所有非 CI-only 测试在本地通过
- [ ] 所有测试在 CI 通过
- [ ] AC 覆盖矩阵完整
- [ ] CI-only 标记有原因注释
- [ ] 修复循环未超限（≤ 2 轮）

## Common Pitfalls

1. **AC 覆盖遗漏**：只看测试通过数，不看是否覆盖所有 AC → 使用覆盖矩阵
2. **忽略 CI-only 标记检查**：R9 要求 CI-only 测试必须标记并有注释
3. **忘记熔断**：连续多次失败仍自动循环 → 必须追踪轮次，超限熔断
4. **测试环境不一致**：本地通过但 CI 失败而未记录 → 必须标注环境差异
5. **只跑单元测试**：Standard 流程要求跑 E2E，Quick 流程可跳过 E2E（R7 豁免）
