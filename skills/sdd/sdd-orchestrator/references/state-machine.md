# SDD State Machine Definition

> **版本**: 2.0  
> **日期**: 2026-05-30

---

## 状态机概述

SDD编排器采用**严格状态机**驱动流程。每个状态有明确的：
- **Entry条件**：进入该状态的前提
- **Execution**：在该状态执行的操作
- **Exit条件**：离开该状态的条件
- **Transitions**：可能的下一状态

---

## 状态定义（Standard Flow）

### IDLE（初始状态）

```yaml
state: IDLE
type: initial
description: 流程未开始

entry_conditions:
  - 用户发起 "sdd start" 或 "用SDD流程做xxx"

execution: |
  1. 判定流程级别（Quick/Standard/Enhanced）
  2. 生成change_id
  3. 创建 docs/changes/{change_id}/ 目录
  4. 初始化 .sdd-state.json

exit_conditions:
  - 目录创建成功
  - 状态文件初始化完成

transitions:
  - to: PO_ENTRY
    trigger: 流程级别判定完成
    automatic: true
```

### PO_ENTRY（PO执行中）

```yaml
state: PO_ENTRY
type: executing
description: PO Agent正在执行

entry_conditions:
  - 前一状态: IDLE
  - .sdd-state.json 已创建

execution: |
  delegate_task:
    goal: "根据变更描述产出PRD"
    skill: po-agent
    deliverables:
      - prd.md

exit_conditions:
  - delegate_task 返回成功
  - prd.md 文件已创建

transitions:
  - to: PO_CHECK
    trigger: po-agent完成
    automatic: true
```

### PO_CHECK（PO门禁）

```yaml
state: PO_CHECK
type: gate
description: 检查PRD产物

entry_conditions:
  - 前一状态: PO_ENTRY
  - prd.md 存在

execution: |
  run_sdd_structure_lint(level="L1")
  检查:
    - prd.md 文件存在
    - 格式符合模板
    - 必填章节完整

exit_conditions:
  - lint 通过

blocking_conditions:
  - lint 不通过 → 返回 PO_ENTRY（修复）

transitions:
  - to: PO_DONE
    trigger: lint通过
    automatic: true
  - to: BLOCKED
    trigger: lint失败次数 > 3
```

### PO_DONE（等待用户确认）

```yaml
state: PO_DONE
type: waiting
description: 等待用户确认PRD

entry_conditions:
  - 前一状态: PO_CHECK
  - lint 通过

execution: |
  输出:
    "✅ PRD已完成: docs/changes/{change_id}/prd.md"
    "请确认PRD内容后说'继续'进入下一阶段"

exit_conditions:
  - 用户输入 "继续" 或 "下一步"

blocking_conditions:
  - 用户输入 "修改" → 返回 PO_ENTRY

transitions:
  - to: BA_ENTRY
    trigger: 用户说"继续"
    automatic: false  # 需要用户确认
```

### BA_ENTRY（BA执行中）

```yaml
state: BA_ENTRY
type: executing
description: BA Agent正在执行

entry_conditions:
  - 前一状态: PO_DONE
  - prd.md 存在（作为输入）

execution: |
  delegate_task:
    goal: "根据PRD产出Spec"
    skill: ba-agent
    inputs:
      - prd.md
    deliverables:
      - spec.md

exit_conditions:
  - delegate_task 返回成功
  - spec.md 已创建

transitions:
  - to: BA_CHECK
    trigger: ba-agent完成
    automatic: true
```

### BA_CHECK（BA门禁）

```yaml
state: BA_CHECK
type: gate
description: 检查Spec产物

entry_conditions:
  - 前一状态: BA_ENTRY
  - spec.md 存在

execution: |
  run_sdd_structure_lint(level="L2")
  检查:
    - spec.md 文件存在
    - AC格式正确（Given-When-Then）
    - 覆盖PRD所有功能点

transitions:
  - to: BA_DONE
    trigger: lint通过
    automatic: true
```

### BA_DONE（等待用户确认）

```yaml
state: BA_DONE
type: waiting
description: 等待用户确认Spec

entry_conditions:
  - 前一状态: BA_CHECK

exit_conditions:
  - 用户输入 "继续"

transitions:
  - to: ARCHITECT_ENTRY
    trigger: 用户说"继续"
    automatic: false
```

### ARCHITECT_ENTRY（Architect执行中）

```yaml
state: ARCHITECT_ENTRY
type: executing
description: Architect Agent正在执行

entry_conditions:
  - 前一状态: BA_DONE
  - spec.md 存在

execution: |
  delegate_task:
    goal: "根据Spec产出Design和Tasks"
    skill: architect-agent
    inputs:
      - spec.md
    deliverables:
      - design.md
      - tasks.md

exit_conditions:
  - delegate_task 返回成功
  - design.md + tasks.md 已创建

transitions:
  - to: ARCHITECT_CHECK
    trigger: architect-agent完成
    automatic: true
```

### ARCHITECT_CHECK（Architect门禁）

```yaml
state: ARCHITECT_CHECK
type: gate
description: 检查Design和Tasks产物

entry_conditions:
  - 前一状态: ARCHITECT_ENTRY
  - design.md + tasks.md 存在

execution: |
  run_sdd_structure_lint(level="L2")
  检查:
    - Design格式正确
    - Tasks拆分合理（可独立部署）
    - 增量模式有Phase标记

transitions:
  - to: ARCHITECT_DONE
    trigger: lint通过
    automatic: true
```

### ARCHITECT_DONE（等待用户确认）

```yaml
state: ARCHITECT_DONE
type: waiting
description: 等待用户确认Design后进入编码

entry_conditions:
  - 前一状态: ARCHITECT_CHECK

exit_conditions:
  - 用户输入 "开始编码"

blocking_conditions:
  - 用户输入 "调整设计" → 返回 ARCHITECT_ENTRY

transitions:
  - to: CODER_ENTRY
    trigger: 用户说"开始编码"
    automatic: false
```

### CODER_ENTRY（Coder执行中）

```yaml
state: CODER_ENTRY
type: executing
description: Coder Agent正在执行（按Tasks逐个实现）

entry_conditions:
  - 前一状态: ARCHITECT_DONE
  - tasks.md + design.md 存在
  - Git工作区clean

execution: |
  # 为每个Task调用coder-agent
  for task in tasks:
    delegate_task:
      goal: f"实现Task: {task.name}"
      skill: coder-agent
      inputs:
        - tasks.md (当前task)
        - design.md
      deliverables:
        - 代码commits
        - task完成报告

exit_conditions:
  - 所有tasks完成
  - completion-report.md 已创建

transitions:
  - to: CODER_CHECK
    trigger: 所有tasks完成
    automatic: true
```

### CODER_CHECK（Coder门禁）

```yaml
state: CODER_CHECK
type: gate
description: 检查代码和Task完成报告

entry_conditions:
  - 前一状态: CODER_ENTRY
  - completion-report.md 存在

execution: |
  run_sdd_structure_lint(level="L2.5")
  检查:
    - 所有Task有完成报告
    - 代码已提交到feature分支
    - 测试通过

transitions:
  - to: REVIEWER_ENTRY
    trigger: lint通过
    automatic: true
```

### REVIEWER_ENTRY（Reviewer执行中）

```yaml
state: REVIEWER_ENTRY
type: executing
description: Reviewer Agent正在执行

entry_conditions:
  - 前一状态: CODER_CHECK
  - 代码已提交
  - completion-report.md 存在

execution: |
  delegate_task:
    goal: "评审代码实现"
    skill: reviewer-agent
    inputs:
      - spec.md
      - design.md
      - completion-report.md
      - 代码commits
    deliverables:
      - review-report.md

exit_conditions:
  - delegate_task 返回成功
  - review-report.md 已创建

transitions:
  - to: REVIEWER_CHECK
    trigger: reviewer-agent完成
    automatic: true
```

### REVIEWER_CHECK（Reviewer门禁）

```yaml
state: REVIEWER_CHECK
type: gate
description: 检查评审结论

entry_conditions:
  - 前一状态: REVIEWER_ENTRY
  - review-report.md 存在

execution: |
  run_sdd_structure_lint(level="L3")
  解析 review-report.md:
    - 结论: passed / conditional / failed
    - CRITICAL问题数

exit_conditions:
  - 结论为 passed 或 conditional

blocking_conditions:
  - 结论为 failed → 返回 CODER_ENTRY（修复）
  - 连续2次failed → BLOCKED（需用户决策）

transitions:
  - to: QA_ENTRY
    trigger: review通过
    automatic: true
  - to: CODER_ENTRY
    trigger: review不通过
    automatic: true
```

### QA_ENTRY（QA执行中）

```yaml
state: QA_ENTRY
type: executing
description: QA Agent正在执行

entry_conditions:
  - 前一状态: REVIEWER_CHECK
  - review-report.md（通过）

execution: |
  delegate_task:
    goal: "执行测试验证"
    skill: qa-agent
    inputs:
      - spec.md
      - review-report.md
    deliverables:
      - qa-report.md

exit_conditions:
  - delegate_task 返回成功
  - qa-report.md 已创建

transitions:
  - to: QA_CHECK
    trigger: qa-agent完成
    automatic: true
```

### QA_CHECK（QA门禁）

```yaml
state: QA_CHECK
type: gate
description: 检查QA结论

entry_conditions:
  - 前一状态: QA_ENTRY
  - qa-report.md 存在

execution: |
  run_sdd_structure_lint(level="L3")
  解析 qa-report.md:
    - 结论: passed / failed
    - AC覆盖率

exit_conditions:
  - 结论为 passed

blocking_conditions:
  - 结论为 failed → 返回 CODER_ENTRY（修复）
  - 连续4次failed → BLOCKED（熔断）

transitions:
  - to: USER_ACCEPT
    trigger: qa通过
    automatic: true
  - to: CODER_ENTRY
    trigger: qa不通过
    automatic: true
```

### USER_ACCEPT（等待用户验收）

```yaml
state: USER_ACCEPT
type: waiting
description: 等待用户确认验收

entry_conditions:
  - 前一状态: QA_CHECK
  - qa-report.md（通过）

execution: |
  输出:
    "✅ QA已通过"
    "- AC覆盖: X/Y"
    "- 测试通过: X/Y"
    "说'归档'完成流程"

exit_conditions:
  - 用户输入 "归档"

transitions:
  - to: ARCHIVE_ENTRY
    trigger: 用户说"归档"
    automatic: false
```

### ARCHIVE_ENTRY（归档执行中）

```yaml
state: ARCHIVE_ENTRY
type: executing
description: 执行归档操作

entry_conditions:
  - 前一状态: USER_ACCEPT
  - 用户确认归档

execution: |
  1. R10检查（PR merged）
  2. 基线融合（current/更新）
  3. 移动 changes/ → archive/
  4. 清理 .sdd-state.json

exit_conditions:
  - 归档完成
  - current/ 已更新

transitions:
  - to: DONE
    trigger: 归档完成
    automatic: true
```

### DONE（完成）

```yaml
state: DONE
type: terminal
description: 流程完成

entry_conditions:
  - 前一状态: ARCHIVE_ENTRY
  - 归档完成

execution: |
  输出归档摘要

transitions: []  # 终止状态
```

### BLOCKED（阻断）

```yaml
state: BLOCKED
type: terminal
description: 流程阻断，需人工介入

entry_conditions:
  - 任意状态连续失败超过阈值
  - 或遇到无法自动恢复的错误

execution: |
  输出:
    - 阻断原因
    - 当前状态
    - 建议的恢复操作

transitions:
  - to: [任意状态]
    trigger: 用户手动恢复
    note: 需用户明确指令
```

---

## 状态转换表

| From | To | Trigger | Auto | Lint |
|:---|:---|:---|:---:|:---:|
| IDLE | PO_ENTRY | sdd start | ✅ | L1 |
| PO_ENTRY | PO_CHECK | po-agent完成 | ✅ | — |
| PO_CHECK | PO_DONE | L1通过 | ✅ | L1 |
| PO_DONE | BA_ENTRY | 用户说"继续" | ❌ | — |
| BA_ENTRY | BA_CHECK | ba-agent完成 | ✅ | — |
| BA_CHECK | BA_DONE | L2通过 | ✅ | L2 |
| BA_DONE | ARCHITECT_ENTRY | 用户说"继续" | ❌ | — |
| ARCHITECT_ENTRY | ARCHITECT_CHECK | architect完成 | ✅ | — |
| ARCHITECT_CHECK | ARCHITECT_DONE | L2通过 | ✅ | L2 |
| ARCHITECT_DONE | CODER_ENTRY | 用户说"开始编码" | ❌ | — |
| CODER_ENTRY | CODER_CHECK | 所有tasks完成 | ✅ | — |
| CODER_CHECK | REVIEWER_ENTRY | L2.5通过 | ✅ | L2.5 |
| REVIEWER_ENTRY | REVIEWER_CHECK | reviewer完成 | ✅ | — |
| REVIEWER_CHECK | QA_ENTRY | review通过 | ✅ | L3 |
| REVIEWER_CHECK | CODER_ENTRY | review不通过 | ✅ | — |
| QA_ENTRY | QA_CHECK | qa完成 | ✅ | — |
| QA_CHECK | USER_ACCEPT | qa通过 | ✅ | L3 |
| QA_CHECK | CODER_ENTRY | qa不通过 | ✅ | — |
| USER_ACCEPT | ARCHIVE_ENTRY | 用户说"归档" | ❌ | — |
| ARCHIVE_ENTRY | DONE | 归档完成 | ✅ | R10+L3 |

---

## 状态文件格式

```json
{
  "change_id": "006-user-login",
  "flow_level": "Standard",
  "current_state": "PO_DONE",
  "previous_state": "PO_CHECK",
  "state_history": [
    {"from": "IDLE", "to": "PO_ENTRY", "at": "2026-05-30T10:00:00Z"},
    {"from": "PO_ENTRY", "to": "PO_CHECK", "at": "2026-05-30T10:15:00Z"},
    {"from": "PO_CHECK", "to": "PO_DONE", "at": "2026-05-30T10:16:00Z"}
  ],
  "lint_results": {
    "L1": {"passed": true, "at": "2026-05-30T10:16:00Z"},
    "L2": null,
    "L3": null
  },
  "user_confirmations": [
    {"state": "PO_DONE", "confirmed_at": null, "waiting_since": "2026-05-30T10:16:00Z"}
  ],
  "incremental_mode": false,
  "started_at": "2026-05-30T10:00:00Z",
  "updated_at": "2026-05-30T10:16:00Z"
}
```
