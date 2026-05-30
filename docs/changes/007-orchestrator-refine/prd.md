# PRD: SDD Orchestrator v2.0.1 优化

## 背景与目标

当前 sdd-orchestrator v2.0.0 存在两个问题：
1. **内容重复**：SKILL.md 与 references/ 目录下的文件内容大量重复，维护困难
2. **缺少显式 skill 声明**：delegate-protocol 未强制要求编排器显式声明使用哪个角色 agent 技能，可能导致 agent "跑偏"

## 目标用户

- Hermes Agent 开发者
- SDD 流程维护者

## 功能范围

| ID | 功能 | 优先级 | 说明 |
|---|---|---|---|
| F1 | 消除 SKILL.md 与 references/ 的内容重复 | P0 | SKILL.md 改为摘要+链接形式 |
| F2 | 显式声明 skill 使用 | P0 | delegate-protocol 强制使用 `skill_view(name='xxx-agent')` |
| F3 | 增加防跑偏机制说明 | P1 | 在委托前必须加载对应技能 |

## 非目标

- 不改变状态机逻辑
- 不改变门禁检查规则
- 不修改各角色 agent 技能本身

## 成功指标

- SKILL.md 行数减少 30%+
- 无重复内容（单点维护）
- delegate-protocol 每个阶段都有显式 `skill_view()` 调用示例

## 用户场景

**场景1：维护状态机定义**
作为开发者，我修改 state-machine.md，不需要同时修改 SKILL.md，避免不一致。

**场景2：委托 PO Agent**
作为编排器，我在委托前必须先 `skill_view(name='po-agent')`，确保使用正确的技能。
