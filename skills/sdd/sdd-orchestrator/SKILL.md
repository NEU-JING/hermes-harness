---
name: sdd-orchestrator
description: Central workflow orchestrator for SDD. Enforces strict phase gates, manages state machine transitions, and delegates to role agents via delegate_task.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sdd, orchestrator, workflow, state-machine, delegate]
    related_skills: [sdd-init, sdd-structure-lint, po-agent, ba-agent, architect-agent, coder-agent, reviewer-agent, qa-agent]
    references:
      - references/state-machine.md
      - references/phase-gates.md
      - references/delegate-protocol.md
      - references/incremental-mode.md
      - references/interrupt-recovery.md
---

# SDD Orchestrator v2.0 — 严格状态机编排器

## Overview

编排器是 SDD 流程的**中央状态机**。职责：
1. **状态管理**：维护 `.sdd-state.json`，驱动状态机推进
2. **门禁强制**：每个状态转换必须通过对应Level的lint检查
3. **Agent委托**：使用 `delegate_task` 实际调度各角色Agent
4. **流程管控**：任何偏离都阻断，必须修复后才能继续

**核心原则**：编排器不直接产出文档，只负责**状态推进和Agent调度**。

---

## State Machine（状态机）

### Standard 流程状态图

```
┌─────────┐    init     ┌─────────┐   lint L1   ┌─────────┐
│  IDLE   │ ──────────▶ │   PO    │ ──────────▶ │  PO_    │
│ (start) │             │ (entry) │             │ CHECK   │
└─────────┘             └────┬────┘             └────┬────┘
                             │                        │
                             │ delegate po-agent      │ lint pass?
                             │ ◀──────────────────────┘
                             │ NO: retry/block
                             │ YES: proceed
                             ▼
                       ┌─────────┐    user     ┌─────────┐
                       │  PO_    │ ──────────▶ │   BA    │
                       │  DONE   │   confirm   │ (entry) │
                       └────┬────┘             └────┬────┘
                            │                       │
                            ▼                       ▼
                      [prd.md created]        [lint + delegate
                                                ba-agent]

┌─────────┐   user    ┌─────────┐   lint    ┌─────────┐   delegate   ┌─────────┐
│   BA    │ ────────▶ │  BA_    │ ───────▶ │ARCHITECT│ ───────────▶ │ ARCH_   │
│  DONE   │ confirm   │ CHECK   │  pass   │ (entry)  │ architect-   │ CHECK   │
└─────────┘           └─────────┘         └────┬────┘   agent       └────┬────┘
                                               │                        │
                                               ▼                        ▼
                                         [design.md +              [lint pass?
                                          tasks.md created]          user confirm?]
┌─────────┐   lint    ┌─────────┐   delegate   ┌─────────┐   lint    ┌─────────┐
│ CODER   │ ───────▶ │ CODER_  │ ───────────▶ │REVIEWER │ ───────▶ │ REVIEW_ │
│(entry)  │  L2.5    │ CHECK   │  reviewer-   │(entry)   │  L3      │ CHECK   │
│         │          │         │  agent       │          │          │         │
└────┬────┘          └────┬────┘              └────┬────┘          └────┬────┘
     │                    │                        │                   │
     │ delegate           │ tasks all done?        │ review passed?    │
     │ coder-agent        │ NO: continue           │ NO: back to coder │
     │ (per task)         │ YES: proceed           │ YES: proceed      │
     ▼                    ▼                        ▼                   ▼
[commits]           [task reports]          [review-report.md]   [conclusion]

┌─────────┐   lint    ┌─────────┐   delegate   ┌─────────┐   user    ┌─────────┐
│   QA    │ ───────▶ │  QA_    │ ───────────▶ │  USER   │ ───────▶ │ARCHIVE_ │
│(entry)  │  pass   │ CHECK   │   qa-agent   │ACCEPT   │ confirm   │ENTRY    │
└────┬────┘         └────┬────┘              └────┬────┘           └────┬────┘
     │                   │                        │                    │
     │                   │ qa passed?             │                    │ R10 + L3
     │                   │ NO: back to coder      │                    │
     │                   │ YES: proceed           │                    ▼
     ▼                   ▼                        ▼               [archive done]
[tests run]        [qa-report.md]         [user says "归档"]
```

### 状态定义

| 状态 | 类型 | 说明 | 产物检查 |
|------|:---:|:---|:---|
| `IDLE` | 初始 | 流程未开始 | 无 |
| `PO_ENTRY` | 执行 | PO Agent执行中 | `.sdd-state.json` 存在 |
| `PO_CHECK` | 门禁 | L1检查PRD | `changes/{id}/prd.md` |
| `PO_DONE` | 等待 | 等待用户确认 | `changes/{id}/prd.md` 存在 |
| `BA_ENTRY` | 执行 | BA Agent执行中 | `prd.md` 存在 |
| `BA_CHECK` | 门禁 | L1+L2检查Spec | `changes/{id}/spec.md` |
| `BA_DONE` | 等待 | 等待用户确认 | `spec.md` 存在 |
| `ARCHITECT_ENTRY` | 执行 | Architect Agent执行中 | `spec.md` 存在 |
| `ARCHITECT_CHECK` | 门禁 | L2检查Design+Tasks | `changes/{id}/design.md` + `tasks.md` |
| `ARCHITECT_DONE` | 等待 | 等待用户确认 | Design + Tasks 存在 |
| `CODER_ENTRY` | 执行 | Coder Agent执行中 | `tasks.md` + Git clean |
| `CODER_CHECK` | 门禁 | L2.5检查代码+报告 | Task完成报告 + commits |
| `REVIEWER_ENTRY` | 执行 | Reviewer Agent执行中 | 代码已提交 |
| `REVIEWER_CHECK` | 门禁 | L3检查Review报告 | `changes/{id}/review-report.md` |
| `QA_ENTRY` | 执行 | QA Agent执行中 | Review通过 |
| `QA_CHECK` | 门禁 | L3检查QA报告 | `changes/{id}/qa-report.md` |
| `USER_ACCEPT` | 等待 | 等待用户验收确认 | QA通过 |
| `ARCHIVE_ENTRY` | 执行 | 归档执行中 | 用户确认 |
| `DONE` | 终止 | 流程完成 | 归档完成 |
| `BLOCKED` | 终止 | 流程阻断 | 需人工介入 |

---

## State Transition（状态转换）

### 转换规则

每个状态转换必须满足：
1. **前置条件**：当前状态的产物检查通过
2. **Lint检查**：调用 `sdd-structure-lint` 对应Level
3. **用户确认**（可选）：特定状态需要用户明确输入

### 转换矩阵

| 当前状态 | 触发条件 | 下一状态 | Lint Level | 用户确认 |
|---------|---------|---------|:----------:|:--------:|
| `IDLE` | `sdd start` | `PO_ENTRY` | L1 | ❌ |
| `PO_ENTRY` | po-agent完成 | `PO_CHECK` | L1 | ❌ |
| `PO_CHECK` | lint通过 | `PO_DONE` | — | ❌ |
| `PO_DONE` | 用户说"继续" | `BA_ENTRY` | — | ✅ |
| `BA_ENTRY` | ba-agent完成 | `BA_CHECK` | L1+L2 | ❌ |
| `BA_CHECK` | lint通过 | `BA_DONE` | — | ❌ |
| `BA_DONE` | 用户说"继续" | `ARCHITECT_ENTRY` | — | ✅ |
| `ARCHITECT_ENTRY` | architect-agent完成 | `ARCHITECT_CHECK` | L2 | ❌ |
| `ARCHITECT_CHECK` | lint通过 | `ARCHITECT_DONE` | — | ❌ |
| `ARCHITECT_DONE` | 用户说"开始编码" | `CODER_ENTRY` | — | ✅ |
| `CODER_ENTRY` | coder-agent完成 | `CODER_CHECK` | L2.5 | ❌ |
| `CODER_CHECK` | lint通过 | `REVIEWER_ENTRY` | — | ❌ |
| `REVIEWER_ENTRY` | reviewer-agent完成 | `REVIEWER_CHECK` | L3 | ❌ |
| `REVIEWER_CHECK` | review通过 | `QA_ENTRY` | — | ❌ |
| `REVIEWER_CHECK` | review不通过 | `CODER_ENTRY` | — | ❌ |
| `QA_ENTRY` | qa-agent完成 | `QA_CHECK` | L3 | ❌ |
| `QA_CHECK` | qa通过 | `USER_ACCEPT` | — | ❌ |
| `QA_CHECK` | qa不通过 | `CODER_ENTRY` | — | ❌ |
| `USER_ACCEPT` | 用户说"归档" | `ARCHIVE_ENTRY` | — | ✅ |
| `ARCHIVE_ENTRY` | 归档完成 | `DONE` | R10+L3 | ❌ |

---

## Agent Delegation（Agent委托）

编排器使用 `delegate_task` 调用各角色Agent。

### 委托协议

```yaml
delegate_task:
  goal: "[当前阶段目标]"
  context: |
    # 当前变更上下文
    change_id: "{change_id}"
    current_state: "{state}"
    flow_level: "{Quick|Standard|Enhanced}"
    incremental_mode: "{true|false}"
    
    # 前置产物（路径列表）
    prerequisites:
      - "{prereq1_path}"
      - "{prereq2_path}"
    
    # 产出要求
    deliverables:
      - file: "{output_path}"
        template: "{template_ref}"
    
    # 约束（来自AGENTS.md/CONSTITUTION.md）
    constraints:
      - "{constraint1}"
      - "{constraint2}"
  
  toolsets: ["file", "terminal", "skills"]
  role: "leaf"
```

### 各阶段委托规范

#### PO阶段委托

```yaml
goal: "根据变更描述产出PRD文档，明确目标、用户、功能范围、非目标、成功指标"
context: |
  change_id: "{change_id}"
  description: "{user_input_description}"
  phase: "po"
  output: "docs/changes/{change_id}/prd.md"
  
  # PRD必须包含的章节
  required_sections:
    - "背景与目标"
    - "目标用户"
    - "功能范围（功能表）"
    - "非目标"
    - "成功指标"
    - "用户场景"

deliverables:
  - file: "docs/changes/{change_id}/prd.md"
    template: "po-agent/templates/prd-template.md"
```

#### BA阶段委托

```yaml
goal: "根据PRD产出Spec文档，细化需求并编写AC（Given-When-Then）"
context: |
  change_id: "{change_id}"
  prd_path: "docs/changes/{change_id}/prd.md"
  phase: "ba"
  output: "docs/changes/{change_id}/spec.md"
  
  # Spec必须包含的章节
  required_sections:
    - "需求清单（R1-RN，对应PRD功能）"
    - "每个需求的AC（Given-When-Then）"
    - "边界情况"
    - "数据契约"

deliverables:
  - file: "docs/changes/{change_id}/spec.md"
    template: "ba-agent/templates/spec-template.md"
```

#### Architect阶段委托

```yaml
goal: "根据Spec产出Design文档和Tasks拆分"
context: |
  change_id: "{change_id}"
  spec_path: "docs/changes/{change_id}/spec.md"
  phase: "architect"
  outputs:
    - "docs/changes/{change_id}/design.md"
    - "docs/changes/{change_id}/tasks.md"
  
  # Design必须包含的章节
  required_sections:
    - "架构决策"
    - "数据流/时序图"
    - "接口定义"
    - "产出物清单"
  
  # Tasks必须包含的章节
  task_requirements:
    - "按业务场景拆分的Task列表"
    - "每个Task可独立部署"
    - "Task间依赖关系"
    - "Phase标记（增量模式）"

deliverables:
  - file: "docs/changes/{change_id}/design.md"
    template: "architect-agent/templates/design-template.md"
  - file: "docs/changes/{change_id}/tasks.md"
    template: "architect-agent/templates/tasks-template.md"
```

#### Coder阶段委托

```yaml
goal: "按Tasks逐步实现代码，每个Task遵循TDD"
context: |
  change_id: "{change_id}"
  tasks_path: "docs/changes/{change_id}/tasks.md"
  design_path: "docs/changes/{change_id}/design.md"
  phase: "coder"
  
  # TDD要求
  tdd_requirements:
    - "每个Task必须先写测试（RED）"
    - "实现代码使测试通过（GREEN）"
    - "重构（REFACTOR）"
    - "提交commit"
  
  # 代码约束（来自AGENTS.md）
  code_constraints: "{from AGENTS.md conventions}"

deliverables:
  - type: "commits"
    branch: "feat/{change_id}"
  - file: "docs/changes/{change_id}/completion-report.md"
    template: "coder-agent/templates/task-completion-report.md"
```

#### Reviewer阶段委托

```yaml
goal: "评审代码实现，检查Spec合规、代码质量、架构一致性"
context: |
  change_id: "{change_id}"
  spec_path: "docs/changes/{change_id}/spec.md"
  design_path: "docs/changes/{change_id}/design.md"
  completion_report: "docs/changes/{change_id}/completion-report.md"
  phase: "reviewer"
  
  # 三阶段评审
  review_phases:
    - "Phase 1: Spec合规（AC覆盖检查）"
    - "Phase 2: 代码质量（DRY/YAGNI/命名/错误处理）"
    - "Phase 3: 架构一致性（模块/接口/数据流）"
  
  # 严重级别
  severity_levels: ["CRITICAL", "MAJOR", "MINOR", "INFO"]

deliverables:
  - file: "docs/changes/{change_id}/review-report.md"
    template: "reviewer-agent/templates/review-report.md"
    required_sections:
      - "评审结论（通过/有条件通过/不通过）"
      - "问题清单（严重级别排序）"
      - "修复建议"
```

#### QA阶段委托

```yaml
goal: "验证AC覆盖，执行测试，产出QA报告"
context: |
  change_id: "{change_id}"
  spec_path: "docs/changes/{change_id}/spec.md"
  review_report: "docs/changes/{change_id}/review-report.md"
  phase: "qa"
  
  # QA检查
  qa_checks:
    - "AC覆盖矩阵（每个AC有测试）"
    - "测试执行（单元/集成/E2E）"
    - "环境差异检查"
    - "熔断检查（连续失败）"

deliverables:
  - file: "docs/changes/{change_id}/qa-report.md"
    template: "qa-agent/templates/qa-report.md"
    required_sections:
      - "AC覆盖矩阵"
      - "测试结果统计"
      - "环境差异说明"
      - "结论（通过/不通过）"
```

---

## Phase Gates（阶段门禁）

每个状态转换必须通过的检查。

### Lint Level 映射

| 状态转换 | Lint Level | 检查内容 |
|---------|:----------:|---------|
| `IDLE → PO_ENTRY` | L1 | 目录结构初始化 |
| `PO_ENTRY → PO_CHECK` | L1 | PRD文件存在、格式正确 |
| `BA_ENTRY → BA_CHECK` | L1+L2 | Spec文件存在、AC格式正确 |
| `ARCHITECT_ENTRY → ARCHITECT_CHECK` | L2 | Design+Tasks存在、格式正确 |
| `CODER_ENTRY → CODER_CHECK` | L2.5 | Task完成、commits存在 |
| `REVIEWER_ENTRY → REVIEWER_CHECK` | L3 | Review报告存在、结论明确 |
| `QA_ENTRY → QA_CHECK` | L3 | QA报告存在、AC覆盖完整 |
| `ARCHIVE_ENTRY → DONE` | R10+L3 | PR merged、归档结构正确 |

### 门禁执行流程

```python
def phase_gate_transition(current_state, next_state):
    """状态转换门禁检查"""
    
    # 1. 确定需要的lint level
    lint_level = get_lint_level(current_state, next_state)
    
    # 2. 执行lint检查（强制，不通过则阻断）
    result = run_sdd_structure_lint(
        level=lint_level,
        change_id=current_change_id,
        path=f"docs/changes/{current_change_id}"
    )
    
    if not result.passed:
        # 阻断：不转换状态，返回错误报告
        update_state_json({
            "state": current_state,  # 保持原状态
            "blocked_reason": result.errors,
            "last_check": "failed"
        })
        return PhaseGateResult(
            success=False,
            errors=result.errors,
            next_state=None  # 不推进
        )
    
    # 3. 通过：更新状态并推进
    update_state_json({
        "state": next_state,
        "last_check": "passed",
        "updated_at": now()
    })
    
    return PhaseGateResult(success=True, next_state=next_state)
```

---

## 使用方式

### 启动新变更

```
用户：用SDD流程做用户登录功能

编排器：
1. 判定流程级别：Standard
2. 创建 changes/006-user-login/ 目录
3. 初始化 .sdd-state.json: { state: "IDLE", ... }
4. 状态转换：IDLE → PO_ENTRY
5. 调用 delegate_task 委托 po-agent
   - goal: "产出PRD文档..."
   - context: { change_id: "006-user-login", description: "用户登录功能" }
6. 等待po-agent完成
7. 状态转换：PO_ENTRY → PO_CHECK（执行L1 lint）
8. lint通过 → PO_DONE
9. 等待用户确认...
```

### 用户确认指令

| 当前状态 | 用户指令 | 动作 |
|---------|---------|------|
| `PO_DONE` | "继续"/"下一步" | → `BA_ENTRY` |
| `BA_DONE` | "继续"/"下一步" | → `ARCHITECT_ENTRY` |
| `ARCHITECT_DONE` | "开始编码" | → `CODER_ENTRY` |
| `USER_ACCEPT` | "归档" | → `ARCHIVE_ENTRY` |
| 任意等待状态 | "状态" | 输出当前状态和产物 |
| 任意状态 | "中断" | 保存状态，可恢复 |

### 恢复中断

```
用户：恢复SDD流程

编排器：
1. 读取 .sdd-state.json
2. 检测 current_state
3. 若 state 为 EXECUTING 状态 → 重新委托对应agent
4. 若 state 为 WAITING 状态 → 等待用户指令
5. 若 state 为 BLOCKED → 显示阻断原因
```

---

## Common Pitfalls

1. **跳过门禁检查**：编排器必须强制执行lint，不能依赖agent自律
2. **状态不同步**：每次状态转换必须立即更新 `.sdd-state.json`
3. **委托上下文不全**：delegate_task的context必须包含完整的前置产物路径
4. **用户确认缺失**：PO_DONE/BA_DONE/ARCHITECT_DONE/USER_ACCEPT必须等待用户确认
5. **恢复状态错误**：恢复时要重新检查当前状态产物是否存在，不存在则回退
6. **增量模式状态复杂**：Phase级状态需要额外维护 sub_phase_status

---

## References

- [state-machine.md](./references/state-machine.md) — 完整状态机定义
- [phase-gates.md](./references/phase-gates.md) — 门禁检查详细规范
- [delegate-protocol.md](./references/delegate-protocol.md) — Agent委托协议
- [incremental-mode.md](./references/incremental-mode.md) — 增量交付模式
- [interrupt-recovery.md](./references/interrupt-recovery.md) — 中断恢复机制
