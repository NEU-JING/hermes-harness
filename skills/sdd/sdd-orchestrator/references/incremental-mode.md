# 增量交付模式（Incremental Delivery Mode）

> **版本**: 2.0  
> **日期**: 2026-05-30  
> **对应状态机**: state-machine.md

---

## 概述

增量交付模式是 SDD 流程的扩展，允许大型变更按 **Phase（阶段）** 拆分，每个 Phase 独立经历 Review → QA → 验收。

**与状态机的关系**: 增量模式在 Standard 状态机基础上，扩展了 `CODER_ENTRY` / `REVIEWER_ENTRY` / `QA_ENTRY` 阶段的子状态。

---

## 启用条件

| 条件 | 说明 |
|------|------|
| 用户指定 | "用增量SDD流程做xxx" |
| Architect指定 | tasks.md 中有 Phase 标记 |
| 自动判定 | 变更涉及 3+ 模块，估时 > 2 周 |

---

## 增量模式状态机扩展

### 标准状态 vs 增量模式状态

```
Standard流程:
CODER_ENTRY → CODER_CHECK → REVIEWER_ENTRY → REVIEWER_CHECK → QA_ENTRY → QA_CHECK

增量模式流程:
CODER_ENTRY(Phase1) → CODER_CHECK(Phase1) → REVIEWER_ENTRY(Phase1) → REVIEWER_CHECK(Phase1)
                                                            ↓ (QA通过后)
                                          CODER_ENTRY(Phase2) → CODER_CHECK(Phase2) → ...
                                                            ↓
                                          CODER_ENTRY(Phase3) → ...
                                                            ↓
                                          USER_ACCEPT → ARCHIVE_ENTRY
```

### 增量模式专用状态

| 状态 | 类型 | 说明 |
|------|:---:|:---|
| `PHASE_N_CODER` | EXECUTING | Phase N 编码中 |
| `PHASE_N_CHECK` | GATE | Phase N 门禁检查 |
| `PHASE_N_REVIEW` | EXECUTING | Phase N 评审中 |
| `PHASE_N_QA` | EXECUTING | Phase N QA中 |
| `PHASE_N_DONE` | WAITING | Phase N 完成，等待进入下一Phase |

---

## .sdd-state.json 增量模式扩展

```json
{
  "change_id": "006-refactoring",
  "flow_level": "Standard",
  "current_state": "PHASE_2_CODER",
  "incremental_mode": true,
  
  "phase_config": {
    "total_phases": 3,
    "current_phase": "phase_2",
    "phases": {
      "phase_1": {
        "name": "数据层重构",
        "status": "accepted",
        "tasks": ["T1", "T2", "T3"],
        "ac_covered": ["AC1-AC8"],
        "completed_at": "2026-05-28T10:00:00Z"
      },
      "phase_2": {
        "name": "服务层重构",
        "status": "in_progress",
        "tasks": ["T4", "T5", "T6"],
        "ac_covered": ["AC9-AC15"],
        "depends_on": ["phase_1"]
      },
      "phase_3": {
        "name": "API层重构",
        "status": "not_started",
        "tasks": ["T7", "T8"],
        "ac_covered": ["AC16-AC20"],
        "depends_on": ["phase_1", "phase_2"]
      }
    }
  },
  
  "state_history": [...],
  "started_at": "2026-05-25T08:00:00Z",
  "updated_at": "2026-05-30T10:00:00Z"
}
```

---

## Phase 生命周期

### Phase 状态流转

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┴───┐
│  NOT_    │───▶│ PHASE_N_ │───▶│ PHASE_N_ │───▶│ PHASE_N_   │
│ STARTED  │    │  CODER   │    │  CHECK   │    │  REVIEW    │
└──────────┘    └──────────┘    └────┬─────┘    └─────┬──────┘
                                     │                │
                                     │         ┌──────┴──────┐
                                     │         ▼             │
                                     │    ┌──────────┐       │
                                     │    │PHASE_N_QA│       │
                                     │    └────┬─────┘       │
                                     │         │             │
                                     ▼         ▼             │
                              ┌──────────┐   ┌──────────┐   │
                              │PHASE_N_  │   │ NEXT     │───┘
                              │ ACCEPTED │   │ PHASE    │
                              └────┬─────┘   └──────────┘
                                   │
                                   ▼
                            ┌──────────┐
                            │ USER_    │
                            │ ACCEPT   │
                            └──────────┘
```

### Phase 状态定义

| 状态 | 说明 | 可进入下一Phase？ |
|------|------|:-----------------:|
| `not_started` | 未开始 | ❌ |
| `in_progress` | 编码中 | ❌ |
| `coding_done` | 编码完成 | ❌ |
| `review_failed` | 评审失败 | ❌（返回Coder） |
| `review_passed` | 评审通过 | ❌ |
| `qa_failed` | QA失败 | ❌（返回Coder） |
| `qa_passed` | QA通过 | ✅（需用户确认） |
| `accepted` | 用户验收 | ✅ |

---

## 增量模式委托规范

### Coder阶段委托（按Phase）

```yaml
delegate_task:
  goal: "实现 Phase {N} 的所有Tasks"
  
  context: |
    change_id: "{change_id}"
    phase_id: "phase_{N}"
    phase_name: "{phase_name}"
    
    ## 前置检查
    preconditions:
      - "依赖Phase已完成: {depends_on}"
    
    ## 当前Phase的Tasks
    tasks:
      - "T4: 重构用户服务"
      - "T5: 重构订单服务"
      - "T6: 添加服务测试"
    
    ## 产出
    deliverables:
      - type: "commits"
        branch: "feat/{change_id}-phase{N}"
      - file: "docs/changes/{change_id}/phase{N}-report.md"
  
  toolsets: ["file", "terminal", "skills"]
```

### Reviewer阶段委托（按Phase）

```yaml
delegate_task:
  goal: "评审 Phase {N} 的代码实现"
  
  context: |
    change_id: "{change_id}"
    phase_id: "phase_{N}"
    
    ## 检查范围
    scope:
      - "Phase {N} 相关文件"
      - "不检查前面Phase（假设已稳定）"
    
    ## 回归检查
    regression:
      - "抽样10%前面Phase的测试"
  
  toolsets: ["file", "terminal", "skills"]
```

---

## Phase 依赖检查

```python
def check_phase_dependencies(change_id, phase_id):
    """检查Phase依赖是否满足"""
    state = load_state(change_id)
    phase = state["phase_config"]["phases"][phase_id]
    
    for dep_phase_id in phase.get("depends_on", []):
        dep_phase = state["phase_config"]["phases"][dep_phase_id]
        if dep_phase["status"] != "accepted":
            return False, f"依赖Phase {dep_phase_id} 未完成"
    
    return True, None
```

---

## 回归测试策略

| Phase | 当前测试 | 回归测试 | 说明 |
|-------|:--------:|:--------:|------|
| Phase 1 | 100% | — | 基线Phase |
| Phase 2 | 100% | Phase 1 核心 10% | 验证不破坏Phase 1 |
| Phase 3 | 100% | Phase 1+2 核心 10% | 验证不破坏前面Phase |
| ... | ... | ... | ... |

**最终归档前**: 全量回归测试100%

---

## 与普通模式的区别

| 对比项 | Standard模式 | 增量模式 |
|--------|-------------|---------|
| Coder委托 | 一次性委托所有Tasks | 按Phase分批委托 |
| Review范围 | 全量代码 | 当前Phase代码 |
| QA范围 | 全量测试 | 当前Phase + 10%回归 |
| 用户确认 | 最终验收 | 每Phase验收 |
| 归档时机 | QA通过后 | 所有Phase验收后 |
| 状态机 | 标准状态 | 扩展Phase子状态 |

---

## 快速参考

```bash
# 启动增量模式
python orchestrator.py start "大型重构" --incremental

# 查看Phase状态
python orchestrator.py status {change_id} --phase

# 手动推进Phase
python orchestrator.py phase-next {change_id}
```
