# Spec: SDD Orchestrator v2.0.1 优化

## 需求清单

### R1: SKILL.md 内容精简

**R1.1**: SKILL.md 的 State Machine 章节改为摘要形式
- **AC1.1**: State Machine 章节只保留概述和状态转换表
- **AC1.2**: 详细状态定义移除，添加链接指向 references/state-machine.md

**R1.2**: SKILL.md 的 Phase Gates 章节改为摘要形式
- **AC1.3**: Phase Gates 章节只保留 Level 概述
- **AC1.4**: 详细检查内容移除，添加链接指向 references/phase-gates.md

**R1.3**: SKILL.md 的 Agent Delegation 章节改为摘要形式
- **AC1.5**: Agent Delegation 章节只保留委托协议概述
- **AC1.6**: 各阶段委托详情移除，添加链接指向 references/delegate-protocol.md

### R2: 显式 Skill 声明

**R2.1**: delegate-protocol.md 每个阶段增加 skill_view() 强制步骤
- **AC2.1**: PO阶段委托前必须有 `skill_view(name='po-agent')`
- **AC2.2**: BA阶段委托前必须有 `skill_view(name='ba-agent')`
- **AC2.3**: Architect阶段委托前必须有 `skill_view(name='architect-agent')`
- **AC2.4**: Coder阶段委托前必须有 `skill_view(name='coder-agent')`
- **AC2.5**: Reviewer阶段委托前必须有 `skill_view(name='reviewer-agent')`
- **AC2.6**: QA阶段委托前必须有 `skill_view(name='qa-agent')`

**R2.2**: delegate-protocol.md 增加防跑偏说明
- **AC2.7**: 在"委托结果处理"章节前增加"前置检查"章节
- **AC2.8**: 前置检查要求：委托前必须通过 skill_view() 加载对应技能
- **AC2.9**: 前置检查失败时，阻断流程并提示用户

## 边界情况

- **B1**: 如果 skill_view() 加载失败（技能不存在），流程必须阻断
- **B2**: SKILL.md 精简后，必须确保所有 references/ 链接有效

## 数据契约

### 输出文件

| 文件 | 变更类型 | 说明 |
|---|---|---|
| `skills/sdd/sdd-orchestrator/SKILL.md` | 修改 | 精简内容 |
| `skills/sdd/sdd-orchestrator/references/delegate-protocol.md` | 修改 | 增加 skill_view() 要求 |
