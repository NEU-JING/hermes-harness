---
name: sdd-orchestrator
description: Central workflow orchestrator for SDD. Enforces strict phase gates, manages state machine transitions, and delegates to role agents via delegate_task.
version: 2.0.1
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

# SDD Orchestrator v2.0.1 — 严格状态机编排器

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

### 状态定义摘要

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

> **详细状态定义**见 [state-machine.md](./references/state-machine.md)

---

## Agent Delegation（Agent委托）

编排器使用 `delegate_task` 调用各角色Agent。**委托前必须先通过 `skill_view()` 加载对应技能**，避免 agent 跑偏。

### 基础委托格式

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

### 委托流程

```python
# 1. 前置检查：加载对应技能
skill_info = skill_view(name='po-agent')  # 根据阶段替换
if not skill_info.success:
    return DelegateResult(success=False, error="技能加载失败")

# 2. 执行委托
result = delegate_task(
    goal="...",
    context={...},
    toolsets=["file", "terminal", "skills"]
)

# 3. 处理结果
if result.success:
    update_state_json({"state": next_state})
else:
    handle_delegate_failure(result)
```

> **各阶段详细委托规范**见 [delegate-protocol.md](./references/delegate-protocol.md)

---

## Phase Gates（阶段门禁）

每个状态转换必须通过对应Level的lint检查。

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
            "state": current_state,
            "blocked_reason": result.errors,
            "last_check": "failed"
        })
        return PhaseGateResult(success=False, errors=result.errors)
    
    # 3. 通过：更新状态并推进
    update_state_json({
        "state": next_state,
        "last_check": "passed",
        "updated_at": now()
    })
    
    return PhaseGateResult(success=True, next_state=next_state)
```

> **详细门禁检查规范**见 [phase-gates.md](./references/phase-gates.md)

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
5. 调用 skill_view(name='po-agent') 加载技能
6. 调用 delegate_task 委托 po-agent
7. 等待po-agent完成
8. 状态转换：PO_ENTRY → PO_CHECK（执行L1 lint）
9. lint通过 → PO_DONE
10. 等待用户确认...
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

---

## Common Pitfalls

1. **跳过门禁检查**：编排器必须强制执行lint，不能依赖agent自律
2. **状态不同步**：每次状态转换必须立即更新 `.sdd-state.json`
3. **委托上下文不全**：delegate_task的context必须包含完整的前置产物路径
4. **用户确认缺失**：PO_DONE/BA_DONE/ARCHITECT_DONE/USER_ACCEPT必须等待用户确认
5. **未加载技能**：委托前必须通过 `skill_view()` 加载对应技能，防止agent跑偏
6. **恢复状态错误**：恢复时要重新检查当前状态产物是否存在，不存在则回退
7. **增量模式状态复杂**：Phase级状态需要额外维护 sub_phase_status

---

## Integration Notes (Hermes集成说明)

### orchestrator.py与Hermes工具的集成

`scripts/orchestrator.py` 是独立的可执行脚本，**需与Hermes工具集成**才能完整工作：

| 功能 | orchestrator.py实现 | 需Hermes集成 |
|:---|:---|:---:|
| 状态机管理 | 完整实现 | ❌ |
| 状态持久化 | 完整实现 | ❌ |
| CLI接口 | 完整实现 | ❌ |
| **lint检查执行** | 框架（检查文件存在） | ✅ 需调用 `sdd-structure-lint` |
| **Agent委托** | 框架（打印说明） | ✅ 需调用 `delegate_task` |
| **技能加载** | 无 | ✅ 需调用 `skill_view()` |

### 集成方式

**方式1: 纯脚本模式（调试/测试）**
```bash
python scripts/orchestrator.py start "变更描述"
# 手动按输出指示执行各阶段
```

**方式2: Hermes集成模式（生产）**
```python
# 在Hermes skill中使用
from hermes_tools import delegate_task, skill_view

# 调用编排器获取当前状态
state = orchestrator.load_state(change_id)

# 根据状态委托agent（必须先加载技能）
if state.current_state == "PO_ENTRY":
    # 1. 加载技能（防跑偏）
    skill_info = skill_view(name='po-agent')
    
    # 2. 执行委托
    result = delegate_task(
        goal="产出PRD",
        context={...}
    )
    
    # 3. 完成后推进状态
    orchestrator.transition(change_id, "PO_CHECK")
```

### lint检查集成

orchestrator.py中的 `execute_lint()` 需替换为：

```python
def execute_lint(self, level: str, change_id: str):
    # 调用 sdd-structure-lint skill
    skill_view(name='sdd-structure-lint')
    # 执行对应level的检查
    result = run_lint(level=level, path=change_dir)
    return result.passed, result.errors
```

---

## References

- [state-machine.md](./references/state-machine.md) — 完整状态机定义
- [phase-gates.md](./references/phase-gates.md) — 门禁检查详细规范
- [delegate-protocol.md](./references/delegate-protocol.md) — Agent委托协议（含 skill_view() 要求）
- [incremental-mode.md](./references/incremental-mode.md) — 增量交付模式
- [interrupt-recovery.md](./references/interrupt-recovery.md) — 中断恢复机制
