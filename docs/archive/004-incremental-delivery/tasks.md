# Tasks: SDD 增量交付支持

> **变更 ID**: 004-incremental-delivery  
> **前置文档**: [prd.md](./prd.md), [spec.md](./spec.md), [design.md](./design.md)  
> **版本**: 1.0  
> **日期**: 2026-05-30

---

## 执行约定

1. **工作目录**: `/root/workspace/hermes-harness`
2. **每 Task 完成后**: commit，格式 `feat({skill}): T{编号} {描述}`
3. **验证方式**: 手动验证（通过 mock 项目走完整流程）
4. **AC 覆盖检查**: 每个 Task 标注覆盖的 AC 编号

---

## Task 执行顺序

```
Phase 1: Schema 与状态管理（基础能力）
T1 → T2 → T3

Phase 2: Orchestrator 增强（核心调度）
T4 → T5 → T6

Phase 3: Agent 增强（Review/QA/Architect）
T7 → T8 → T9

Phase 4: 文档与验证
T10 → T11 → T12
```

---

## Phase 1: Schema 与状态管理 [可独立交付]

**交付标准**: Schema 定义完成，.sdd-state.json 扩展可用
**AC 覆盖**: AC1-AC3
**检查点**: 状态文件可正确读写 Phase 状态

---

### T1: 创建 .sdd-state.json Schema 文档
**估时**: 20m  
**依赖**: None  
**AC 覆盖**: AC1-AC3

**步骤**:
1. 创建 `skills/sdd/shared/sdd-state-schema.md`
2. 定义 `.sdd-state.json` 完整 schema（含 Phase 扩展）
3. 包含示例和字段说明
4. Commit: `feat(shared): T1 sdd-state schema with phase support`

**验证**:
```bash
# 检查文件存在
ls skills/sdd/shared/sdd-state-schema.md
```

---

### T2: 更新 sdd-structure-lint 支持 Phase 检查
**估时**: 30m  
**依赖**: T1  
**AC 覆盖**: AC4-AC6

**步骤**:
1. 读取 `skills/sdd/sdd-structure-lint/SKILL.md`
2. 增加 Level 2.5：Phase 结构检查
3. 增加 Phase 依赖检查逻辑
4. Commit: `feat(sdd-structure-lint): T2 phase structure lint`

**验证**:
```bash
# 检查 SKILL.md 已更新
grep -q "phase" skills/sdd/sdd-structure-lint/SKILL.md
```

---

### T3: 创建增量模式参考文档
**估时**: 30m  
**依赖**: T1  
**AC 覆盖**: AC11-AC14

**步骤**:
1. 创建 `skills/sdd/sdd-orchestrator/references/incremental-mode.md`
2. 详细说明增量模式的工作流程
3. 包含状态机图和示例
4. Commit: `feat(sdd-orchestrator): T3 incremental mode reference`

**验证**:
```bash
ls skills/sdd/sdd-orchestrator/references/incremental-mode.md
```

---

## Phase 2: Orchestrator 增强 [依赖 Phase 1]

**交付标准**: Orchestrator 支持 `--incremental` 和 Phase 调度
**AC 覆盖**: AC4-AC6, AC11-AC14
**检查点**: 可通过 `--incremental` 启动增量流程

---

### T4: 更新 sdd-orchestrator SKILL.md - Phase 状态管理
**估时**: 45m  
**依赖**: T3  
**AC 覆盖**: AC1-AC3, AC11-AC12

**步骤**:
1. 读取 `skills/sdd/sdd-orchestrator/SKILL.md`
2. 在 "门禁检查" 章节增加 Phase 状态检查
3. 在 "中断恢复" 章节增加 Phase 级别恢复
4. 更新 `.sdd-state.json` 示例（含 phase_status）
5. Commit: `feat(sdd-orchestrator): T4 phase state management`

**验证**:
```bash
grep -q "phase_status" skills/sdd/sdd-orchestrator/SKILL.md
grep -q "sub_phases_completed" skills/sdd/sdd-orchestrator/SKILL.md
```

---

### T5: 更新 sdd-orchestrator SKILL.md - 增量模式流程
**估时**: 45m  
**依赖**: T4  
**AC 覆盖**: AC11-AC14

**步骤**:
1. 在 "Phase 0: 流程判定" 章节增加 `--incremental` 判定逻辑
2. 增加 "Phase 调度（增量模式）" 章节
3. 增加 Phase 完成后用户确认流程
4. 更新流程图（支持增量模式）
5. Commit: `feat(sdd-orchestrator): T5 incremental mode workflow`

**验证**:
```bash
grep -q "incremental" skills/sdd/sdd-orchestrator/SKILL.md
grep -q "Phase 调度" skills/sdd/sdd-orchestrator/SKILL.md
```

---

### T6: 更新 sdd-orchestrator SKILL.md - Phase 门禁与触发
**估时**: 30m  
**依赖**: T5  
**AC 覆盖**: AC4-AC6

**步骤**:
1. 增加 Phase 门禁检查触发逻辑
2. 增加 Phase Review/QA 触发逻辑
3. 增加 Phase 完成后的状态更新
4. Commit: `feat(sdd-orchestrator): T6 phase gate and trigger`

**验证**:
```bash
grep -q "phase.*review" skills/sdd/sdd-orchestrator/SKILL.md
grep -q "phase.*qa" skills/sdd/sdd-orchestrator/SKILL.md
```

---

## Phase 3: Agent 增强 [依赖 Phase 2]

**交付标准**: Reviewer/QA/Architect 支持 Phase 视图
**AC 覆盖**: AC7-AC10, AC15-AC17
**检查点**: 各 Agent 可正确处理 Phase 级别任务

---

### T7: 更新 reviewer-agent SKILL.md - Phase Review 支持
**估时**: 30m  
**依赖**: T6  
**AC 覆盖**: AC7-AC8

**步骤**:
1. 读取 `skills/sdd/reviewer-agent/SKILL.md`
2. 增加 "Phase Review" 章节
3. 定义 PhaseReviewReport 结构
4. 增加 Phase 代码范围确定逻辑
5. 创建 `references/phase-review.md`
6. Commit: `feat(reviewer-agent): T7 phase review support`

**验证**:
```bash
grep -q "Phase Review" skills/sdd/reviewer-agent/SKILL.md
ls skills/sdd/reviewer-agent/references/phase-review.md
```

---

### T8: 更新 qa-agent SKILL.md - Phase QA + 回归测试
**估时**: 45m  
**依赖**: T6  
**AC 覆盖**: AC9-AC10

**步骤**:
1. 读取 `skills/sdd/qa-agent/SKILL.md`
2. 增加 "Phase QA" 章节
3. 定义 PhaseQAResult 结构
4. 增加回归测试逻辑（10% 抽样）
5. 创建 `references/phase-qa.md`
6. Commit: `feat(qa-agent): T8 phase qa with regression`

**验证**:
```bash
grep -q "Phase QA" skills/sdd/qa-agent/SKILL.md
grep -q "regression" skills/sdd/qa-agent/SKILL.md
ls skills/sdd/qa-agent/references/phase-qa.md
```

---

### T9: 更新 architect-agent SKILL.md - Tasks.md Phase 标记
**估时**: 30m  
**依赖**: None  
**AC 覆盖**: AC15-AC17

**步骤**:
1. 读取 `skills/sdd/architect-agent/SKILL.md`
2. 在 "Tasks 拆分" 章节增加 Phase 标记规范
3. 增加 Phase 交付标准模板
4. 增加 Phase 依赖声明示例
5. Commit: `feat(architect-agent): T9 tasks phase marking`

**验证**:
```bash
grep -q "可独立交付" skills/sdd/architect-agent/SKILL.md
grep -q "依赖 Phase" skills/sdd/architect-agent/SKILL.md
```

---

## Phase 4: 文档与验证 [依赖 Phase 3]

**交付标准**: 所有文档更新完成，增量模式可演示
**AC 覆盖**: 全量 AC 验证
**检查点**: 可完整走一遍 2-Phase 增量流程

---

### T10: 更新 README.md 说明增量模式
**估时**: 20m  
**依赖**: T5  
**AC 覆盖**: 文档

**步骤**:
1. 读取 `README.md`
2. 在 "SDD 流程" 章节增加增量模式说明
3. 增加增量流程图
4. 更新 "快速开始" 示例
5. Commit: `docs: T10 README incremental mode guide`

**验证**:
```bash
grep -q "增量" README.md
```

---

### T11: 更新 docs/current/ 基线文档
**估时**: 15m  
**依赖**: T10  
**AC 覆盖**: 文档

**步骤**:
1. 读取 `docs/current/README.md`
2. 更新 Skill 清单（新增/修改的 Skills）
3. 更新变更历史
4. Commit: `docs: T11 update current baseline`

**验证**:
```bash
grep -q "004-incremental-delivery" docs/current/README.md
```

---

### T12: 创建验证测试用例（Mock 项目）
**估时**: 30m  
**依赖**: T7, T8, T9, T11  
**AC 覆盖**: 全量 AC

**步骤**:
1. 创建 `examples/incremental-demo/` 目录
2. 创建 Mock PRD（含 2 个 Phase）
3. 创建 Mock Tasks.md（Phase 标记）
4. 编写验证脚本（模拟增量流程）
5. Commit: `test: T12 incremental mode demo`

**验证**:
```bash
ls examples/incremental-demo/
```

---

## 汇总

| Phase | Tasks | 估时 | AC 覆盖 |
|-------|-------|------|---------|
| Phase 1 | T1-T3 | 80m | AC1-AC3, AC4-AC6 |
| Phase 2 | T4-T6 | 120m | AC4-AC6, AC11-AC14 |
| Phase 3 | T7-T9 | 105m | AC7-AC10, AC15-AC17 |
| Phase 4 | T10-T12 | 65m | 文档 + 全量验证 |
| **总计** | **12** | **370m (~6h)** | **17 AC** |

---

## 增量交付检查点

### Phase 1 完成后检查
- [ ] `.sdd-state.json` Schema 文档完整
- [ ] `sdd-structure-lint` 支持 Phase 检查
- [ ] 增量模式参考文档可用

### Phase 2 完成后检查
- [ ] Orchestrator 支持 `--incremental`
- [ ] Phase 状态管理可用
- [ ] Phase 门禁检查可用

### Phase 3 完成后检查
- [ ] Reviewer Agent 支持 Phase Review
- [ ] QA Agent 支持 Phase QA + 回归测试
- [ ] Architect Agent 支持 Phase 标记

### Phase 4 完成后检查
- [ ] README 更新完成
- [ ] 基线文档更新完成
- [ ] Mock 项目验证通过
- [ ] 全量 17 AC 验证通过
