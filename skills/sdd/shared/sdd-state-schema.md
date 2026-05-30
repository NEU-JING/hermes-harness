# .sdd-state.json Schema 定义

> **版本**: 1.1.0（支持增量交付）  
> **日期**: 2026-05-30

---

## 概述

`.sdd-state.json` 是 SDD 流程的状态文件，记录变更的当前阶段、已完成阶段、Phase 状态（增量模式）等信息。

**位置**: `docs/changes/{change_id}/.sdd-state.json`

---

## Schema 定义

### 根对象

```json
{
  "$schema": "sdd-state-v1.1",
  "type": "object",
  "required": ["change_id", "flow_level", "current_phase", "phases_completed"],
  "properties": {
    "change_id": { "type": "string" },
    "flow_level": { "enum": ["Quick", "Standard", "Enhanced"] },
    "current_phase": { "type": "string" },
    "current_sub_phase": { "type": "string" },
    "phases_completed": { "type": "array", "items": { "type": "string" } },
    "sub_phases_completed": { "type": "array", "items": { "type": "string" } },
    "phase_status": { "$ref": "#/definitions/PhaseStatusMap" },
    "incremental_mode": { "type": "boolean", "default": false },
    "started_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" }
  }
}
```

### PhaseStatusMap

```json
{
  "type": "object",
  "patternProperties": {
    "^phase_\\d+$": { "$ref": "#/definitions/PhaseStatus" }
  }
}
```

### PhaseStatus

```json
{
  "type": "object",
  "required": ["status", "ac_covered"],
  "properties": {
    "status": {
      "enum": [
        "not_started",
        "in_progress",
        "coding_done",
        "review_failed",
        "review_passed",
        "qa_failed",
        "qa_passed",
        "accepted"
      ]
    },
    "ac_covered": {
      "type": "array",
      "items": { "type": "string" }
    },
    "tasks_completed": {
      "type": "array",
      "items": { "type": "string" }
    },
    "test_count": { "type": "integer" },
    "review_status": {
      "enum": ["not_started", "in_progress", "passed", "failed", "conditional"]
    },
    "qa_status": {
      "enum": ["not_started", "in_progress", "passed", "failed", "conditional"]
    },
    "depends_on": {
      "type": "array",
      "items": { "type": "string" }
    },
    "completed_at": { "type": "string", "format": "date-time" }
  }
}
```

---

## 示例

### 示例 1：非增量模式（向后兼容）

```json
{
  "change_id": "[你的变更ID]",
  "flow_level": "Standard",
  "current_phase": "coder",
  "phases_completed": ["po", "ba", "architect"],
  "started_at": "2026-05-25T10:00:00Z",
  "updated_at": "2026-05-25T14:00:00Z"
}
```

### 示例 2：增量模式 - Phase 1 完成

```json
{
  "change_id": "[你的变更ID]",
  "flow_level": "Standard",
  "current_phase": "coder",
  "current_sub_phase": "phase_2_core_service",
  "phases_completed": ["po", "ba", "architect"],
  "sub_phases_completed": ["phase_1_data_layer"],
  "phase_status": {
    "phase_1": {
      "status": "qa_passed",
      "ac_covered": ["AC1-AC6", "AC7-AC14"],
      "tasks_completed": ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"],
      "test_count": 293,
      "review_status": "passed",
      "qa_status": "passed",
      "completed_at": "2026-05-30T10:00:00Z"
    },
    "phase_2": {
      "status": "in_progress",
      "ac_covered": ["AC15-AC21"],
      "tasks_completed": [],
      "depends_on": ["phase_1"]
    }
  },
  "incremental_mode": true,
  "started_at": "2026-05-28T08:00:00Z",
  "updated_at": "2026-05-30T10:00:00Z"
}
```

### 示例 3：增量模式 - Phase 2 Review 失败

```json
{
  "change_id": "[你的变更ID]",
  "flow_level": "Standard",
  "current_phase": "coder",
  "current_sub_phase": "phase_2_core_service",
  "phases_completed": ["po", "ba", "architect"],
  "sub_phases_completed": ["phase_1_data_layer"],
  "phase_status": {
    "phase_1": {
      "status": "qa_passed",
      "ac_covered": ["AC1-AC14"],
      "tasks_completed": ["T1-T10"],
      "test_count": 293,
      "review_status": "passed",
      "qa_status": "passed",
      "completed_at": "2026-05-30T10:00:00Z"
    },
    "phase_2": {
      "status": "review_failed",
      "ac_covered": ["AC15-AC21"],
      "tasks_completed": ["T11"],
      "review_status": "failed",
      "depends_on": ["phase_1"]
    }
  },
  "incremental_mode": true,
  "started_at": "2026-05-28T08:00:00Z",
  "updated_at": "2026-05-30T11:30:00Z"
}
```

---

## 字段说明

### 顶层字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `change_id` | string | ✅ | 变更唯一标识 |
| `flow_level` | enum | ✅ | 流程级别（Quick/Standard/Enhanced） |
| `current_phase` | string | ✅ | 当前 SDD 阶段（po/ba/architect/coder/reviewer/qa） |
| `current_sub_phase` | string | ❌ | 当前子 Phase（如 "phase_2_tutor"） |
| `phases_completed` | array | ✅ | 已完成的 SDD 阶段列表 |
| `sub_phases_completed` | array | ❌ | 已完成的子 Phase 列表 |
| `phase_status` | object | ❌ | 各 Phase 详细状态（增量模式） |
| `incremental_mode` | boolean | ❌ | 是否启用增量模式（默认 false） |
| `started_at` | string | ✅ | 变更开始时间（ISO 8601） |
| `updated_at` | string | ✅ | 最后更新时间（ISO 8601） |

### PhaseStatus 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `status` | enum | ✅ | Phase 当前状态 |
| `ac_covered` | array | ✅ | 该 Phase 覆盖的 AC 列表 |
| `tasks_completed` | array | ❌ | 已完成的 Task ID 列表 |
| `test_count` | integer | ❌ | 测试总数 |
| `review_status` | enum | ❌ | Review 状态 |
| `qa_status` | enum | ❌ | QA 状态 |
| `depends_on` | array | ❌ | 依赖的 Phase ID 列表 |
| `completed_at` | string | ❌ | 完成时间（ISO 8601） |

---

## Phase 状态枚举

| 状态值 | 说明 | 可进入下一 Phase？ |
|--------|------|:------------------:|
| `not_started` | 未开始 | ❌ |
| `in_progress` | 进行中（Coding） | ❌ |
| `coding_done` | Coding 完成，待 Review | ❌ |
| `review_failed` | Review 不通过 | ❌（返回 Coder） |
| `review_passed` | Review 通过，待 QA | ❌ |
| `qa_failed` | QA 不通过 | ❌（返回 Coder） |
| `qa_passed` | QA 通过（可交付） | ✅（需用户确认） |
| `accepted` | 用户验收通过 | ✅ |

---

## 向后兼容

- `incremental_mode` 默认为 `false`，非增量模式完全兼容
- `current_sub_phase`、`sub_phases_completed`、`phase_status` 为可选字段
- 旧状态文件无这些字段时，Orchestrator 自动初始化为非增量模式

---

## 验证规则

1. **Phase ID 格式**: 必须符合 `^phase_\d+$`（如 phase_1, phase_2）
2. **依赖检查**: 若 `phase_status[phase_N].depends_on` 包含 `phase_M`，则 `phase_M.status` 必须为 `qa_passed` 或 `accepted`
3. **时间顺序**: `completed_at` 必须在 `started_at` 之后
4. **状态一致性**: 若 `status` 为 `qa_passed`，则 `qa_status` 必须为 `passed`
