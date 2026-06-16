# SDD + Kanban Profile 调度集成指南

> **版本：v2.3.0**  
> **状态：✅ 推荐方案，零源码修改，100% 原生支持**  
> **更新：2026-06-17 — 6角色独立Profile + 异构评审模式**

---

## 核心发现

### ❌ 绝对不能用的方案：旧 profile 参数方式

**根本不存在！** `/usr/local/lib/hermes-agent/hermes_cli/delegate_tool.py` 源码中完全没有 `profile` 参数的处理逻辑。

- 旧版技能文档中描述的 Profile 委托机制**仅停留在设计层面**
- 相关函数签名根本没有 `profile` 参数
- 所有子 agent 始终共用同一个模型配置
- **即使源码改了也不能用**——用户明确禁止修改 Hermes 源码

### ✅ 真正有效的方案：Kanban + Profile（原生机制）

**代码证据**（`/usr/local/lib/hermes-agent/hermes_cli/kanban_db.py` 第 6406-6540 行）：

```python
def _default_spawn(task: Task, workspace: str, *, board: Optional[str] = None):
    # ...
    profile_arg = normalize_profile_name(task.assignee)
    # ...
    cmd = [
        *_resolve_hermes_argv(),
        "-p", profile_arg,   # ← 真实加载 Profile！
        "--accept-hooks",
    ]
    # ...
    if task.model_override:  # ← 甚至支持单任务模型覆盖！
        cmd.extend(["-m", task.model_override])
```

**工作原理**：
1. 创建任务时指定 `assignee: "<profile_name>"`
2. Gateway 调度器每 60s pick up 就绪任务
3. 调用 `hermes -p <profile_name> chat -q "work kanban task <id>"`
4. 每个 Profile 用自己的 `config.yaml`，天然用不同模型/Provider！

---

## 实施步骤（hermes-harness 标准模式）

### 第一步：验证模型可用性

配置前先确认 Provider 下确实有目标模型：

```bash
# 验证火山引擎可用模型
curl -H "Authorization: Bearer ***" \
  "https://ark.cn-beijing.volces.com/api/coding/v3/models" \
  | jq '.data[].id' | sort

# 验证 DeepSeek 可用模型
curl -H "Authorization: Bearer ***" \
  "https://api.deepseek.com/v1/models" \
  | jq '.data[].id' | sort
```

> ⚠️ **不要轻信文档或记忆**，尤其是火山引擎这类自定义 Provider，可用模型列表可能与预期不符。

### 第二步：创建 6 个独立 Profile（每角色一个）

**设计原则：每个 SDD 角色一个独立 Profile**
- Profile 创建几乎零开销（目录 + config.yaml）
- 每个角色独立调整模型、Provider、工具集
- 配置修改在下一次 spawn 时立即生效

#### `~/.hermes/profiles/sdd-po/config.yaml`（产品经理）
```yaml
# PO: 需求文档，多模态模型优先
model:
  default: doubao-seed-2.0-pro
  provider: custom
  base_url: https://ark.cn-beijing.volces.com/api/coding/v3
  api_key: ark-***********************-fcad8
skills:
  external_dirs:
    - /root/workspace/hermes-harness/skills
```

#### `~/.hermes/profiles/sdd-ba/config.yaml`（需求分析师）
```yaml
# BA: Spec 文档细化，推理适中
model:
  default: doubao-seed-2.0-pro
  provider: custom
  base_url: https://ark.cn-beijing.volces.com/api/coding/v3
  api_key: ark-***********************-fcad8
skills:
  external_dirs:
    - /root/workspace/hermes-harness/skills
```

#### `~/.hermes/profiles/sdd-architect/config.yaml`（架构师）
```yaml
# Architect: 系统设计，高推理需求
# TODO: 待 glm-5.1 端点确认后替换
model:
  default: doubao-seed-2.0-pro
  provider: custom
  base_url: https://ark.cn-beijing.volces.com/api/coding/v3
  api_key: ark-***********************-fcad8
skills:
  external_dirs:
    - /root/workspace/hermes-harness/skills
```

#### `~/.hermes/profiles/sdd-coder/config.yaml`（开发工程师）
```yaml
# Coder: 代码实现，专用编码模型
# TODO: 待代码专用模型端点确认后替换
model:
  default: doubao-seed-2.0-pro
  provider: custom
  base_url: https://ark.cn-beijing.volces.com/api/coding/v3
  api_key: ark-***********************-fcad8
skills:
  external_dirs:
    - /root/workspace/hermes-harness/skills
```

#### `~/.hermes/profiles/sdd-qa/config.yaml`（测试工程师）
```yaml
# QA: 测试验证，多模态模型优先
model:
  default: doubao-seed-2.0-pro
  provider: custom
  base_url: https://ark.cn-beijing.volces.com/api/coding/v3
  api_key: ark-***********************-fcad8
skills:
  external_dirs:
    - /root/workspace/hermes-harness/skills
```

#### `~/.hermes/profiles/sdd-reviewer/config.yaml`（评审专家）🔥 异构模式
```yaml
# Reviewer: 代码评审，完全独立 Provider
# ✅ 异构评审模式：用不同 Provider 消除模型偏见
model:
  default: deepseek-v4-pro
  provider: deepseek
  base_url: https://api.deepseek.com/v1
  api_key: sk-********************************************
skills:
  external_dirs:
    - /root/workspace/hermes-harness/skills
```

> **🔥 异构评审模式价值**：Reviewer 使用完全不同的 Provider（原生 DeepSeek），
> 而非与开发角色相同的火山引擎自定义 Provider。这样 Reviewer 不会因使用同一模型
> 而产生偏见，评审更客观独立，真正实现「第三方评审」。

### 第三步：在 AGENTS.md 中定义映射

```yaml
# AGENTS.md
sdd_config:
  profile_enabled: true   # 启用 Profile 模式
  
  # 角色 → Profile 映射
  role_to_profile:
    po: sdd-po
    ba: sdd-ba
    architect: sdd-architect
    coder: sdd-coder
    reviewer: sdd-reviewer
    qa: sdd-qa
```

### 第四步：修改 orchestrator.py 的 delegate_agent 方法

```python
def delegate_agent(self, change_id: str, state: State):
    """委托Agent执行任务（v2.3.0：Kanban + 独立 Profile）"""
    role = STATE_ROLE_MAP.get(state)
    
    # 从 AGENTS.md 读取 Profile 映射
    profile = self.get_profile_for_role(role)
    
    # 构建任务上下文
    context = self.build_delegate_context(change_id, state)
    
    # ✅ 使用 Kanban 创建任务 — 原生支持 Profile！
    # 调度器会自动：hermes -p <profile> chat -q "work kanban task XXX"
    result = subprocess.run(
        ["hermes", "kanban", "create",
         "--title", f"{change_id}: {role} 阶段",
         "--assignee", profile,  # ← 这里就是 Profile！
         "--body", context,      # 前置产物路径 + AC + 约束
         "--skills", f"sdd-{role}-agent"],
        capture_output=True, text=True
    )
    
    # 提取任务ID
    task_id = extract_task_id(result.stdout)
    
    # 保存任务ID到状态文件中，用于后续轮询
    self.update_state(change_id, {
        "kanban_task_id": task_id,
        "delegated_at": datetime.now().isoformat()
    })
```

### 第五步：启动 Gateway 调度器

```bash
hermes gateway start
```

调度器每 60s 自动：
1. 扫描 ready 状态的 Kanban 任务
2. 用任务的 `assignee` 作为 Profile 名称启动 worker
3. 每个 worker 读取自己 Profile 的 `config.yaml`，用对应模型执行

---

## 角色 → Profile → 模型映射表（v2.3.0）

| SDD 角色 | Profile | Provider | 模型 | 推理需求 |
|:--------:|:-------:|:--------:|:----:|:--------:|
| PO | `sdd-po` | 火山引擎 custom | doubao-seed-2.0-pro | 适中 |
| BA | `sdd-ba` | 火山引擎 custom | doubao-seed-2.0-pro | 适中 |
| Architect | `sdd-architect` | 火山引擎 custom | doubao-seed-2.0-pro* | 高 |
| Coder | `sdd-coder` | 火山引擎 custom | doubao-seed-2.0-pro* | 高 |
| **Reviewer** | **`sdd-reviewer`** | **原生 DeepSeek** | **deepseek-v4-pro** | 最高 |
| QA | `sdd-qa` | 火山引擎 custom | doubao-seed-2.0-pro | 适中 |

> *\* 占位模型，待 glm-5.1 和代码专用模型端点确认后替换*

---

## 轮询任务完成与状态机自动推进

```python
def poll_task_completion(self, task_id: str) -> Optional[bool]:
    """轮询任务完成状态"""
    result = subprocess.run(
        ["hermes", "kanban", "show", task_id],
        capture_output=True, text=True
    )
    status = extract_status(result.stdout)
    
    if status == "done":
        return True
    elif status in ["blocked", "failed"]:
        return False
    return None  # 进行中

def auto_advance(self, change_id: str):
    """任务完成后自动推进状态机"""
    state = self.load_state(change_id)
    
    if state.kanban_task_id:
        result = self.poll_task_completion(state.kanban_task_id)
        if result is True:
            # 任务完成：执行 lint 门禁 + 推进到下一状态
            next_state = self.get_next_state(state.current_state)
            lint_passed, errors = self.execute_lint(
                self.get_lint_level(state.current_state),
                change_id
            )
            if lint_passed:
                self.transition(change_id, next_state)
                # 如果下一状态需要委托，自动触发
                if next_state in NEEDS_DELEGATION:
                    self.delegate_agent(change_id, next_state)
        elif result is False:
            # 任务失败：标记为 BLOCKED
            self.update_state(change_id, {"state": "BLOCKED"})
```

---

## 为什么这个方案完美？

| 特性 | 说明 |
|:----:|:-----|
| **零源码修改** | 完全使用 Hermes 原生功能，不碰 `/usr/local/lib/hermes-agent/` |
| **升级兼容** | Hermes 升级不影响，Profile + Kanban 是官方稳定功能 |
| **真正隔离** | 每个 Profile 有独立的记忆、技能、配置目录 |
| **自动调度** | Gateway 后台运行，自动处理任务队列 |
| **可观测** | `hermes kanban list` 实时查看各阶段进度 |
| **模型灵活** | 每个 Profile 可以独立配置 model/provider/API key |
| **异构评审** | Reviewer 用不同 Provider，消除模型偏见 |
| **独立调优** | 每个角色可以单独优化模型选择，不影响其他 |

---

## 常见问题

### Q: Profile 目录已经存在但是空的？
A: 正常。`hermes profile create` 只创建目录结构，需要手动添加 `config.yaml`。

### Q: 调度器多久 pick up 一次任务？
A: 默认 60s，可通过 `kanban.dispatch_interval_seconds` 配置修改。

### Q: 可以在任务级别覆盖模型吗？
A: 可以！`kanban_create` 有 `model_override` 字段，优先级高于 Profile 配置。

### Q: 如何验证某个 Profile 在用正确的模型？
A: 查看 worker log：`hermes kanban log <task_id>`，日志头部会显示使用的模型。

### Q: 为什么 Reviewer 要用不同的 Provider？
A: 同一模型会产生"开发者视角偏见"。用完全不同的 Provider（如 DeepSeek vs. 火山引擎），
Reviewer 能从不同的训练数据分布出发，发现更多问题，评审真正独立客观。

### Q: 为什么不用共享 Profile（3个Profile配6角色）？
A: Profile 几乎零成本，独立 Profile 带来的灵活性远大于管理成本。
某个角色需要换模型时，只改自己的 config.yaml，不影响其他角色。
如果共享，改一个模型会影响多个角色，风险更高。
