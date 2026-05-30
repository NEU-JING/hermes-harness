# Spec: SDD 增量交付支持

> **变更 ID**: 004-incremental-delivery  
> **版本**: 1.0  
> **日期**: 2026-05-30  
> **前置文档**: [prd.md](./prd.md)

---

## 一、AC 清单（21 条）

### Phase 状态追踪（AC1-AC3）

#### AC1: Phase 状态记录
**Given** 一个启用了增量模式的 SDD 变更  
**When** 用户完成 Phase 1 的 Coding  
**Then** `.sdd-state.json` 包含 `phase_status.phase_1.status = "completed"`  
**And** `phase_status.phase_1.ac_covered = ["AC1-AC6"]`  
**And** `phase_status.phase_1.completed_at` 记录时间戳

#### AC2: 已完成 Phase 追踪
**Given** 变更已完成 Phase 1 和 Phase 2  
**When** 查看 `.sdd-state.json`  
**Then** `sub_phases_completed = ["phase_1", "phase_2"]`  
**And** `current_sub_phase = "phase_3"`

#### AC3: Phase 依赖检查
**Given** Phase 2 依赖于 Phase 1  
**When** 用户尝试在未完成 Phase 1 Review 的情况下启动 Phase 2  
**Then** Orchestrator 阻断并提示："Phase 1 Review 未完成，请先完成 Phase 1"

---

### Phase 门禁检查（AC4-AC6）

#### AC4: Phase 结构检查
**Given** Phase 1 Coding 已完成  
**When** 进入 Phase 1 Review 前  
**Then** 自动调用 `sdd-structure-lint` Level 2 检查  
**And** 检查该 Phase 产出的文件完整性

#### AC5: Phase 依赖检查
**Given** Phase 2 配置依赖 Phase 1  
**When** 启动 Phase 2 Coder 前  
**Then** Orchestrator 检查 `phase_status.phase_1.status == "qa_passed"`  
**And** 若不满足则阻断

#### AC6: Phase 失败处理
**Given** Phase 1 Review 发现严重问题  
**When** Review 结论为 "不通过"  
**Then** `phase_status.phase_1.status = "review_failed"`  
**And** 阻断进入 Phase 2  
**And** 返回 Coder 修复

---

### Phase 内嵌套 Review/QA（AC7-AC10）

#### AC7: Phase Mini Review
**Given** Phase 1 Coding 完成  
**When** 进入 Phase 1 Review 阶段  
**Then** Reviewer Agent 仅检查 Phase 1 相关的代码变更  
**And** 产出 `review-report.md` 的 Phase 1 章节  

#### AC8: Phase Mini QA
**Given** Phase 1 Review 通过  
**When** 进入 Phase 1 QA 阶段  
**Then** QA Agent 运行 Phase 1 的测试用例  
**And** 产出 `qa-report.md` 的 Phase 1 章节

#### AC9: Phase 回归测试
**Given** Phase 2 QA 阶段  
**When** 运行测试时  
**Then** 先运行 Phase 1 的核心测试（10% 抽样或关键路径）  
**And** 再运行 Phase 2 的全量测试  
**And** Phase 1 测试失败则阻断

#### AC10: 报告合并
**Given** Phase 1 和 Phase 2 都已完成 QA  
**When** 查看 `qa-report.md`  
**Then** 包含 Phase 1 和 Phase 2 的独立章节  
**And** 包含汇总统计（总 AC 数、通过数、失败数）

---

### Orchestrator 增量模式（AC11-AC14）

#### AC11: 增量模式启用
**Given** 用户发起新变更  
**When** 用户说 "用增量 SDD 流程做 xxx" 或传入 `--incremental`  
**Then** Orchestrator 启用增量模式  
**And** 输出："🔍 流程判定: Standard (增量模式)"

#### AC12: Phase 完成确认
**Given** Phase 1 QA 通过  
**When** 准备进入 Phase 2 前  
**Then** Orchestrator 询问用户："Phase 1 已完成（AC1-AC6，6 个测试通过）。是否进入 Phase 2？"
**And** 用户确认后才继续

#### AC13: Phase 基线更新（可选）
**Given** Phase 1 验收通过  
**When** 用户启用 `--update-baseline-per-phase`  
**Then** 更新 `docs/current/README.md` 标记 Phase 1 已交付  
**And** 不影响最终归档

#### AC14: 指定 Phase 启动
**Given** 变更已完成 Phase 1  
**When** 用户说 "从 Phase 2 继续" 或传入 `--phase=2`  
**Then** Orchestrator 检查 Phase 1 已完成  
**And** 从 Phase 2 开始执行

---

### Tasks.md Phase 增强（AC15-AC17）

#### AC15: Phase 交付标记
**Given** Architect 产出 tasks.md  
**When** 使用增量模式  
**Then** 每个 Phase 标题包含交付标记：  
- `[可独立交付]` — 无依赖  
- `[依赖 Phase X]` — 有依赖

#### AC16: Phase 交付标准
**Given** Phase 1 标记为 `[可独立交付]`  
**When** 查看 tasks.md  
**Then** 包含交付标准：  
- 测试通过数：X 个  
- AC 覆盖：AC1-AC6  
- 检查点：Review + QA + 用户确认

#### AC17: Phase 检查点
**Given** Phase 2 标记为 `[依赖 Phase 1]`  
**When** 查看 tasks.md  
**Then** 明确列出检查点：  
- Phase 1 Review 通过  
- Phase 1 QA 通过  
- 用户确认进入 Phase 2

---

## 二、AC 覆盖矩阵

| 模块 | AC 范围 | 数量 | 说明 |
|------|--------|:----:|------|
| Phase 状态追踪 | AC1-AC3 | 3 | `.sdd-state.json` 扩展 |
| Phase 门禁检查 | AC4-AC6 | 3 | Orchestrator 增强 |
| Phase 内嵌套 Review/QA | AC7-AC10 | 4 | Reviewer/QA Agent 增强 |
| Orchestrator 增量模式 | AC11-AC14 | 4 | 流程控制增强 |
| Tasks.md Phase 增强 | AC15-AC17 | 3 | Architect Agent 增强 |
| **总计** | **AC1-AC17** | **17** | |

---

## 三、数据格式

### .sdd-state.json 扩展

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

### Phase 状态枚举

```python
class PhaseStatus:
    NOT_STARTED = "not_started"      # 未开始
    IN_PROGRESS = "in_progress"      # 进行中
    CODING_DONE = "coding_done"      # Coding 完成，待 Review
    REVIEW_FAILED = "review_failed"  # Review 不通过
    REVIEW_PASSED = "review_passed"  # Review 通过，待 QA
    QA_FAILED = "qa_failed"          # QA 不通过
    QA_PASSED = "qa_passed"          # QA 通过（可交付）
    ACCEPTED = "accepted"            # 用户验收通过
```

---

## 四、验收检查清单

### 开发前检查
- [ ] AC 覆盖度 100%（17/17）
- [ ] 数据格式定义完整
- [ ] 向后兼容方案确认

### 开发后检查
- [ ] 每个 AC 有对应测试
- [ ] 非增量模式完全兼容
- [ ] 文档更新完整
