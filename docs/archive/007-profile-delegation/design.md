# Design — 007: SDD Orchestrator v2.1.0 Profile 委托集成方案

> **变更 ID**: `007-profile-delegation`
> **版本**: v1.0
> **创建时间**: 2026-05-31
> **前置文档**: [prd.md](./prd.md) | [spec.md](./spec.md)

---

## 1. 方案对比

### 1.1 方案 A：6 角色独立 Profile（每角色一个 Profile）

**核心思路**：每个 SDD 角色拥有一个独立 Hermes Profile，共 6 个 Profile。

```
Profile 矩阵：
┌─────────────┬──────────┬──────────┬───────────────────────────────┐
│ Profile      │ 角色     │ 模型     │ 预加载 Skills                  │
├─────────────┼──────────┼──────────┼───────────────────────────────┤
│ sdd-po       │ PO       │ flash    │ po-agent                      │
│ sdd-ba       │ BA       │ flash    │ ba-agent                      │
│ sdd-architect│ Architect│ pro      │ architect-agent               │
│ sdd-coder    │ Coder    │ pro      │ coder-agent, tdd, local-verif │
│ sdd-reviewer │ Reviewer │ pro      │ reviewer-agent, post-code-rev │
│ sdd-qa       │ QA       │ flash    │ qa-agent                      │
└─────────────┴──────────┴──────────┴───────────────────────────────┘
```

**优点**：
- ✅ 精细粒度控制：可为每个角色单独调整模型、工具集、Skills
- ✅ 角色隔离最彻底：PO 和 BA 完全独立，不会互相干扰
- ✅ 扩展灵活：新增第 7 个角色只需新增一个 Profile，不影响现有配置

**缺点**：
- ❌ Profile 数量多（6 个），用户创建和维护成本高
- ❌ 实际使用中 PO/BA/QA 配置完全相同（模型=flash，工具集=file,skills），产生了 3 个冗余 Profile
- ❌ Architect 和 Coder 配置高度相似（模型=pro，工具集=file,terminal,skills），区别仅在于预加载 Skills
- ❌ 升级命令需执行 6 次 `hermes profile create`，耗时且易出错
- ❌ 不符合原 PRD 中 "3 个 Profile 覆盖 6 个角色" 的设计意图

**复杂度评分**：创建 6/10 | 维护 7/10 | 用户体验 4/10

---

### 1.2 方案 B：3 Profile 角色分组（按工作负载分组）✅ 选定

**核心思路**：按角色工作负载特征将 6 个角色分为 3 组，每组共享一个 Profile。

```
Profile 矩阵：
┌──────────────┬────────────────┬──────────┬───────────────────────────────┐
│ Profile      │ 适用角色       │ 模型     │ 预加载 Skills                  │
├──────────────┼────────────────┼──────────┼───────────────────────────────┤
│ sdd-flash    │ PO, BA, QA     │ flash    │ po-agent, ba-agent, qa-agent   │
│ sdd-pro      │ Architect,Coder│ pro      │ architect-agent, coder-agent,   │
│              │                │          │ tdd, local-verifier             │
│ sdd-reviewer │ Reviewer       │ pro      │ reviewer-agent, post-code-rev   │
└──────────────┴────────────────┴──────────┴───────────────────────────────┘
```

**分组逻辑**：

| 分组 | 角色 | 共同特征 |
|:------|:-----|:---------|
| **文档密集型** | PO, BA, QA | 以 Markdown 文档产出为主；无需终端/Git 权限；快速模型即可满足 |
| **编码密集型** | Architect, Coder | 需要代码生成、构建、测试、Git 操作；需高质量模型 + 全工具集 |
| **独立评审** | Reviewer | 需要独立会话隔离；高质量模型；可读代码和 Diff |

**优点**：
- ✅ **精简高效**：3 个 Profile 覆盖 6 个角色，创建和维护成本低
- ✅ **语义清晰**：Profile 名称（flash/pro/reviewer）直接反映工作负载特征，而非角色名
- ✅ **符合最小权限原则**：sdd-flash 无 terminal/github，sdd-pro 和 sdd-reviewer 有
- ✅ **升级命令简洁**：`scripts/setup-sdd-profiles.sh` 一键创建 3 个 Profile
- ✅ **预加载 Skills 共享复用**：同组角色共享同一预加载列表，Skill 更新对所有适用角色生效
- ✅ **AGENTS.md 覆盖自然**：用户覆盖某角色时只需改一行映射（如 `po: "sdd-pro"`）

**缺点**：
- ⚠️ 角色间无法独立微调（如 PO 和 QA 使用不同模型），但当前设计不需要此能力
- ⚠️ 新增一个与现有分组特征不同的角色时，可能需要新增第 4 个 Profile（可接受）

**复杂度评分**：创建 3/10 | 维护 3/10 | 用户体验 8/10

---

### 1.3 方案对比总结

| 维度 | 方案 A（6 Profile） | 方案 B（3 Profile）✅ |
|:-----|:-------------------|:---------------------|
| Profile 数量 | 6 | 3 |
| 创建命令次数 | 6 × `hermes profile create` | 3 × `hermes profile create` |
| 维护成本 | 高（6 份配置需同步） | 低（3 份配置） |
| 角色隔离粒度 | 细（每角色独立） | 中（同组共享） |
| 向后兼容性 | 一致 | 一致 |
| 用户体验 | 复杂（6 个名称需记忆） | 简单（flash/pro/reviewer 语义化） |
| 映射表行数 | 6 | 6（相同） |
| 扩展新角色成本 | 新增 1 Profile（可接受） | 可能需新增 Profile（可接受） |
| 符合 PRD 设计 | 否（原 PRD 明确 3 Profile） | ✅ 是 |

**结论**：选择方案 B。3 Profile 角色分组在满足所有 AC 的前提下，提供了更低的维护成本和更清晰的语义。

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SDD Orchestrator v2.1.0                       │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                     Profile 解析层 (NEW)                       │  │
│  │                                                                │  │
│  │  ┌──────────────────┐    ┌──────────────────┐                 │  │
│  │  │ sdd-rules.md     │    │ AGENTS.md        │                 │  │
│  │  │ ROLE_TO_PROFILE_ │    │ sdd_config.      │                 │  │
│  │  │ DEFAULT (默认)   │    │ role_to_profile  │                 │  │
│  │  │                  │    │ (项目覆盖)       │                 │  │
│  │  └────────┬─────────┘    └────────┬─────────┘                 │  │
│  │           │     浅合并 (shallow)  │                            │  │
│  │           └──────────┬───────────┘                            │  │
│  │                      ▼                                        │  │
│  │           ┌──────────────────┐                                │  │
│  │           │ resolve_profile  │                                │  │
│  │           │ (role) → profile │                                │  │
│  │           │       | None     │                                │  │
│  │           └────────┬─────────┘                                │  │
│  │                    │                                          │  │
│  │     ┌──────────────┼──────────────┐                           │  │
│  │     ▼              ▼              ▼                           │  │
│  │  profile=       profile=       profile=                       │  │
│  │  "sdd-flash"    "sdd-pro"     "sdd-reviewer"                  │  │
│  │  (PO/BA/QA)     (Arch/Coder)  (Reviewer)                      │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    delegate_task (NEW)                         │  │
│  │                                                                │  │
│  │  delegate_task(                                               │  │
│  │      goal: "...",                                             │  │
│  │      profile: "sdd-flash",  ← NEW: 可选字段                   │  │
│  │      context: {...},                                          │  │
│  │      toolsets: [...],                                         │  │
│  │      role: "leaf"                                             │  │
│  │  )                                                            │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              ▼                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Hermes Profile Runtime                      │  │
│  │                                                                │  │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────────┐               │  │
│  │  │sdd-flash │   │ sdd-pro  │   │sdd-reviewer  │               │  │
│  │  │          │   │          │   │              │               │  │
│  │  │ model:   │   │ model:   │   │ model:       │               │  │
│  │  │  flash   │   │  pro     │   │  pro         │               │  │
│  │  │          │   │          │   │              │               │  │
│  │  │ tools:   │   │ tools:   │   │ tools:       │               │  │
│  │  │  file    │   │  file    │   │  file        │               │  │
│  │  │  skills  │   │  terminal│   │  terminal    │               │  │
│  │  │          │   │  skills  │   │  skills      │               │  │
│  │  │          │   │  github  │   │  github      │               │  │
│  │  │          │   │          │   │              │               │  │
│  │  │ session: │   │ session: │   │ session:     │               │  │
│  │  │  shared  │   │  shared  │   │  ISOLATED ✨ │               │  │
│  │  └──────────┘   └──────────┘   └──────────────┘               │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 模块划分

```
源文件修改范围（5 个修改 + 1 个新建）：

┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: 规则定义层                                             │
│                                                                  │
│  📄 skills/sdd/shared/sdd-rules.md           [MODIFY]            │
│     └─ 新增 ROLE_TO_PROFILE_DEFAULT 常量                         │
│                                                                  │
│  📄 AGENTS.md                                 [MODIFY]            │
│     └─ 新增 sdd_config.role_to_profile 可选覆盖段                 │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: 编排器内核                                             │
│                                                                  │
│  📄 skills/sdd/sdd-orchestrator/SKILL.md      [MODIFY]            │
│     ├─ 版本号 2.0.3 → 2.1.0                                    │
│     ├─ 更新 Delegation 章节                                     │
│     └─ 新增 Profile 委托集成说明                                 │
│                                                                  │
│  📄 skills/sdd/sdd-orchestrator/               [MODIFY]           │
│     references/delegate-protocol.md                              │
│     ├─ 委托格式新增 profile 字段                                  │
│     ├─ Profile 选择算法伪代码                                    │
│     └─ 回退逻辑说明                                              │
│                                                                  │
│  📄 skills/sdd/sdd-orchestrator/               [MODIFY]           │
│     scripts/orchestrator.py                                      │
│     ├─ 新增 load_profile_mapping()                               │
│     ├─ 修改 delegate_agent() 支持 profile 参数                    │
│     └─ 新增 get_profile_for_role()                               │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: 初始化与配置                                           │
│                                                                  │
│  📄 skills/sdd/sdd-init/SKILL.md              [MODIFY]            │
│     └─ 升级模式新增 Profile 检测与创建步骤                         │
│                                                                  │
│  📄 scripts/setup-sdd-profiles.sh             [NEW]               │
│     └─ 一键创建 3 个 Profile 的 Shell 脚本                        │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4: 数据模型                                               │
│                                                                  │
│  📄 skills/sdd/shared/sdd-state-schema.md     [MODIFY]            │
│     └─ .sdd-state.json Schema 新增 profile 字段                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 数据流

```
用户启动 SDD 流程
       │
       ▼
┌──────────────────┐
│ sdd-orchestrator │
│ transition()     │
└────────┬─────────┘
         │ 状态机推进到 *_ENTRY
         ▼
┌──────────────────────┐
│ delegate_agent()     │
│ (role=从 STATE 推导) │
└────────┬─────────────┘
         │
         ▼
┌─────────────────────────────┐
│ get_profile_for_role(role)  │  ← NEW: Profile 解析入口
│                             │
│  1. 读取 shared/sdd-rules.md│
│     → ROLE_TO_PROFILE_     │
│       DEFAULT              │
│                             │
│  2. 读取 AGENTS.md          │
│     → sdd_config.          │
│       role_to_profile      │
│                             │
│  3. 浅合并                  │
│     default.update(override)│
│                             │
│  4. 查找 role → profile     │
│     found? → 继续           │
│     missing? → return None  │
│                             │
│  5. 验证 Profile 存在       │
│     hermes profile list     │
│     exists? → return name   │
│     missing? → WARN+None    │
└────────┬────────────────────┘
         │
         ├── profile = "sdd-flash" ──────┐
         ├── profile = "sdd-pro" ────────┤
         ├── profile = "sdd-reviewer" ───┤
         └── profile = None ─────────────┤
                                         ▼
                              ┌──────────────────┐
                              │ delegate_task(   │
                              │   goal: "...",   │
                              │   profile: ...,  │  ← NEW 字段
                              │   context: {...} │
                              │ )                │
                              └──────────────────┘
```

---

## 3. 详细设计

### 3.1 Role → Profile 映射数据模型

**设计决策**：默认映射定义在 `shared/sdd-rules.md`，AGENTS.md 只做可选覆盖。

**理由**：
- `sdd-rules.md` 是 SDD 流程的通用规则文件，所有项目自动继承
- `AGENTS.md` 是项目级配置，只做覆盖不承载通用规则
- 避免 AGENTS.md 膨胀——通用规则不应在每个项目的 AGENTS.md 中重复定义

```yaml
# shared/sdd-rules.md — 新增常量定义
# SDD 角色→Profile 默认映射（编排器 v2.1.0+ 使用）
ROLE_TO_PROFILE_DEFAULT:
  po: "sdd-flash"        # 文档密集 — 快速模型
  ba: "sdd-flash"        # 文档密集 — 快速模型
  architect: "sdd-pro"   # 编码设计 — 高质量模型
  coder: "sdd-pro"       # 编码实现 — 高质量模型
  reviewer: "sdd-reviewer"  # 独立评审 — 高质量模型 + 独立会话
  qa: "sdd-flash"        # 测试验证 — 快速模型
```

```yaml
# AGENTS.md — 可选覆盖（用户按需添加）
## SDD Profile 覆盖（可选）
# 不声明 = 使用 shared/sdd-rules.md 默认映射
# 只覆盖指定角色，未覆盖角色继续使用默认值
sdd_config:
  role_to_profile:
    po: "sdd-pro"      # 示例：将 PO 升级为 pro 模型
    # ba/architect/coder/reviewer/qa 继续使用默认值
```

### 3.2 Profile 解析算法

```
resolve_profile(role: str) → str | None:

  Input:  role ∈ {po, ba, architect, coder, reviewer, qa}

  1. defaults = parse_yaml("skills/sdd/shared/sdd-rules.md")
               → extract ROLE_TO_PROFILE_DEFAULT

  2. agents_md = parse_yaml("AGENTS.md")
     override  = agents_md.sdd_config?.role_to_profile  or {}

  3. merged = {**defaults, **override}    # 浅合并

  4. profile = merged.get(role)
     if profile is None:
         log(WARN, f"角色 '{role}' 未在映射表中找到，回退到无 Profile 模式")
         return None

  5. if not hermes_profile_exists(profile):
         log(WARN, f"Profile '{profile}' 不存在。运行: hermes profile create {profile}")
         return None

  6. return profile
```

### 3.3 delegate_task 格式变更

**变更前（v2.0.2）**：
```yaml
delegate_task:
  goal: "..."
  context: |
    ...
  toolsets: ["file", "terminal", "skills"]
  role: "leaf"
```

**变更后（v2.1.0）**：
```yaml
delegate_task:
  goal: "..."
  profile: "sdd-flash"        # NEW: 可选字段
  context: |
    ...
  toolsets: ["file", "skills"]  # 与 Profile 工具集一致
  role: "leaf"
```

**向后兼容**：`profile` 字段不存在时行为与 v2.0.2 完全一致（不指定 profile，子 Agent 继承编排器会话配置）。

### 3.4 orchestrator.py 代码变更

**新增方法**：

```python
# 1. 加载 Profile 映射
def load_profile_mapping(self) -> Dict[str, str]:
    """从 shared/sdd-rules.md 加载默认映射 + AGENTS.md 覆盖"""
    ...

# 2. 解析单个角色的 Profile
def get_profile_for_role(self, role: str) -> Optional[str]:
    """根据角色返回 Profile 名称或 None"""
    ...

# 3. 检查 Profile 是否存在（调用 hermes CLI）
def check_profile_exists(self, profile_name: str) -> bool:
    """调用 hermes profile list 检查 Profile 是否存在"""
    ...
```

**修改方法**：

```python
# delegate_agent() — 新增 profile 参数
def delegate_agent(self, change_id: str, state: State):
    role = self.get_role_from_state(state)              # NEW
    profile = self.get_profile_for_role(role)           # NEW
    
    if profile:
        print(f"🔷 使用 Profile: {profile}")
        context["profile"] = profile                   # NEW
    else:
        print(f"ℹ️  无 Profile 配置，使用默认模式")
    
    # ... 现有委托逻辑 ...
```

### 3.5 sdd-init 升级模式扩展

在 `sdd-init --upgrade` 的 Step B4（执行升级）中新增：

```markdown
### Step B4.x: 检测并创建 SDD Profiles

1. 检测 Hermes 版本 ≥ v2.1.0
   → hermes --version | grep -oP '\d+\.\d+\.\d+'
   
2. 版本满足则执行 setup 脚本
   → bash scripts/setup-sdd-profiles.sh
   
3. 输出 Profile 创建摘要
   → hermes profile list | grep sdd-
```

### 3.6 新建文件：scripts/setup-sdd-profiles.sh

一键脚本，幂等创建 3 个 Profile：

```bash
#!/bin/bash
# setup-sdd-profiles.sh — 创建 SDD v2.1.0 所需的 3 个 Hermes Profile
# 用法: bash scripts/setup-sdd-profiles.sh
# 幂等：已存在的 Profile 跳过创建

set -e

echo "=== SDD Profile Setup ==="

# 检查 hermes 命令
if ! command -v hermes &> /dev/null; then
    echo "❌ hermes 命令不可用，请安装 Hermes v2.1.0+"
    exit 1
fi

create_profile() {
    local name=$1 model=$2 tools=$3
    if hermes profile list 2>/dev/null | grep -q "$name"; then
        echo "⏭️  Profile '$name' 已存在，跳过"
    else
        echo "📁 创建 Profile: $name"
        hermes profile create "$name" --model "$model" --tools "$tools"
        echo "✅ Profile '$name' 创建成功"
    fi
}

# sdd-flash: 文档密集型角色 (PO/BA/QA)
create_profile "sdd-flash" \
    "deepseek/deepseek-v4-flash" \
    "file,skills"

# sdd-pro: 编码密集型角色 (Architect/Coder)
create_profile "sdd-pro" \
    "deepseek/deepseek-v4-pro" \
    "file,terminal,skills,github"

# sdd-reviewer: 独立评审 (Reviewer)
create_profile "sdd-reviewer" \
    "deepseek/deepseek-v4-pro" \
    "file,terminal,skills,github"

echo ""
echo "=== Profile 创建摘要 ==="
hermes profile list 2>/dev/null | grep "sdd-"
echo ""
echo "✅ 3 个 SDD Profile 就绪"
```

### 3.7 3 个 Profile 的完整规格

| 配置项 | sdd-flash | sdd-pro | sdd-reviewer |
|:-------|:----------|:--------|:-------------|
| **模型** | `deepseek/deepseek-v4-flash` | `deepseek/deepseek-v4-pro` | `deepseek/deepseek-v4-pro` |
| **工具集** | `file`, `skills` | `file`, `terminal`, `skills`, `github` | `file`, `terminal`, `skills`, `github` |
| **预加载 Skills** | `po-agent`, `ba-agent`, `qa-agent`, `sdd-orchestrator` | `architect-agent`, `coder-agent`, `sdd-orchestrator`, `test-driven-development`, `local-verifier` | `reviewer-agent`, `sdd-orchestrator`, `post-coding-review` |
| **适用角色** | PO, BA, QA | Architect, Coder | Reviewer |
| **会话模式** | 共享 | 共享 | **独立** |
| **最小权限** | 无 terminal/github | 全工具集 | 全工具集 |

### 3.8 向后兼容策略

```
兼容性决策树：

AGENTS.md 是否有 sdd_config.role_to_profile?
    │
    ├── NO  → 不启用 Profile 模式
    │         delegate_task 不传 profile 参数
    │         行为与 v2.0.3 完全一致 ✅
    │
    └── YES → 解析覆盖映射
              │
              ├── 覆盖后的 profile 存在 → 使用 Profile 委托 ✅
              │
              ├── 覆盖后的 profile 不存在 → WARNING + 回退 ✅
              │
              └── role 不在映射表中 → WARNING + 回退 ✅
```

---

## 4. 关键设计决策

| 决策 | 选择 | 理由 |
|:-----|:-----|:-----|
| Profile 数量 | 3 个 | 角色分组复用，降低维护成本 |
| 默认映射位置 | `shared/sdd-rules.md` | 通用规则应定义为常量，不在 AGENTS.md |
| AGENTS.md 角色 | 仅做可选覆盖 | 项目配置不应承载通用规则 |
| 合并策略 | 浅合并（shallow merge） | 简单可靠，不需要深度嵌套合并 |
| Profile 不存在的处理 | 回退 + WARNING | 不阻断流程，用户可稍后修复 |
| orchestrator.py 版本 | v2.0.0 → v2.1.0 | 新增 Profile 感知能力，主版本号升级 |
| Profile 名称前缀 | `sdd-` | 命名空间隔离，避免与其他 Profile 冲突 |
| 创建脚本语言 | Bash shell | 跨平台兼容（Linux/macOS/WSL），无额外依赖 |
| 预加载 Skills 位置 | Profile 创建后通过配置文件设置 | `hermes profile create` 当前不支持 `--skills` 参数 |

---

## 5. 边界条件处理

| 边界场景 | 处理策略 |
|:---------|:---------|
| AGENTS.md 不存在 | 仅使用默认映射（→ Profile 模式仍可用） |
| AGENTS.md YAML 解析失败 | 回退到无 Profile 模式 + ERROR 日志 |
| role_to_profile 指向非法字符 | 回退 + ERROR "Profile 名称不合法" |
| Hermes < v2.1.0 | sdd-init 跳过 Profile 创建，提示升级 |
| hermes CLI 不可用 | 脚本退出，不阻塞主流程 |
| 同一 Profile 被多角色使用 | 正常设计——3 个 Profile 覆盖 6 个角色 |
| Profile 创建时磁盘满 | 捕获错误，跳过该 Profile 继续下一个 |

---

## 6. 非功能需求满足

| NFR | 设计如何满足 |
|:----|:------------|
| **性能**：resolve_profile() < 10ms | YAML 解析在内存中完成，无网络调用 |
| **安全**：最小权限 | sdd-flash 仅 file+skills，无 terminal/github |
| **可用性**：无配置回退 | 无 role_to_profile → delegate_task 不传 profile |
| **可维护性**：配置 ≤ 20 行 | AGENTS.md 新增段约 6 行（注释+1行覆盖映射） |
| **可扩展性**：新增角色低成本 | 在 ROLE_TO_PROFILE_DEFAULT 加 1 行映射即可 |

---

## 7. 产出物清单

| # | 文件 | 操作 | 说明 |
|:--:|------|:----:|------|
| 1 | `skills/sdd/shared/sdd-rules.md` | 修改 | 新增 ROLE_TO_PROFILE_DEFAULT（约 10 行） |
| 2 | `AGENTS.md` | 修改 | 新增 sdd_config 可选覆盖段（约 8 行注释+配置） |
| 3 | `skills/sdd/sdd-orchestrator/SKILL.md` | 修改 | 版本号升级；Delegation 章节更新；"Hermes v2.1.0 Profile 集成"改为正式规范 |
| 4 | `skills/sdd/sdd-orchestrator/references/delegate-protocol.md` | 修改 | 委托格式新增 profile 字段；Profile 选择算法；"Planned"→正式 |
| 5 | `skills/sdd/sdd-orchestrator/scripts/orchestrator.py` | 修改 | 新增 3 个方法；delegate_agent() 支持 profile |
| 6 | `skills/sdd/sdd-init/SKILL.md` | 修改 | 升级模式新增 Profile 检测与创建步骤 |
| 7 | `skills/sdd/shared/sdd-state-schema.md` | 修改 | Schema 新增 profile 可选字段 |
| 8 | `scripts/setup-sdd-profiles.sh` | **新建** | 一键创建 3 个 Profile |

**不修改的文件**：各角色 Agent SKILL.md（po-agent、ba-agent 等）—— Profile 绑定是透明的基础设施层。
