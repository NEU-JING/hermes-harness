# Spec — SDD Orchestrator v2.0 重构

> **变更ID**: 006-orchestrator-v2  
> **日期**: 2026-05-30

---

## 需求清单

### R1: 状态机定义

系统必须定义严格的18状态机，每个状态有明确的类型和转换规则。

**AC1.1**: 状态类型分类
- **Given** 状态机初始化
- **When** 加载状态定义
- **Then** 状态必须分为: INITIAL(1), EXECUTING(6), GATE(6), WAITING(4), TERMINAL(2)

**AC1.2**: 状态转换合法性
- **Given** 当前状态为 X
- **When** 尝试转换到 Y
- **Then** 若 Y 不在 X 的 transitions 列表中，必须拒绝转换

### R2: 门禁检查

系统必须在状态转换时强制执行对应级别的lint检查。

**AC2.1**: L0初始化检查
- **Given** IDLE → PO_ENTRY 转换
- **When** 执行门禁
- **Then** 必须检查: 目录已创建, .sdd-state.json 已初始化

**AC2.2**: L1基础产物检查
- **Given** PO_ENTRY → PO_CHECK 或 BA_ENTRY → BA_CHECK
- **When** 执行门禁
- **Then** 必须检查产物文件存在且非空

**AC2.3**: L2设计产物检查
- **Given** ARCHITECT_ENTRY → ARCHITECT_CHECK
- **When** 执行门禁
- **Then** 必须检查: design.md 存在, tasks.md 存在, 格式正确

**AC2.4**: L2.5代码产物检查
- **Given** CODER_ENTRY → CODER_CHECK
- **When** 执行门禁
- **Then** 必须检查: completion-report.md 存在, commits 存在

**AC2.5**: L3报告质量检查
- **Given** REVIEWER_ENTRY → REVIEWER_CHECK 或 QA_ENTRY → QA_CHECK
- **When** 执行门禁
- **Then** 必须检查报告文件存在，结论明确

**AC2.6**: R10归档检查
- **Given** ARCHIVE_ENTRY → DONE
- **When** 执行门禁
- **Then** 必须检查: 当前分支为 main, 有 PR merge 记录

**AC2.7**: 门禁失败阻断
- **Given** 任意门禁检查
- **When** 检查不通过
- **Then** 必须阻断状态转换，保持在当前状态，输出错误

### R3: Agent委托协议

系统必须使用 delegate_task 调用各阶段agent。

**AC3.1**: PO阶段委托
- **Given** 状态为 PO_ENTRY
- **When** 执行阶段
- **Then** 必须调用 delegate_task(skill='po-agent', goal='产出PRD', ...)

**AC3.2**: BA阶段委托
- **Given** 状态为 BA_ENTRY
- **When** 执行阶段
- **Then** 必须调用 delegate_task(skill='ba-agent', inputs=['prd.md'], ...)

**AC3.3**: Architect阶段委托
- **Given** 状态为 ARCHITECT_ENTRY
- **When** 执行阶段
- **Then** 必须调用 delegate_task(skill='architect-agent', inputs=['spec.md'], ...)

**AC3.4**: Coder阶段委托
- **Given** 状态为 CODER_ENTRY
- **When** 执行阶段
- **Then** 必须按Tasks逐个调用 delegate_task(skill='coder-agent', ...)

**AC3.5**: Reviewer阶段委托
- **Given** 状态为 REVIEWER_ENTRY
- **When** 执行阶段
- **Then** 必须调用 delegate_task(skill='reviewer-agent', inputs=[...], ...)

**AC3.6**: QA阶段委托
- **Given** 状态为 QA_ENTRY
- **When** 执行阶段
- **Then** 必须调用 delegate_task(skill='qa-agent', inputs=[...], ...)

### R4: 状态自动推进

系统必须根据产物存在性和lint结果自动推进状态。

**AC4.1**: EXECUTING→GATE自动推进
- **Given** EXECUTING状态(agent完成)
- **When** 检测到产物存在
- **Then** 自动转换到对应 CHECK 状态

**AC4.2**: GATE通过自动推进
- **Given** GATE状态(lint通过)
- **When** 检查通过
- **Then** 自动转换到下一状态(DONE或WAITING)

**AC4.3**: WAITING等待用户确认
- **Given** WAITING状态
- **When** 未收到用户确认
- **Then** 保持状态，不自动推进

### R5: 中断恢复

系统必须支持从任意状态恢复。

**AC5.1**: 状态文件持久化
- **Given** 任意状态转换
- **When** 转换完成
- **Then** 必须立即更新 .sdd-state.json

**AC5.2**: 恢复检测
- **Given** 用户发起恢复
- **When** 扫描 changes/ 目录
- **Then** 必须找到所有进行中的变更(current_state ≠ DONE/BLOCKED)

**AC5.3**: 执行中状态恢复
- **Given** 恢复时状态为 EXECUTING
- **When** 检查产物完整性
- **Then** 产物完整→推进到CHECK，不完整→重新委托agent

**AC5.4**: 等待状态恢复
- **Given** 恢复时状态为 WAITING
- **When** 加载状态
- **Then** 输出用户提示，等待确认指令

### R6: 增量交付扩展

系统必须支持增量交付模式的Phase级子状态。

**AC6.1**: 增量模式检测
- **Given** tasks.md 中有 Phase 标记
- **When** 加载Architect产物
- **Then** 启用增量模式，状态机扩展Phase子状态

**AC6.2**: Phase依赖检查
- **Given** 进入 Phase N
- **When** 检查前置条件
- **Then** 必须验证所有依赖Phase状态为 accepted

**AC6.3**: Phase独立交付
- **Given** Phase N 完成QA
- **When** 用户验收
- **Then** 该Phase可独立交付，不阻塞其他Phase

### R7: Review失败回退

系统必须在Review失败时正确回退到Coder阶段。

**AC7.1**: Review失败回退
- **Given** REVIEWER_CHECK 状态
- **When** review结论为 failed
- **Then** 必须转换到 CODER_ENTRY，不清除已有产物

**AC7.2**: 连续失败熔断
- **Given** Reviewer连续2次失败
- **When** 第2次失败
- **Then** 必须转换到 BLOCKED 状态，等待用户决策

### R8: QA失败回退

系统必须在QA失败时正确回退到Coder阶段。

**AC8.1**: QA失败回退
- **Given** QA_CHECK 状态
- **When** qa结论为 failed
- **Then** 必须转换到 CODER_ENTRY

**AC8.2**: QA熔断
- **Given** QA连续4次失败
- **When** 第4次失败
- **Then** 必须转换到 BLOCKED 状态

---

## 数据契约

### .sdd-state.json Schema

```json
{
  "change_id": "string",
  "flow_level": "Quick|Standard|Enhanced",
  "current_state": "string",
  "previous_state": "string|null",
  "state_history": [
    {
      "from": "string",
      "to": "string",
      "at": "ISO8601",
      "trigger": "string",
      "auto": "boolean"
    }
  ],
  "lint_results": {
    "L1": {"passed": "boolean", "at": "ISO8601"},
    "L2": {...},
    "L2.5": {...},
    "L3": {...}
  },
  "incremental_mode": "boolean",
  "phase_config": "object|null",
  "started_at": "ISO8601",
  "updated_at": "ISO8601",
  "metadata": {
    "orchestrator_version": "string"
  }
}
```

---

## AC覆盖矩阵

| AC | 测试类型 | 优先级 |
|:---|:---|:---:|
| AC1.1-1.2 | 单元测试 | P0 |
| AC2.1-2.7 | 集成测试 | P0 |
| AC3.1-3.6 | 集成测试 | P0 |
| AC4.1-4.3 | 集成测试 | P1 |
| AC5.1-5.4 | 集成测试 | P1 |
| AC6.1-6.3 | 集成测试 | P1 |
| AC7.1-7.2 | 集成测试 | P0 |
| AC8.1-8.2 | 集成测试 | P0 |
