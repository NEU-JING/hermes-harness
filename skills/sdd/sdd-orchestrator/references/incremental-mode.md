# 增量交付模式（Incremental Delivery Mode）

> **版本**: 1.0  
> **日期**: 2026-05-30

---

## 什么是增量交付模式？

增量交付模式是 SDD 流程的一种变体，允许大型变更按 **Phase（阶段）** 拆分，每个 Phase 独立经历 Review → QA → 验收，验证通过后再进入下一 Phase。

```
传统线性模式：
Design → All Coding → Review → QA → 验收 → 归档
              ↓
        问题发现晚，返工成本高

增量交付模式：
Phase 1 → Review → QA → 验收 → (可独立上线)
   ↓
Phase 2 → Review → QA → 验收 → (可独立上线)
   ↓
Phase 3 → Review → QA → 验收 → 归档
```

---

## 适用场景

| 场景 | 说明 |
|------|------|
| 大型系统重构 | 分阶段验证架构方向，降低风险 |
| 多模块并行开发 | 某模块延期不影响其他模块交付 |
| 快速验证核心功能 | 先交付 MVP，再逐步增强 |
| 需求不确定性高 | 早期交付获取反馈，及时调整 |

---

## Phase 生命周期

### 状态机

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┴───┐
│  NOT_    │───▶│   IN_    │───▶│ CODING_  │───▶│  REVIEW_   │
│ STARTED  │    │ PROGRESS │    │   DONE   │    │   PASSED   │
└──────────┘    └──────────┘    └────┬─────┘    └─────┬──────┘
                                     │                │
                                     │         ┌──────┴──────┐
                                     │         ▼             │
                                     │    ┌──────────┐       │
                                     │    │ REVIEW_  │───────┘
                                     │    │ FAILED   │
                                     │    └──────────┘
                                     │
                                     ▼
                              ┌──────────┐
                              │   QA_    │
                              │  PASSED  │
                              └────┬─────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
              ┌──────────┐   ┌──────────┐   ┌──────────┐
              │   QA_    │   │ ACCEPTED │   │  NEXT    │
              │  FAILED  │   │          │   │  PHASE   │
              └──────────┘   └──────────┘   └──────────┘
```

### 状态说明

| 状态 | 说明 | 可进入下一 Phase？ |
|------|------|:------------------:|
| `not_started` | 未开始 | ❌ |
| `in_progress` | 进行中（Coding） | ❌ |
| `coding_done` | Coding 完成，待 Review | ❌ |
| `review_failed` | Review 不通过 | ❌（返回 Coder） |
| `review_passed` | Review 通过，待 QA | ❌ |
| `qa_failed` | QA 不通过 | ❌（返回 Coder） |
| `qa_passed` | QA 通过（可交付） | ✅（需用户确认） |
| `accepted` | 用户验收通过 | ✅ |

---

## 启用增量模式

### 方式 1：用户明确指定

```
用户：用增量 SDD 流程做 AILP V4 重构

编排器输出：
🔍 流程判定: Standard (增量模式)
阶段: PO → BA → Architect → [Phase 1] → [Phase 2] → [Phase 3] → 归档
```

### 方式 2：Architect 指定

在 `tasks.md` 中明确标注 Phase：

```markdown
## Phase 1: 基础数据层 [可独立交付]
**交付标准**: Path + Radar API 全量测试通过

## Phase 2: 核心服务层 [依赖 Phase 1]
**交付标准**: Tutor + Certification API 测试通过

## Phase 3: 验证与执行 [依赖 Phase 1+2]
**交付标准**: Sandbox + Profile + Employer 测试通过
```

### 方式 3：命令行标志

```bash
# 启动增量模式
hermes sdd start "变更描述" --incremental

# 从指定 Phase 开始
hermes sdd resume "change-id" --phase=2
```

---

## .sdd-state.json 扩展

增量模式下，`.sdd-state.json` 包含 Phase 状态：

```json
{
  "change_id": "002-ailp-v4-refactor",
  "flow_level": "Standard",
  "current_phase": "coder",
  "current_sub_phase": "phase_2_tutor",
  "phases_completed": ["po", "ba", "architect"],
  "sub_phases_completed": ["phase_1_path_radar"],
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

详见 [sdd-state-schema.md](../shared/sdd-state-schema.md)。

---

## Phase 检查点

### 1. Phase 依赖检查

进入 Phase N 前，检查所有依赖 Phase 是否已完成 QA：

```
检查 Phase 2 依赖：
- phase_1.status = "qa_passed" ✅ 通过
- phase_1.review_status = "passed" ✅ 通过

结论：可以进入 Phase 2
```

### 2. Phase 门禁检查

Phase Coding 完成后，触发 Level 2.5 Phase 检查：

```
✓ Phase ID 格式正确
✓ 依赖已满足
✓ AC 覆盖非空
✓ Task 完成数匹配

结论：可以进入 Phase Review
```

### 3. Phase Review

Reviewer Agent 仅检查当前 Phase 的代码：

```
Phase 1 Review：
- 检查文件：models/path.py, models/radar.py, api/paths.py, api/radar.py
- 结论：passed
```

### 4. Phase QA

QA Agent 运行当前 Phase 测试 + 前面 Phase 回归测试：

```
Phase 2 QA：
- Phase 2 测试：50 个 ✅
- Phase 1 回归：29 个（10% 抽样）✅
- AC 覆盖：15/15 = 100%

结论：qa_passed
```

### 5. 用户确认

Phase QA 通过后，询问用户是否进入下一 Phase：

```
🎉 Phase 2 已完成！
- AC 覆盖：AC15-AC21（7 个）
- 测试通过：50/50
- 回归测试：29/29

是否进入 Phase 3？
[y] 是，进入 Phase 3
[n] 否，暂停在此
[b] 返回 Coder 修复
```

---

## 回归测试策略

为避免前面 Phase 被后面 Phase 破坏，每个 Phase QA 包含回归测试：

| Phase | 当前 Phase 测试 | 前面 Phase 回归 | 总测试数 |
|-------|-----------------|-----------------|---------|
| Phase 1 | 100% | — | 100% |
| Phase 2 | 100% | Phase 1 核心 10% | ~110% |
| Phase 3 | 100% | Phase 1+2 核心 10% | ~120% |

**注意**：最终归档前的 QA 仍会运行全量回归测试。

---

## 向后兼容

- `incremental_mode` 默认为 `false`
- 非增量模式下，所有 Phase 相关字段可选
- 旧状态文件自动兼容，无需迁移

---

## 常见问题

### Q1: 所有项目都应该用增量模式吗？

**不是**。增量模式适用于：
- 变更涉及 3+ 个独立模块
- 变更估时 > 2 周
- 需要早期验证核心功能

小型变更（< 1 周，单模块）使用标准模式更高效。

### Q2: Phase 拆分粒度如何确定？

**原则**：每个 Phase 可独立验收。

| 好的拆分 | 不好的拆分 |
|----------|-----------|
| Phase 1: 数据层 + 基础 API | Phase 1: 所有模型 |
| Phase 2: 业务服务层 | Phase 2: 所有服务 |
| Phase 3: 接入层 + 集成 | Phase 3: 所有 API |

### Q3: Phase 间出现循环依赖怎么办？

**Design 阶段必须解决**。若出现循环依赖，说明：
1. Phase 拆分不合理，需调整
2. 架构设计有缺陷，需重构

### Q4: 可以在 Phase 进行中调整 Tasks 吗？

**可以，但需重新 Review**。调整 Tasks 后：
1. 更新 `tasks.md`
2. 重新触发 Phase Review
3. QA 验证新 Tasks

---

## 最佳实践

1. **Design 阶段明确 Phase 边界** — 在 Design 文档中说明各 Phase 的职责和依赖
2. **Phase 1 尽量独立** — 降低后续 Phase 的风险
3. **每 Phase 完成后演示** — 给用户看成果，获取反馈
4. **保持 Phase 间松耦合** — 通过接口契约交互，避免直接依赖实现
5. **文档更新同步** — 每 Phase 完成后更新 `docs/current/README.md`
