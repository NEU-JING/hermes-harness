# Design: SDD 增量交付支持

> **变更 ID**: 004-incremental-delivery  
> **版本**: 1.0  
> **日期**: 2026-05-30  
> **前置文档**: [prd.md](./prd.md), [spec.md](./spec.md)

---

## 一、Brainstorming（方案对比）

### 方案 A：Phase 内嵌套子 SDD 流程（推荐）

**思路**：保持顶层 SDD 流程不变，在每个 Phase 内增加 Mini Review + Mini QA。

```
PO → BA → Architect → [Phase 1 Coder → Phase 1 Review → Phase 1 QA] → 
                      [Phase 2 Coder → Phase 2 Review → Phase 2 QA] →
                      最终 Review → 最终 QA → 验收 → 归档
```

**优点**：
- 改动最小，向后兼容
- 保持 SDD 流程完整性
- 易于理解和实施

**缺点**：
- Review/QA 需要支持 Phase 视图
- 报告结构需要调整

### 方案 B：多变更 ID 拆分

**思路**：将每个 Phase 拆分为独立变更 ID。

```
002-ailp-v4-phase1 → 归档
003-ailp-v4-phase2 → 归档
004-ailp-v4-phase3 → 归档
```

**优点**：
- 完全遵循现有 SDD 流程
- 每个变更独立可追踪

**缺点**：
- 变更间依赖管理复杂
- 需要手动协调
- 基线文档碎片化

### 方案 C：Phase Manager Skill

**思路**：新增 `phase-manager` Skill，专门管理 Phase 生命周期。

**优点**：
- 职责分离清晰
- 可扩展性强

**缺点**：
- 增加系统复杂度
- 需要学习新 Skill

**选择**：方案 A（Phase 内嵌套子 SDD 流程）
- 理由：改动最小，向后兼容，符合 SDD 的渐进增强原则

---

## 二、架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      SDD Orchestrator                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Flow Level │  │   Phase     │  │      State Manager      │ │
│  │   Router    │  │   Router    │  │  (.sdd-state.json)      │ │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────────────┘ │
└─────────┼────────────────┼──────────────────────────────────────┘
          │                │
          ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Phase Lifecycle                          │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│  │  Coding  │───▶│  Review  │───▶│    QA    │───▶│ Accepted │ │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│       │               │               │               │        │
│       ▼               ▼               ▼               ▼        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│  │   TDD    │    │  Mini    │    │  Mini    │    │  User    │ │
│  │  Tasks   │    │  Review  │    │   QA     │    │ Confirm  │ │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 模块关系

| 模块 | 职责 | 依赖 |
|------|------|------|
| `sdd-orchestrator` | 流程判定、Phase 调度、状态管理 | 所有 Agent |
| `sdd-structure-lint` | Phase 门禁检查 | `sdd-orchestrator` |
| `reviewer-agent` | Phase Mini Review | `sdd-orchestrator` |
| `qa-agent` | Phase Mini QA + 回归测试 | `sdd-orchestrator` |
| `architect-agent` | Tasks.md Phase 标记 | `sdd-orchestrator` |

---

## 三、关键设计决策

### 决策 1：Phase 状态存储位置

| 选项 | 说明 | 选择 |
|------|------|:----:|
| A | `.sdd-state.json` 扩展 | ✅ |
| B | 独立 `phase-state.json` | |

**选择 A**：集中管理，减少文件数量，状态查询简单。

### 决策 2：Phase Review/QA 触发时机

| 选项 | 说明 | 选择 |
|------|------|:----:|
| A | Phase Coding 完成后自动触发 | ✅ |
| B | 用户手动触发 | |
| C | 最终 Review/QA 统一处理 | |

**选择 A**：符合增量交付理念，早期发现问题。

### 决策 3：回归测试范围

| 选项 | 说明 | 选择 |
|------|------|:----:|
| A | 前面所有 Phase 的核心测试（10% 抽样） | ✅ |
| B | 前面所有 Phase 的全量测试 | |
| C | 仅当前 Phase 测试 | |

**选择 A**：平衡效率与质量，避免测试时间过长。

### 决策 4：用户确认粒度

| 选项 | 说明 | 选择 |
|------|------|:----:|
| A | 每 Phase 完成后询问 | ✅ |
| B | 批量 Phase 完成后询问 | |
| C | 仅最终验收询问 | |

**选择 A**：给用户最大控制权，符合 SDD 门禁理念。

---

## 四、数据流

### 4.1 Phase 生命周期状态机

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

### 4.2 Phase 完成流程

```
Phase N Coding 完成
       │
       ▼
┌──────────────┐
│ Phase 门禁检查 │  ──▶  sdd-structure-lint Level 2
│ (依赖检查)     │  ──▶  检查 Phase N-1 是否 QA_PASSED
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Phase Review  │  ──▶  reviewer-agent (仅检查 Phase N 代码)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Phase QA      │  ──▶  qa-agent (Phase N 测试 + 前面 Phase 回归)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 用户确认      │  ──▶  "Phase N 完成，是否进入 Phase N+1?"
└──────┬───────┘
       │
       ▼
  更新 .sdd-state.json
       │
       ▼
  进入 Phase N+1 (或归档)
```

---

## 五、接口契约

### 5.1 Orchestrator → 各 Agent

| 调用方 | 被调用方 | 接口 | 数据格式 |
|--------|---------|------|---------|
| Orchestrator | sdd-structure-lint | `lint_phase(change_id, phase_id, level=2)` | LintResult |
| Orchestrator | reviewer-agent | `review_phase(change_id, phase_id)` | PhaseReviewReport |
| Orchestrator | qa-agent | `test_phase(change_id, phase_id, include_regression=True)` | PhaseQAResult |
| Orchestrator | architect-agent | `generate_tasks_with_phases(prd, spec)` | TasksWithPhases |

### 5.2 PhaseReviewReport 结构

```python
class PhaseReviewReport:
    phase_id: str                    # "phase_1"
    change_id: str                   # "002-ailp-v4-refactor"
    status: Literal["passed", "failed", "conditional"]
    ac_covered: List[str]            # ["AC1", "AC2", ...]
    issues: List[ReviewIssue]
    is_phase_deliverable: bool       # 是否可独立交付
    blockers_for_next_phase: List[str]
    completed_at: str                # ISO 8601
```

### 5.3 PhaseQAResult 结构

```python
class PhaseQAResult:
    phase_id: str
    change_id: str
    status: Literal["passed", "failed", "conditional"]
    test_summary: TestSummary        # 总测试数、通过数、失败数
    regression_tests: TestSummary    # 回归测试统计
    ac_coverage: float               # AC 覆盖度 (0.0-1.0)
    failed_acs: List[str]
    environment_constraints: List[str]
    is_deliverable: bool
```

---

## 六、产出物清单

### 6.1 新增文件

| 文件路径 | 说明 | 大小预估 |
|----------|------|---------|
| `skills/sdd/sdd-orchestrator/SKILL.md` | 更新：增加增量模式支持 | +100 行 |
| `skills/sdd/sdd-orchestrator/references/incremental-mode.md` | 新增：增量模式详细说明 | 200 行 |
| `skills/sdd/reviewer-agent/references/phase-review.md` | 新增：Phase Review 指南 | 150 行 |
| `skills/sdd/qa-agent/references/phase-qa.md` | 新增：Phase QA 指南 | 150 行 |

### 6.2 修改文件

| 文件路径 | 修改内容 |
|----------|----------|
| `skills/sdd/sdd-orchestrator/SKILL.md` | 增加 Phase 状态管理、增量模式流程 |
| `skills/sdd/architect-agent/SKILL.md` | 增加 tasks.md Phase 标记规范 |
| `skills/sdd/reviewer-agent/SKILL.md` | 增加 Phase Review 流程 |
| `skills/sdd/qa-agent/SKILL.md` | 增加 Phase QA + 回归测试 |
| `skills/sdd/shared/sdd-state-schema.md` | 新增：.sdd-state.json 完整 schema |

### 6.3 无需修改

- `skills/sdd/po-agent/SKILL.md` — PRD 无需感知 Phase
- `skills/sdd/ba-agent/SKILL.md` — Spec 无需感知 Phase
- `skills/sdd/coder-agent/SKILL.md` — Coder 只关注当前 Task

---

## 七、AC 覆盖矩阵

| 模块 | 负责 AC | 实现文件 |
|------|--------|---------|
| sdd-orchestrator | AC1-AC6, AC11-AC14 | SKILL.md + incremental-mode.md |
| reviewer-agent | AC7, AC8 | SKILL.md + phase-review.md |
| qa-agent | AC9, AC10 | SKILL.md + phase-qa.md |
| architect-agent | AC15-AC17 | SKILL.md |
| shared | Schema 定义 | sdd-state-schema.md |

---

## 八、风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| 向后兼容问题 | `.sdd-state.json` 中 `incremental_mode` 默认为 false，非增量模式完全不变 |
| Phase 间耦合 | Design 阶段强制检查 Phase 依赖，高耦合时警告 |
| 回归测试耗时 | 仅运行核心测试（10% 抽样），完整测试在最终 QA |
| 状态文件损坏 | 定期自动备份 `.sdd-state.json` 到 `.sdd-state.json.bak` |

---

## 九、验证策略

1. **单元测试**：每个 Skill 的 Phase 逻辑独立测试
2. **集成测试**：完整走一遍 2-Phase 的增量流程
3. **向后兼容测试**：验证非增量模式完全不受影响
4. **文档测试**：验证所有引用文档可访问
