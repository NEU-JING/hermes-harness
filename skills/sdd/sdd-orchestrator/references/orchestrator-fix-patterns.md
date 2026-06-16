# orchestrator.py 实战修复模式

> 基于 2026-06-16 会话：Review 发现 6 个 CRITICAL 问题后的修复记录

---

## 修复速查表

### C1: 轮询机制（delegate_agent 末尾加 while 循环）

```python
def _poll_kanban_task(self, task_id, poll_interval=5, timeout=600):
    """轮询 Kanban 任务状态"""
    import subprocess, time
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = subprocess.run(
            ["hermes", "kanban", "list"],
            capture_output=True, text=True, timeout=15
        )
        for line in result.stdout.split("\n"):
            if task_id in line and "done" in line:
                return "done"
            if task_id in line and "blocked" in line:
                return "blocked"
        time.sleep(poll_interval)
    return "timeout"
```

在 `delegate_agent()` 中 `kanban create` 成功后，调用轮询：
```python
max_retries = 3
for attempt in range(max_retries):
    status = self._poll_kanban_task(task_id, poll_interval=5, timeout=600)
    if status == "done":
        # 自动 transition 到 CHECK 状态
        next_gate = {"PO_ENTRY": "PO_CHECK", "BA_ENTRY": "BA_CHECK", ...}
        self.transition(change_id, next_gate[state])
        return
    elif status == "blocked":
        # 3 次后标记 BLOCKED，记录状态历史
        state_data.current_state = "BLOCKED"
        self.save_state(change_id, state_data)
```

### C2: ROLE_TO_PROFILE_DEFAULT 对齐 AGENTS.md

```python
# ❌ 旧：3 个 Profile（sdd-flash/sdd-pro），与 AGENTS.md 不一致
ROLE_TO_PROFILE_DEFAULT = {
    "po": "sdd-flash", "ba": "sdd-flash", "architect": "sdd-pro",
    "coder": "sdd-pro", "reviewer": "sdd-reviewer", "qa": "sdd-flash",
}

# ✅ 新：6 个 Profile，完全对齐 AGENTS.md
ROLE_TO_PROFILE_DEFAULT = {
    "po": "sdd-po", "ba": "sdd-ba", "architect": "sdd-architect",
    "coder": "sdd-coder", "reviewer": "sdd-reviewer", "qa": "sdd-qa",
}
```

### C3: model_audit 审计功能

1. 给 `SDDState` 加字段：
```python
@dataclass
class SDDState:
    # ... 已有字段 ...
    model_audit: List[Dict] = field(default_factory=list)
```

2. 给 `StateHistoryEntry` 加 metadata：
```python
@dataclass
class StateHistoryEntry:
    # ... 已有字段 ...
    metadata: Dict = field(default_factory=dict)
```

3. 新增 `do_audit()` 方法和 `audit` CLI 子命令：
```python
def do_audit(self, change_id):
    state = self.load_state(change_id)
    # 输出模型使用审计报告
    # 列出每个阶段使用的模型和 Provider
    # 检测模型一致性（是否所有阶段用同一模型）
```

### C4: execute_lint 升级为内容质量检查

| Lint Level | 旧行为 | 新行为 |
|-----------|--------|--------|
| L1 | 只检查 prd.md 存在 | 正则匹配 PRD 必须包含的 5 大章节 |
| L1+L2 | 只检查 spec.md 存在 | 正则匹配 `#### Scenario AC\d+:` 和 `**WHEN**` 格式 |
| L2 | 只检查 design.md/tasks.md 存在 | 检查架构描述、接口定义、数据模型、任务拆分章节 |

```python
# L1 内容检查示例
import re
prd_content = prd_file.read_text()
required_sections = [
    (r'## 背景|## 背景与目标', "背景"),
    (r'## 用户场景|## 用例', "用户场景"),
    (r'## 功能范围|## In Scope', "功能范围"),
    (r'## 非功能需求|## NFR', "非功能需求"),
    (r'## 验收标准', "验收标准"),
]
for pattern, name in required_sections:
    if not re.search(pattern, prd_content):
        errors.append(f"PRD 缺少章节: {name}")
```

---

## 修复验证命令

```bash
# 语法检查
python3 -c "import py_compile; py_compile.compile('skills/sdd/sdd-orchestrator/scripts/orchestrator.py', doraise=True)"

# 状态查询
python3 skills/sdd/sdd-orchestrator/scripts/orchestrator.py status <change_id>

# 审计
python3 skills/sdd/sdd-orchestrator/scripts/orchestrator.py audit <change_id>
```
