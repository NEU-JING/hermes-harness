# Tasks — SDD Orchestrator v2.0 重构

> **变更ID**: 006-orchestrator-v2  
> **日期**: 2026-05-30

---

## Phase 1: SKILL.md重构

### T1: 重构SKILL.md主文档

**任务**: 重写 sdd-orchestrator/SKILL.md，定义严格状态机

**产出要求**:
- 定义18个状态（INITIAL/EXECUTING/GATE/WAITING/TERMINAL）
- 完整状态转换表
- 各阶段delegate_task调用规范
- 使用方式说明

**验收标准**:
- [ ] SKILL.md 包含完整状态机定义
- [ ] 每个状态有明确的ENTRY/EXIT条件
- [ ] 定义6个EXECUTING状态的delegate调用
- [ ] 版本号更新为 2.0.0

**依赖**: 无

---

## Phase 2: References完善

### T2: 创建state-machine.md

**任务**: 定义完整状态机

**产出要求**:
- 18状态的详细定义（YAML格式）
- 每个状态的ENTRY条件、EXECUTION、EXIT条件
- 状态转换表
- .sdd-state.json 格式定义

**验收标准**:
- [ ] 包含所有18个状态
- [ ] 每个状态类型正确
- [ ] 转换表完整

**依赖**: T1

### T3: 创建phase-gates.md

**任务**: 定义5级门禁检查

**产出要求**:
- L0-L3 + R10 检查内容
- 各级检查的执行流程
- 失败处理和阈值

**验收标准**:
- [ ] L0-L3检查内容明确
- [ ] R10检查逻辑
- [ ] 失败阈值定义（Reviewer 2次，QA 4次）

**依赖**: T1

### T4: 创建delegate-protocol.md

**任务**: 定义Agent委托协议

**产出要求**:
- 6阶段（PO/BA/Architect/Coder/Reviewer/QA）的delegate_task规范
- 每个阶段的context格式
- 委托结果处理

**验收标准**:
- [ ] 6个阶段都有delegate定义
- [ ] context包含所有必要输入
- [ ] 结果处理逻辑

**依赖**: T1

### T5: 创建interrupt-recovery.md

**任务**: 定义中断恢复机制

**产出要求**:
- 中断场景分析
- 状态文件格式
- 各状态类型的恢复策略
- 用户恢复指令

**验收标准**:
- [ ] 覆盖所有中断场景
- [ ] 恢复策略可行
- [ ] 示例完整

**依赖**: T2

---

## Phase 3: 现有References更新

### T6: 更新incremental-mode.md

**任务**: 与v2.0状态机对齐

**产出要求**:
- 增量模式作为状态机扩展
- Phase级子状态定义
- .sdd-state.json 增量模式扩展

**验收标准**:
- [ ] 与state-machine.md一致
- [ ] Phase状态流转清晰
- [ ] 数据格式正确

**依赖**: T2

### T7: 更新pr-and-review-flow.md

**任务**: 与v2.0状态机对齐

**产出要求**:
- Review在状态机中的位置
- Review结论处理（passed/conditional/failed）
- 失败回退机制

**验收标准**:
- [ ] Review结论映射到状态转换
- [ ] 失败回退逻辑
- [ ] 熔断机制

**依赖**: T1, T3

---

## Phase 4: 可执行脚本

### T8: 创建orchestrator.py

**任务**: 实现可执行状态机脚本

**产出要求**:
- State Enum定义
- SDDOrchestrator类
- CLI接口（start/resume/status/transition）
- lint检查执行
- delegate调用框架

**验收标准**:
- [ ] 18状态完整定义
- [ ] CLI命令可用
- [ ] 状态转换逻辑
- [ ] lint调用框架

**依赖**: T1, T2, T3, T4

---

## Phase 5: 部署与验证

### T9: 部署到本地Hermes

**任务**: 同步到~/.hermes/skills/sdd/

**产出要求**:
- rsync同步所有文件
- 验证文件完整性

**验收标准**:
- [ ] 所有文件同步
- [ ] 版本号正确

**依赖**: T1-T8

### T10: 补全SDD文档

**任务**: 创建006变更目录，产出PRD/Spec/Design/Tasks

**产出要求**:
- docs/changes/006-orchestrator-v2/ 目录
- prd.md, spec.md, design.md, tasks.md

**验收标准**:
- [ ] 4个文档完整
- [ ] 符合SDD格式

**依赖**: T9

---

## Task依赖图

```
T1 (SKILL.md)
  ├─> T2 (state-machine)
  │     ├─> T5 (interrupt-recovery)
  │     └─> T6 (incremental-mode)
  ├─> T3 (phase-gates)
  │     └─> T7 (pr-and-review-flow)
  ├─> T4 (delegate-protocol)
  │
  └─> T8 (orchestrator.py)
        └─> T9 (部署)
              └─> T10 (SDD文档)
```

---

## Phase交付标准

| Phase | 交付标准 | 可独立部署 |
|:-----:|:---|:---:|
| Phase 1 | SKILL.md v2.0完成 | ❌ (需references支撑) |
| Phase 2 | 4个references完成 | ❌ |
| Phase 3 | 2个references更新完成 | ❌ |
| Phase 4 | orchestrator.py可用 | ✅ (CLI可用) |
| Phase 5 | 完整SDD流程完成 | ✅ (可归档) |

---

## 变更完成标准

- [ ] 所有18状态定义完整
- [ ] 5级门禁检查可实现
- [ ] 6阶段delegate协议明确
- [ ] orchestrator.py可执行
- [ ] 本地Hermes已部署
- [ ] SDD文档完整

---

## 备注

**Phase标记**: 本变更使用Phase拆分，但最终需全部Phase完成才能归档。

**执行顺序**: T1 → (T2, T3, T4并行) → (T5, T6, T7并行) → T8 → T9 → T10

**实际执行**: T1-T8已完成（代码已实现），T9-T10为补SDD流程。
