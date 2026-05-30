# PRD: SDD 增量交付支持

> **变更 ID**: 004-incremental-delivery  
> **版本**: 1.0  
> **日期**: 2026-05-30  
> **状态**: Draft  

---

## 一、背景与目标

### 1.1 背景

当前 SDD 流程采用**线性瀑布模式**：
```
Design → All Tasks → All Coding → Review → QA → 验收 → 归档
```

这在大型重构项目中暴露出问题：
- **问题发现晚**：所有 Coding 完成后才进入 Review，问题累积
- **返工成本高**：一个模块的问题可能影响其他模块
- **用户反馈滞后**：无法早期验证核心架构是否正确
- **上线周期长**：必须等所有 Phase 完成才能交付

### 1.2 目标

为 SDD 流程增加**增量交付模式**，支持分 Phase 独立交付：
```
Phase 1 Coding → Review → QA → 验收 → (可独立上线)
      ↓
Phase 2 Coding → Review → QA → 验收 → (可独立上线)
      ↓
Phase 3 Coding → Review → QA → 验收 → (可独立上线)
```

---

## 二、用户与场景

### 2.1 目标用户

| 用户角色 | 场景 | 痛点 |
|---------|------|------|
| 产品经理 | 大型功能开发 | 无法早期看到成果，调整方向成本高 |
| Tech Lead | 系统重构 | 担心架构方向错误，想尽早验证 |
| 开发团队 | 多模块并行 | 某模块延期影响整体交付 |

### 2.2 典型场景

**场景 A：AILP V4 重构**
- Phase 1 (Path + Radar)：基础能力，可独立上线
- Phase 2 (Tutor + Certification)：核心服务，依赖 Phase 1
- Phase 3+ (Sandbox/Profile/Employer)：增值功能，依赖前面
- **增量交付价值**：Phase 1 完成即可给用户演示，确认方向正确后再投入 Phase 2

---

## 三、功能范围

### 3.1 In Scope（范围内）

1. **Phase 级状态追踪**
   - 支持在 `.sdd-state.json` 中记录各 Phase 完成状态
   - 支持 Phase 间依赖检查

2. **Phase 内嵌套 Review/QA**
   - 每完成一个 Phase，触发 Mini Review
   - 每完成一个 Phase，触发 Mini QA
   - 支持 Phase 回归测试（验证前面 Phase 无回归）

3. **Orchestrator 增强**
   - 新增 `--incremental` 流程标志
   - 支持 Phase 级门禁检查
   - 支持 Phase 完成后的用户确认

4. **Tasks.md Phase 标记**
   - 每个 Phase 增加交付标准说明
   - 每个 Phase 增加依赖声明

5. **Review/QA Report Phase 视图**
   - 支持按 Phase 生成评审报告
   - 明确标记 Phase 是否可独立交付

### 3.2 Out of Scope（范围外）

1. **自动上线部署** —— 仅支持交付标记，实际部署由外部 CI/CD 处理
2. **Phase 内并行开发** —— 一个 Phase 内的 Tasks 仍串行执行
3. **跨变更 ID 依赖** —— 依赖管理在单个变更 ID 内

---

## 四、功能需求

### FR1: Phase 级状态追踪

**需求描述**：`.sdd-state.json` 支持记录各 Phase 状态

**验收标准**：
- AC1: `.sdd-state.json` 包含 `phase_status` 字段，记录每个 Phase 的状态
- AC2: 支持 `sub_phases_completed` 数组，标记已完成的 Phase
- AC3: 支持 `current_sub_phase` 字段，标记当前正在执行的 Phase

### FR2: Phase 门禁检查

**需求描述**：每个 Phase 完成后触发门禁检查

**验收标准**：
- AC4: Phase 完成时自动调用 `sdd-structure-lint` Level 2 检查
- AC5: 支持 Phase 间依赖检查（Phase N 开始前检查 Phase N-1 是否已完成 Review+QA）
- AC6: Phase 检查失败时阻断进入下一 Phase

### FR3: Phase 内嵌套 Review/QA

**需求描述**：每个 Phase 完成后触发 Mini Review 和 Mini QA

**验收标准**：
- AC7: Phase 完成 Coding 后，自动触发 Phase Reviewer（检查该 Phase 的代码）
- AC8: Phase Review 通过后，自动触发 Phase QA（运行该 Phase 的测试）
- AC9: Phase QA 包含回归测试（验证前面所有 Phase 的测试仍通过）
- AC10: Phase Review/QA 报告合并到主 `review-report.md` 和 `qa-report.md`

### FR4: Orchestrator 增量模式

**需求描述**：Orchestrator 支持增量交付流程

**验收标准**：
- AC11: 支持 `--incremental` 标志启用增量模式
- AC12: 增量模式下，每完成一个 Phase 询问用户是否进入下一 Phase
- AC13: 增量模式下，每个 Phase 完成后更新基线文档（可选）
- AC14: 支持 `--phase=N` 标志从指定 Phase 开始

### FR5: Tasks.md Phase 增强

**需求描述**：`tasks.md` 支持 Phase 级元数据

**验收标准**：
- AC15: 每个 Phase 标题包含 `[可独立交付]` 或 `[依赖 Phase X]` 标记
- AC16: 每个 Phase 包含交付标准说明（测试通过数、AC 覆盖）
- AC17: 每个 Phase 包含检查点说明（Review/QA/用户确认）

---

## 五、非功能需求

### NFR1: 向后兼容
- 现有 SDD 流程（非增量模式）必须完全兼容
- 现有 `.sdd-state.json` 无 `phase_status` 时自动迁移

### NFR2: 性能
- Phase 门禁检查 < 5s
- Phase QA 回归测试只运行前面 Phase 的核心测试（< 30s）

### NFR3: 可维护性
- Phase 相关逻辑集中封装，不分散到各 Agent
- 新增 `phase-manager` 辅助 Skill（可选）

---

## 六、成功指标

| 指标 | 目标 | 测量方式 |
|------|------|---------|
| 早期问题发现率 | 50%+ 问题在 Phase 1 发现 | Review 报告问题分布 |
| Phase 独立交付率 | 100% Phase 1 可独立交付 | QA 报告验收结论 |
| 返工成本降低 | 相比线性模式降低 30% | 对比同类项目 |
| 用户满意度 | 用户明确认可增量模式 | 用户反馈 |

---

## 七、里程碑

| 里程碑 | 交付物 | 日期 |
|--------|--------|------|
| M1 | PRD + Spec 完成 | 2026-05-30 |
| M2 | Design + Tasks 完成 | 2026-05-30 |
| M3 | sdd-orchestrator 增强完成 | 2026-05-31 |
| M4 | Reviewer/QA Agent 增强完成 | 2026-05-31 |
| M5 | 文档更新 + 归档 | 2026-05-31 |

---

## 八、风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| Phase 间耦合比预期高 | 无法独立交付 | Design 阶段强制要求松耦合设计 |
| 回归测试时间过长 | 影响开发效率 | 仅运行核心测试，完整测试在最终 QA |
| 用户频繁切换上下文 | 降低效率 | Phase 批量确认，减少中断 |
