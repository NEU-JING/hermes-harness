# 增量交付模式演示

> 演示 SDD 增量交付模式的工作流程

---

## 场景

假设一个电商系统重构项目，拆分为 3 个 Phase：

| Phase | 模块 | 依赖 | 交付标记 |
|-------|------|------|----------|
| Phase 1 | 用户系统 + 商品系统 | 无 | [可独立交付] |
| Phase 2 | 订单系统 + 支付系统 | Phase 1 | [依赖 Phase 1] |
| Phase 3 | 推荐系统 + 搜索系统 | Phase 1,2 | [依赖 Phase 1,2] |

---

## 启动增量模式

```bash
# 用户发起变更
用增量 SDD 流程做电商系统重构

# 编排器输出
🔍 流程判定: Standard (增量模式)
阶段: PO → BA → Architect → [Phase 1] → [Phase 2] → [Phase 3] → 归档
```

---

## Phase 1 执行

### 1. Architect 产出 tasks.md

```markdown
## Phase 1: 基础层 [可独立交付]
**交付标准**: 用户/商品 API 测试通过，AC1-AC10 验证完成
**AC 覆盖**: AC1-AC10

### T1: 用户模型
**文件**: `app/models/user.py`
**验证**: `pytest tests/test_user.py -v`

### T2: 商品模型
**文件**: `app/models/product.py`
**验证**: `pytest tests/test_product.py -v`

...

## Phase 2: 交易层 [依赖 Phase 1]
**交付标准**: 订单/支付 API 测试通过，AC11-AC20 验证完成
**AC 覆盖**: AC11-AC20
**依赖**: Phase 1 验收通过

...
```

### 2. Coder 执行 Phase 1 Tasks

```
T1 → T2 → T3 → ... → T10
Phase 1 Coding 完成
```

### 3. Phase 1 Review

```
范围: T1-T10 代码
结论: passed
问题: 0 Critical, 0 Major, 1 Minor
是否可交付: ✅ 是
```

### 4. Phase 1 QA

```
当前 Phase 测试: 50/50 ✅
回归测试: —（Phase 1 无前面 Phase）
AC 覆盖: 10/10 = 100%
结论: qa_passed
```

### 5. 用户确认

```
🎉 Phase 1 已完成！
- AC 覆盖：AC1-AC10（10 个）
- 测试通过：50/50

是否进入 Phase 2？
[y] 是，进入 Phase 2
[n] 否，暂停在此
```

---

## Phase 2 执行

### 依赖检查

```
检查 Phase 2 依赖：
- phase_1.status = "qa_passed" ✅

结论：可以进入 Phase 2
```

### 1. Coder 执行 Phase 2 Tasks

```
T11 → T12 → T13 → ... → T20
Phase 2 Coding 完成
```

### 2. Phase 2 Review

```
范围: T11-T20 代码
结论: passed
是否可交付: ✅ 是
```

### 3. Phase 2 QA

```
当前 Phase 测试: 60/60 ✅
回归测试: Phase 1 抽样 5/5 ✅
AC 覆盖: 10/10 = 100%
结论: qa_passed
```

### 4. 用户确认

```
🎉 Phase 2 已完成！
- AC 覆盖：AC11-AC20（10 个）
- 测试通过：60/60
- 回归测试：5/5

是否进入 Phase 3？
```

---

## .sdd-state.json 状态

```json
{
  "change_id": "005-ecommerce-refactor",
  "flow_level": "Standard",
  "current_phase": "coder",
  "current_sub_phase": "phase_3_recommendation",
  "phases_completed": ["po", "ba", "architect"],
  "sub_phases_completed": ["phase_1", "phase_2"],
  "phase_status": {
    "phase_1": {
      "status": "accepted",
      "ac_covered": ["AC1-AC10"],
      "tasks_completed": ["T1-T10"],
      "test_count": 50,
      "review_status": "passed",
      "qa_status": "passed",
      "completed_at": "2026-05-30T10:00:00Z"
    },
    "phase_2": {
      "status": "accepted",
      "ac_covered": ["AC11-AC20"],
      "tasks_completed": ["T11-T20"],
      "test_count": 60,
      "review_status": "passed",
      "qa_status": "passed",
      "completed_at": "2026-05-30T14:00:00Z"
    },
    "phase_3": {
      "status": "in_progress",
      "ac_covered": ["AC21-AC30"],
      "tasks_completed": [],
      "depends_on": ["phase_1", "phase_2"]
    }
  },
  "incremental_mode": true,
  "started_at": "2026-05-30T08:00:00Z",
  "updated_at": "2026-05-30T14:30:00Z"
}
```

---

## 优势对比

| 维度 | 线性模式 | 增量模式 |
|------|---------|---------|
| 问题发现 | 最后才发现 | 每 Phase 发现 |
| 返工成本 | 高（涉及全部） | 低（仅当前 Phase） |
| 上线时间 | 全部完成 | Phase 1 即可上线 |
| 用户反馈 | 滞后 | 及时 |
| 风险 | 集中 | 分散 |

---

## 验证检查清单

- [ ] Phase 依赖检查正确
- [ ] Phase Review 范围正确
- [ ] Phase QA 包含回归测试
- [ ] 用户确认流程可用
- [ ] 状态更新正确
