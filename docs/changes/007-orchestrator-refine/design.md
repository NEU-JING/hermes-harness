# Design: SDD Orchestrator v2.0.1 优化

## 架构决策

### 决策1: SKILL.md 精简策略

**选择**: 保留概述+链接，详细内容移至 references/

**理由**:
- 单点维护：状态机定义只在 state-machine.md 维护
- 减少 SKILL.md 体积，提高可读性
- 符合"SKILL.md 是入口，references/ 是详情"的设计

### 决策2: Skill 显式声明位置

**选择**: 在 delegate-protocol.md 的"前置检查"章节统一要求

**理由**:
- 每个阶段委托前执行，确保 agent 使用正确技能
- 集中管理，不分散在各阶段详情中
- 与 lint 检查类似，作为委托的前置条件

## 数据流

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│   SKILL.md  │───▶│  references/    │    │ delegate-   │
│  (精简版)   │    │  (详细定义)     │    │ protocol.md │
└─────────────┘    └─────────────────┘    └──────┬──────┘
      │                                          │
      │ 链接引用                                  │ 前置检查
      │                                          ▼
      │                               ┌─────────────────┐
      │                               │ skill_view()    │
      │                               │ 加载对应技能    │
      │                               └────────┬────────┘
      │                                        │
      └────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ delegate_task() │
                    │ 实际委托执行    │
                    └─────────────────┘
```

## 产出物清单

### 修改文件

1. **SKILL.md**: 精简 State Machine、Phase Gates、Agent Delegation 章节
2. **references/delegate-protocol.md**: 增加"前置检查"章节，要求 skill_view()

## 关键技术决策

### T1: 链接格式

使用相对路径链接，确保在 Hermes 技能系统中可解析：

```markdown
详细状态定义见 [state-machine.md](./references/state-machine.md)
```

### T2: Skill 加载失败处理

在 delegate-protocol.md 中定义失败处理流程：

```python
# 前置检查
skill_info = skill_view(name='po-agent')
if not skill_info.success:
    return DelegateResult(
        success=False,
        error=f"无法加载技能: po-agent",
        action="检查技能是否已安装"
    )
```
