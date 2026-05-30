# Design — SDD Orchestrator v2.0 重构

> **变更ID**: 006-orchestrator-v2  
> **日期**: 2026-05-30

---

## 架构决策

### 决策1: 严格状态机 vs 流程描述

**选项对比**:

| 方案 | 优点 | 缺点 |
|:---|:---|:---|
| A: 流程描述 (v1.0) | 灵活，易修改 | 执行不严格，易偏离 |
| B: 严格状态机 (v2.0) | 强制规范，可追溯 | 实现复杂 |

**选择**: B

**理由**: 编排器的核心职责是流程管控，必须强制执行。

### 决策2: 阻断式 vs 建议式门禁

**选项对比**:

| 方案 | 优点 | 缺点 |
|:---|:---|:---|
| A: 建议式 | 不阻塞流程 | 检查经常被跳过 |
| B: 阻断式 | 强制质量保证 | 可能增加等待 |

**选择**: B

**理由**: 宁可流程慢，也不让有问题的产物进入下一阶段。

### 决策3: delegate_task vs 直接调用

**选项对比**:

| 方案 | 优点 | 缺点 |
|:---|:---|:---|
| A: 直接调用函数 | 简单直接 | 无法利用subagent隔离 |
| B: delegate_task | 上下文隔离，可追踪 | 调用开销 |

**选择**: B

**理由**: delegate_task 提供标准化的agent调用协议，支持中断恢复。

---

## 状态机设计

### 状态定义

```python
class State(Enum):
    # 初始
    IDLE = ("IDLE", StateType.INITIAL)
    
    # 执行中 (自动推进)
    PO_ENTRY = ("PO_ENTRY", StateType.EXECUTING)
    BA_ENTRY = ("BA_ENTRY", StateType.EXECUTING)
    ARCHITECT_ENTRY = ("ARCHITECT_ENTRY", StateType.EXECUTING)
    CODER_ENTRY = ("CODER_ENTRY", StateType.EXECUTING)
    REVIEWER_ENTRY = ("REVIEWER_ENTRY", StateType.EXECUTING)
    QA_ENTRY = ("QA_ENTRY", StateType.EXECUTING)
    
    # 门禁 (检查通过后自动推进)
    PO_CHECK = ("PO_CHECK", StateType.GATE)
    BA_CHECK = ("BA_CHECK", StateType.GATE)
    ARCHITECT_CHECK = ("ARCHITECT_CHECK", StateType.GATE)
    CODER_CHECK = ("CODER_CHECK", StateType.GATE)
    REVIEWER_CHECK = ("REVIEWER_CHECK", StateType.GATE)
    QA_CHECK = ("QA_CHECK", StateType.GATE)
    
    # 等待 (需用户确认)
    PO_DONE = ("PO_DONE", StateType.WAITING)
    BA_DONE = ("BA_DONE", StateType.WAITING)
    ARCHITECT_DONE = ("ARCHITECT_DONE", StateType.WAITING)
    USER_ACCEPT = ("USER_ACCEPT", StateType.WAITING)
    
    # 终止
    DONE = ("DONE", StateType.TERMINAL)
    BLOCKED = ("BLOCKED", StateType.TERMINAL)
```

### 状态转换图

```
┌─────────┐    init     ┌─────────┐   lint L1   ┌─────────┐
│  IDLE   │ ──────────▶ │   PO    │ ──────────▶ │  PO_    │
└─────────┘             │ (entry) │             │ CHECK   │
                        └────┬────┘             └────┬────┘
                             │                        │
                             │ delegate po-agent      │ lint pass?
                             │ ◀──────────────────────┘
                             │ NO: retry
                             │ YES: proceed
                             ▼
                       ┌─────────┐    user     ┌─────────┐
                       │  PO_    │ ──────────▶ │   BA    │
                       │  DONE   │   confirm   │ (entry) │
                       └────┬────┘             └────┬────┘
                            │                       │
                            ▼                       ▼
                      [prd.md]               [lint + delegate
                                              ba-agent]

[后续状态同v1.0，但每个转换都有严格的lint检查]
```

### 转换规则表

| 当前状态 | 下一状态 | 触发条件 | 自动 | Lint |
|:---|:---|:---|:---:|:---:|
| IDLE | PO_ENTRY | sdd start | ✅ | L0 |
| PO_ENTRY | PO_CHECK | po-agent完成 | ✅ | — |
| PO_CHECK | PO_DONE | L1通过 | ✅ | L1 |
| PO_DONE | BA_ENTRY | 用户说"继续" | ❌ | — |
| ... | ... | ... | ... | ... |

完整转换表见: [references/state-machine.md](../references/state-machine.md)

---

## 数据流

### 1. 启动新变更

```
用户输入
    ↓
[编排器] determine_flow_level()
    ↓
生成 change_id
    ↓
创建 changes/{id}/ 目录
    ↓
初始化 .sdd-state.json {state: IDLE}
    ↓
状态转换: IDLE → PO_ENTRY
    ↓
delegate_task(skill='po-agent')
    ↓
等待完成 → PO_CHECK → PO_DONE
    ↓
等待用户确认...
```

### 2. 状态转换流程

```
当前状态 X
    ↓
检查转换合法性 (X → Y 是否在转换表)
    ↓
若是GATE状态 → 执行lint检查
    ↓
lint通过?
    ├─ 否 → 阻断，保持X
    └─ 是 → 继续
    ↓
更新 .sdd-state.json
    ↓
若是EXECUTING → delegate agent
若是WAITING → 提示用户
    ↓
完成
```

### 3. 中断恢复流程

```
用户: 恢复
    ↓
扫描 changes/*/ .sdd-state.json
    ↓
找到 current_state ≠ DONE/BLOCKED
    ↓
根据状态类型:
    ├─ EXECUTING → 检查产物 → 完整则推进CHECK，否则重委托
    ├─ WAITING → 输出提示等待用户
    ├─ GATE → 重新执行lint
    └─ 其他 → 报告异常
```

---

## 接口定义

### 编排器CLI

```bash
# 启动新变更
python orchestrator.py start "描述" [--quick|--enhanced]

# 恢复变更
python orchestrator.py resume [change_id]

# 查看状态
python orchestrator.py status [change_id]

# 手动状态转换（调试用）
python orchestrator.py transition <change_id> <target_state>
```

### Python API

```python
class SDDOrchestrator:
    def start(self, description: str, **flags) -> str:
        """启动新变更，返回change_id"""
        
    def resume(self, change_id: Optional[str] = None):
        """恢复中断的变更"""
        
    def transition(self, change_id: str, target_state: str) -> bool:
        """执行状态转换"""
        
    def execute_lint(self, level: str, change_id: str) -> Tuple[bool, List[str]]:
        """执行lint检查"""
```

---

## 产出物清单

### 新增文件

| 文件 | 类型 | 说明 |
|:---|:---|:---|
| `references/state-machine.md` | reference | 完整状态机定义 |
| `references/phase-gates.md` | reference | 5级门禁检查规范 |
| `references/delegate-protocol.md` | reference | Agent委托协议 |
| `references/interrupt-recovery.md` | reference | 中断恢复机制 |
| `scripts/orchestrator.py` | script | 可执行编排器 |

### 修改文件

| 文件 | 变更类型 | 说明 |
|:---|:---|:---|
| `SKILL.md` | 重写 | v2.0完整文档 |
| `references/incremental-mode.md` | 更新 | 与状态机对齐 |
| `references/pr-and-review-flow.md` | 更新 | 与状态机对齐 |

---

## 关键技术决策

| 决策 | 选择 | 理由 |
|:---|:---|:---|
| 状态持久化 | JSON文件 | 简单，人类可读，易于调试 |
| lint执行 | 外部脚本调用 | 可复用 sdd-structure-lint |
| delegate上下文 | YAML格式 | 结构化，易于扩展 |
| 失败重试 | 计数熔断 | 防止无限循环，保护资源 |

---

## 风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|:---|:---:|:---:|:---|
| 状态机过于严格 | 中 | 中 | 提供 `--force` 调试选项 |
| lint性能慢 | 低 | 中 | lint结果缓存 |
| 状态文件损坏 | 低 | 高 | 定期备份，校验JSON格式 |
| 并发变更冲突 | 低 | 中 | 每个变更独立目录 |

---

## 验证策略

| 验证项 | 方法 |
|:---|:---|
| 状态机完整性 | 单元测试: 所有状态都有合法转换 |
| 门禁强制 | 集成测试: lint失败时阻断转换 |
| delegate调用 | Mock测试: 验证delegate_task被调用 |
| 中断恢复 | 模拟测试: 随机kill后恢复 |
| 回归测试 | 现有5个归档变更可正常执行 |
