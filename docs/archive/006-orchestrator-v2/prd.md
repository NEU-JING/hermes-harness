# PRD — SDD Orchestrator v2.0 重构

> **变更ID**: 006-orchestrator-v2  
> **日期**: 2026-05-30  
> **状态**: PRD阶段

---

## 背景与目标

### 问题陈述

当前 sdd-orchestrator v1.0 在实际应用中存在严重问题：

1. **流程描述不清晰**: 仅文字描述各阶段"应该做什么"，没有严格的ENTRY/EXIT条件
2. **门禁检查不强制**: lint检查是"建议性"而非"阻断性"，经常跳过检查继续执行
3. **未使用delegate调度**: 各阶段agent调用没有使用 `delegate_task`，而是口头描述
4. **流程易偏离**: 缺乏状态机控制，用户或agent可以随意跳过阶段
5. **中断恢复困难**: 没有标准状态文件，恢复时难以确定当前位置

这些问题导致编排器**没有起到流程管控作用**，SDD流程经常偏离规范。

### 目标

将 sdd-orchestrator 重构为 **v2.0 严格状态机编排器**，实现：

1. **严格状态机**: 18个精确定义的状态，每个状态有明确的ENTRY/EXIT条件
2. **强制门禁**: 5级lint检查，不通过则阻断转换
3. **delegate调度**: 明确定义6阶段的 `delegate_task` 调用协议
4. **自动推进**: 根据产物存在性和lint结果自动推进状态
5. **中断恢复**: 完整的 `.sdd-state.json` 机制，支持任意点恢复

---

## 目标用户

| 用户类型 | 需求 |
|---------|------|
| **SDD使用者** | 希望流程按规范执行，不被跳过阶段 |
| **Hermes Agent** | 需要清晰的指令，知道当前该做什么 |
| **项目维护者** | 需要可追溯的变更历史和状态 |

---

## 功能范围

| ID | 功能 | 优先级 | 说明 |
|:---|:---|:---:|:---|
| F1 | 严格状态机 | P0 | 18状态定义，ENTRY/EXIT明确 |
| F2 | 5级门禁检查 | P0 | L0-L3 + R10，强制阻断 |
| F3 | delegate协议 | P0 | 6阶段agent委托规范 |
| F4 | 自动状态推进 | P1 | 根据产物和lint自动推进 |
| F5 | 中断恢复 | P1 | .sdd-state.json完整恢复机制 |
| F6 | 增量交付扩展 | P1 | Phase级子状态支持 |

### 非目标

- 不修改其他skill（po-agent/ba-agent等保持原样）
- 不改变flow level判定逻辑
- 不增加新的skill角色

---

## 成功指标

| 指标 | 目标值 | 测量方式 |
|:---|:---:|:---|
| 阶段跳过率 | 0% | 检查状态历史，无非法转换 |
| 门禁通过率 | 100% | 所有归档变更必须通过L3 |
| 中断恢复成功率 | >95% | 随机中断测试恢复成功率 |
| delegate调用合规率 | 100% | 所有agent调用使用delegate_task |

---

## 用户场景

### 场景1: 启动新变更

```
用户: 用SDD流程做用户登录功能

编排器:
1. 判定流程级别: Standard
2. 创建 changes/007-user-login/ 目录
3. 初始化 .sdd-state.json: { state: "IDLE", ... }
4. 状态转换: IDLE → PO_ENTRY
5. 调用 delegate_task 委托 po-agent
6. 等待po-agent完成 → PO_CHECK → PO_DONE
7. 等待用户确认...

用户: 继续

编排器: 状态转换 PO_DONE → BA_ENTRY...
```

### 场景2: 门禁阻断

```
用户: 继续

编排器:
1. 当前状态: PO_DONE → BA_ENTRY → BA_CHECK
2. 执行L1+L2 lint检查
3. ❌ spec.md AC格式错误
4. ⛔ 门禁检查失败，转换阻断
5. 保持在 BA_ENTRY，返回错误报告

用户: 修复AC格式

编排器: 重新BA_CHECK → 通过 → BA_DONE
```

### 场景3: 中断恢复

```
[会话中断]

用户: 恢复SDD流程

编排器:
1. 读取 docs/changes/007-user-login/.sdd-state.json
2. 检测到 current_state: "ARCHITECT_DONE"
3. 检查产物: design.md ✅, tasks.md ✅
4. 输出: "从 ARCHITECT_DONE 恢复，请说'开始编码'继续"

用户: 开始编码

编排器: 状态转换 → CODER_ENTRY → 委托coder-agent
```

---

## 术语表

| 术语 | 说明 |
|:---|:---|
| **State** | 状态机中的一个节点，如 PO_ENTRY |
| **Transition** | 状态转换，需满足ENTRY条件和门禁检查 |
| **Gate** | 门禁检查点，如 L1/L2/L3 |
| **delegate** | 使用 delegate_task 调用其他skill |
| **.sdd-state.json** | 状态持久化文件 |

---

## 附录

### v1.0 vs v2.0 对比

| 维度 | v1.0 | v2.0 |
|:---|:---|:---|
| 状态定义 | 7个阶段（文字描述） | 18个状态（严格定义） |
| 门禁检查 | 建议性 | 强制性，阻断失败 |
| Agent调度 | 口头描述 | delegate_task协议 |
| 状态推进 | 人工 | 自动（产物+lint驱动） |
| 中断恢复 | 无 | 完整机制 |
| 增量交付 | 描述性 | 状态机扩展 |
