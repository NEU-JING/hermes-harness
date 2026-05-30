# Interrupt Recovery Mechanism

> **版本**: 2.0  
> **日期**: 2026-05-30

---

## 中断场景

编排器可能因以下原因中断：

| 场景 | 原因 | 恢复方式 |
|------|------|---------|
| Agent重启 | 会话结束 | 自动检测状态文件，从当前状态恢复 |
| 用户中断 | 用户说"暂停" | 保存状态，等待用户指令 |
| 系统错误 | 工具失败 | 记录错误，转为BLOCKED状态 |
| 长时间运行 | 任务超时 | 保存进度，分片恢复 |

---

## 状态文件格式

### 完整状态文件

```json
{
  "change_id": "006-user-login",
  "flow_level": "Standard",
  "incremental_mode": false,
  
  "current_state": "CODER_ENTRY",
  "previous_state": "ARCHITECT_DONE",
  "state_history": [
    {
      "from": "IDLE",
      "to": "PO_ENTRY",
      "at": "2026-05-30T10:00:00Z",
      "trigger": "sdd_start",
      "auto": true
    },
    {
      "from": "PO_ENTRY",
      "to": "PO_CHECK",
      "at": "2026-05-30T10:15:00Z",
      "trigger": "po_agent_complete",
      "auto": true
    }
  ],
  
  "lint_results": {
    "L1": {
      "passed": true,
      "at": "2026-05-30T10:16:00Z",
      "duration_ms": 150
    },
    "L2": null,
    "L2.5": null,
    "L3": null
  },
  
  "user_confirmations": [
    {
      "state": "PO_DONE",
      "confirmed_at": "2026-05-30T10:20:00Z",
      "confirmed_by": "user_input"
    },
    {
      "state": "BA_DONE",
      "confirmed_at": "2026-05-30T10:45:00Z",
      "confirmed_by": "user_input"
    },
    {
      "state": "ARCHITECT_DONE",
      "confirmed_at": null,
      "waiting_since": "2026-05-30T11:00:00Z"
    }
  ],
  
  "agent_delegations": [
    {
      "phase": "PO",
      "delegated_at": "2026-05-30T10:00:00Z",
      "completed_at": "2026-05-30T10:15:00Z",
      "result": "success"
    },
    {
      "phase": "BA",
      "delegated_at": "2026-05-30T10:20:00Z",
      "completed_at": "2026-05-30T10:40:00Z",
      "result": "success"
    },
    {
      "phase": "ARCHITECT",
      "delegated_at": "2026-05-30T10:45:00Z",
      "completed_at": "2026-05-30T11:00:00Z",
      "result": "success"
    },
    {
      "phase": "CODER",
      "delegated_at": null,
      "completed_at": null,
      "result": null,
      "note": "中断前准备委托"
    }
  ],
  
  "failure_history": [],
  
  "metadata": {
    "orchestrator_version": "2.0.0",
    "hermes_session": "session_id",
    "last_heartbeat": "2026-05-30T11:00:00Z"
  },
  
  "started_at": "2026-05-30T10:00:00Z",
  "updated_at": "2026-05-30T11:00:00Z"
}
```

---

## 恢复流程

### 自动检测

```python
def detect_and_recover():
    """会话启动时自动检测并恢复"""
    
    # 1. 扫描所有变更目录
    changes_dirs = glob("docs/changes/*/")
    
    for change_dir in changes_dirs:
        state_file = f"{change_dir}/.sdd-state.json"
        
        if not os.path.exists(state_file):
            continue
        
        # 2. 读取状态
        state = load_json(state_file)
        
        # 3. 检查是否需要恢复
        if state["current_state"] in ["DONE", "BLOCKED"]:
            continue  # 已完成或阻断，无需恢复
        
        # 4. 执行恢复
        recover_change(state)
```

### 恢复决策

```python
def recover_change(state):
    """根据状态决定恢复策略"""
    
    current_state = state["current_state"]
    
    # 执行中状态 → 重新委托
    if is_executing_state(current_state):
        return recover_executing(state)
    
    # 等待状态 → 提示用户
    if is_waiting_state(current_state):
        return recover_waiting(state)
    
    # 门禁状态 → 重新检查
    if is_gate_state(current_state):
        return recover_gate(state)
    
    # 异常状态 → 报告
    return recover_abnormal(state)
```

### 各状态恢复策略

#### 执行中状态恢复

```python
def recover_executing(state):
    """PO_ENTRY, BA_ENTRY, ARCHITECT_ENTRY, CODER_ENTRY, REVIEWER_ENTRY, QA_ENTRY"""
    
    current = state["current_state"]
    change_id = state["change_id"]
    
    # 1. 检查之前的委托是否完成
    last_delegation = get_last_delegation(state)
    
    if last_delegation and last_delegation["completed_at"]:
        # 委托已完成但未推进状态（异常中断）
        output(f"检测到 {current} 已完成但未推进，继续门禁检查...")
        return transition_to_check(current, change_id)
    
    # 2. 检查产物是否存在
    deliverables = get_expected_deliverables(current, change_id)
    missing = [d for d in deliverables if not file_exists(d)]
    
    if not missing:
        # 产物已存在，可能是委托完成后的中断
        output(f"✅ 产物已存在，继续下一阶段...")
        return transition_to_check(current, change_id)
    
    # 3. 产物不完整，需要重新委托
    output(f"🔄 从 {current} 恢复，重新委托...")
    
    # 根据状态重新委托对应agent
    agent_map = {
        "PO_ENTRY": "po-agent",
        "BA_ENTRY": "ba-agent",
        "ARCHITECT_ENTRY": "architect-agent",
        "CODER_ENTRY": "coder-agent",
        "REVIEWER_ENTRY": "reviewer-agent",
        "QA_ENTRY": "qa-agent"
    }
    
    skill = agent_map[current]
    return delegate_to_agent(skill, state, resume=True)
```

#### 等待状态恢复

```python
def recover_waiting(state):
    """PO_DONE, BA_DONE, ARCHITECT_DONE, USER_ACCEPT"""
    
    current = state["current_state"]
    waiting_since = get_waiting_since(state, current)
    elapsed = now() - waiting_since
    
    output(f"""
🔄 检测到中断恢复
━━━━━━━━━━━━━━━━━━━━
变更: {state['change_id']}
当前状态: {current}
等待时长: {elapsed}

产物状态:
{format_deliverables_status(state)}

下一步:
{get_next_step_prompt(current)}
━━━━━━━━━━━━━━━━━━━━
请确认是否继续？
""")
    
    # 等待用户输入
    return wait_for_user_input(current)
```

#### 门禁状态恢复

```python
def recover_gate(state):
    """PO_CHECK, BA_CHECK, ARCHITECT_CHECK, CODER_CHECK, REVIEWER_CHECK, QA_CHECK"""
    
    current = state["current_state"]
    change_id = state["change_id"]
    
    output(f"🔄 从门禁状态 {current} 恢复，重新执行检查...")
    
    # 重新执行lint检查
    lint_level = get_lint_level_for_state(current)
    result = run_sdd_structure_lint(lint_level, change_id)
    
    if result.passed:
        # 检查通过，推进到下一状态
        next_state = get_next_state_after_gate(current)
        return execute_transition(current, next_state, change_id)
    else:
        # 检查不通过，保持当前状态并报告
        output(f"❌ 检查未通过，请修复后重试")
        output(result.errors)
        return stay_at_state(current)
```

#### 异常状态恢复

```python
def recover_abnormal(state):
    """BLOCKED或其他异常状态"""
    
    output(f"""
⚠️ 变更处于异常状态
━━━━━━━━━━━━━━━━━━━━
变更: {state['change_id']}
状态: {state['current_state']}
阻断原因: {state.get('blocked_reason', '未知')}

失败历史:
{format_failure_history(state)}

建议操作:
1. "恢复" — 尝试从当前状态继续
2. "回退到 {get_previous_executable_state(state)}" — 回退到可执行状态
3. "重置" — 重置状态机（会丢失进度）
━━━━━━━━━━━━━━━━━━━━
""")
    
    return wait_for_user_decision()
```

---

## 用户恢复指令

| 指令 | 作用 |
|------|------|
| `sdd resume` 或 "恢复SDD流程" | 自动检测并恢复最近的变更 |
| `sdd resume {change_id}` | 恢复指定变更 |
| `sdd status` 或 "查看SDD状态" | 显示所有进行中的变更状态 |
| `sdd abort {change_id}` | 放弃变更（删除changes/目录） |

---

## 恢复示例

### 场景1: PO阶段中断

```
用户: 恢复SDD流程

编排器:
🔄 检测到中断恢复
━━━━━━━━━━━━━━━━━━━━
变更: 006-user-login
当前状态: PO_ENTRY
等待时长: 2小时

产物状态:
❌ prd.md — 不存在（PO agent未完成）

下一步:
重新委托 po-agent 产出 PRD
━━━━━━━━━━━━━━━━━━━━

[自动执行]
→ delegate_task: po-agent
→ 产出 prd.md
→ 状态: PO_ENTRY → PO_CHECK → PO_DONE
→ 等待用户确认...
```

### 场景2: 等待用户确认时中断

```
用户: 恢复SDD流程

编排器:
🔄 检测到中断恢复
━━━━━━━━━━━━━━━━━━━━
变更: 006-user-login
当前状态: ARCHITECT_DONE
等待时长: 1天

产物状态:
✅ design.md — 存在
✅ tasks.md — 存在

下一步:
用户确认后进入 CODER_ENTRY 阶段
━━━━━━━━━━━━━━━━━━━━
请说"开始编码"继续
```

### 场景3: 编码阶段中断

```
用户: 恢复SDD流程

编排器:
🔄 检测到中断恢复
━━━━━━━━━━━━━━━━━━━━
变更: 006-user-login
当前状态: CODER_ENTRY

已完成的任务:
✅ T1: 用户模型定义
✅ T2: 登录API实现
⏳ T3: 密码加密（进行中）

下一步:
继续完成 T3 及后续任务
━━━━━━━━━━━━━━━━━━━━

[自动执行]
→ delegate_task: coder-agent (resume=T3)
→ 继续完成 T3
```

---

## 最佳实践

1. **频繁更新状态文件**: 每个状态转换后立即写入 `.sdd-state.json`
2. **产物原子性**: 每个agent的产物应完整写入后再推进状态
3. **失败快速记录**: 失败后立即更新状态文件，记录失败原因
4. **用户确认持久化**: 用户确认后立即写入状态文件，防止重复询问
5. **心跳机制**: 长时间运行的agent定期更新 `last_heartbeat`
