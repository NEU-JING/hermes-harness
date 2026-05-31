# Spec — 007: 基于 Hermes v2.1.0 Profile 的 SDD 多 Agent 委托协议升级

> **变更 ID**: `007-profile-delegation`
> **流程级别**: Standard
> **创建时间**: 2026-05-31
> **版本**: v1.0
> **前置文档**: [prd.md](./prd.md)

---

## 功能概述

升级 SDD Orchestrator 委托协议，利用 Hermes v2.1.0 Profile 隔离能力实现多 Agent 委托的模型分级、独立会话评审和最小权限控制。通过 3 个 Hermes Profile 将 6 个 SDD 角色按工作负载特征分组，编排器通过内置默认映射 + AGENTS.md 可选覆盖驱动 Profile 选择逻辑。默认映射定义在 `shared/sdd-rules.md` 中，AGENTS.md 可覆盖。

---

## 详细需求

### 需求 R1：3 个 Hermes Profile 定义

**描述**：定义 3 个 Profile 的完整规格，每个 Profile 包含模型、预加载 Skills、工具集和适用角色。

**Profile 规格**：

#### Profile 1: `sdd-flash`

| 配置项 | 值 | 说明 |
|:---|:---|:---|
| 模型 | `deepseek/deepseek-v4-flash` | 快速稳定，文档/需求/测试编写首选 |
| 预加载 Skills | `po-agent`, `ba-agent`, `qa-agent`, `sdd-orchestrator` | 启动时自动加载，确保代理知道自己的角色 |
| 工具集 | `file`, `skills` | 文件读写、技能加载——无需终端/Git 权限 |
| 适用角色 | PO、BA、QA | 以文档产出为主，无需代码执行权限 |

#### Profile 2: `sdd-pro`

| 配置项 | 值 | 说明 |
|:---|:---|:---|
| 模型 | `deepseek/deepseek-v4-pro` | 高质量编码与技术设计 |
| 预加载 Skills | `architect-agent`, `coder-agent`, `sdd-orchestrator`, `test-driven-development`, `local-verifier` | 编码必需 |
| 工具集 | `file`, `terminal`, `skills`, `github` | 全权限终端、Git 操作、代码搜索 |
| 适用角色 | Architect、Coder | 需要代码生成、构建、测试、Git 操作 |

#### Profile 3: `sdd-reviewer`

| 配置项 | 值 | 说明 |
|:---|:---|:---|
| 模型 | `deepseek/deepseek-v4-pro` | 高质量评审需同等级模型 |
| 预加载 Skills | `reviewer-agent`, `sdd-orchestrator`, `post-coding-review` | 独立加载，不与其他角色共享会话 |
| 工具集 | `file`, `terminal`, `skills`, `github` | 代码阅读、Diff 查看、构建验证、Git 操作 |
| 适用角色 | Reviewer | **独立会话**——看不到 Coder 阶段的对话上下文 |

**约束**：
- Profile 模型在创建时固定，运行时不自动切换
- Profile 的 Skills 目录绑定到 `~/.hermes/skills/sdd/`，Skill 更新对所有 Profile 生效
- Profile 不绑定特定变更 ID——它们是全局资源，可被所有 SDD 变更复用

---

### 需求 R2：`shared/sdd-rules.md` 默认映射定义

**描述**：在 `skills/sdd/shared/sdd-rules.md` 中定义 `ROLE_TO_PROFILE` 默认映射常量，作为编排器的内置默认值。这是 SDD 流程的通用规则，所有项目自动继承。AGENTS.md 可选择性覆盖。

**默认映射**（定义在 `sdd-rules.md`）：

```yaml
# shared/sdd-rules.md — SDD 角色→Profile 默认映射
ROLE_TO_PROFILE_DEFAULT:
  po: "sdd-flash"
  ba: "sdd-flash"
  architect: "sdd-pro"
  coder: "sdd-pro"
  reviewer: "sdd-reviewer"
  qa: "sdd-flash"
```

**AGENTS.md 覆盖方式**（可选）：
```yaml
## SDD Profile 覆盖（可选）
# 不声明 = 使用 shared/sdd-rules.md 默认映射
# 声明后只覆盖指定的角色，未指定角色继续使用默认值
sdd_config:
  role_to_profile:
    po: "sdd-pro"  # 仅覆盖 PO，其他角色用默认
```

**约束**：
- 默认映射定义在 `shared/sdd-rules.md`，非 AGENTS.md
- AGENTS.md 的 `sdd_config.role_to_profile` **仅做覆盖**，不允许清空默认映射
- 每个 role key 的值必须是合法 Profile 名称（字母、数字、连字符）

---

### 需求 R3：Orchestrator Profile 感知委托

**描述**：编排器在执行 `delegate_task` 前，从 `shared/sdd-rules.md` 加载默认 `ROLE_TO_PROFILE` 映射，然后检查 AGENTS.md 是否有覆盖，合并后解析当前角色对应的 Profile 名称，并传递给委托调用。

**输入**：当前委托角色的类型（`po` / `ba` / `architect` / `coder` / `reviewer` / `qa`）

**处理流程**：

```
1. 从 `shared/sdd-rules.md` 加载默认 `ROLE_TO_PROFILE` 映射
2. 检查 AGENTS.md 是否有 `sdd_config.role_to_profile` 覆盖段
3. 如果有，合并覆盖到默认映射中
4. 在合并后的映射中查找当前角色
5. 如果找到 → 使用对应 Profile
6. 如果未找到（角色不在映射中）→ 回退到无 Profile 模式
7. 检查 Profile 是否存在（`hermes profile list`）
8. 如果 Profile 不存在 → 输出 WARNING，回退到无 Profile 模式
9. 将 Profile 名称（或无 Profile）传递给 `delegate_task`
**输出**：`delegate_task` 调用携带 `profile` 参数（Profile 存在时）或不携带（回退时）

**约束**：
- Profile 解析失败不阻断流程，仅输出警告并回退
- 每个阶段委托前重新读取 AGENTS.md（支持运行时热更新）

---

### 需求 R4：sdd-init Profile 自动创建

**描述**：sdd-init 在升级模式（`--upgrade`）下自动创建 3 个 Hermes Profile，检测 Hermes 版本 ≥ v2.1.0 后执行 `hermes profile create`。

**Profile 创建参数**：

| Profile | CLI 参数 | 
|:---|:---|
| `sdd-flash` | `hermes profile create sdd-flash --model deepseek/deepseek-v4-flash --tools file,skills` |
| `sdd-pro` | `hermes profile create sdd-pro --model deepseek/deepseek-v4-pro --tools file,terminal,skills,github` |
| `sdd-reviewer` | `hermes profile create sdd-reviewer --model deepseek/deepseek-v4-pro --tools file,terminal,skills,github` |

**约束**：
- Profile 已存在时跳过创建，输出 SKIP 信息
- `hermes` 命令不可用时跳过 Profile 创建，输出提示要求手动创建
- 创建后自动配置预加载 Skills 列表
- 创建完成后输出 3 个 Profile 的摘要

---

### 需求 R5：向后兼容

**描述**：AGENTS.md 无 `role_to_profile` 配置时，整个系统保持变更前行为不变——编排器不指定 Profile，子 Agent 继承编排器会话配置。

**输入**：AGENTS.md 中不包含 `sdd_config.role_to_profile` 段，或配置段值为空

**输出**：`delegate_task` 调用不携带 `profile` 参数

**约束**：
- 向后兼容必须 100% 覆盖——任何无配置场景不得引入新错误
- 所有现有 SDD 测试用例在无配置时必须通过
- 用户可在任意时间通过添加配置启用 Profile 模式

---

### 需求 R6：Delegate 协议新格式（含 Profile 字段）

**描述**：升级 delegate-protocol.md 中定义的委托格式，新增 `profile` 字段；编排器代码中 `delegate_task` 调用增加 Profile 参数传递。

**新格式**：

```yaml
delegate_task:
  goal: "[明确的目标描述]"
  profile: "sdd-flash"        # 新增字段，可选
  context: |
    ## 变更上下文
    change_id: "{change_id}"
    current_state: "{state}"
    flow_level: "Standard"
    # ... 前置产物、约束、产出要求同 v2.0.2
  toolsets: ["file", "terminal", "skills"]
  role: "leaf"
```

**Profile 选择算法**（伪代码）：

```python
def resolve_profile(role: str, agents_md: dict) -> str | None:
    """
    根据角色从默认映射 + AGENTS.md 覆盖解析 Profile 名称。
    返回 Profile 名称或 None（回退模式）。
    """
    # 1. 从 shared/sdd-rules.md 加载默认映射
    from sdd_rules import ROLE_TO_PROFILE_DEFAULT
    
    role_to_profile = dict(ROLE_TO_PROFILE_DEFAULT)
    
    # 2. AGENTS.md 覆盖（浅合并）
    sdd_config = agents_md.get("sdd_config", {})
    override = sdd_config.get("role_to_profile", {})
    if override:
        role_to_profile.update(override)
    
    # 3. 查找角色映射
    profile_name = role_to_profile.get(role)
    if not profile_name:
        return None
    
    # 4. 验证 Profile 存在
    if not hermes_profile_exists(profile_name):
        logger.warning(
            f"Profile '{profile_name}' 不存在，回退到无 Profile 模式。"
            f"运行 'hermes profile create {profile_name}' 创建。"
        )
        return None
    
    return profile_name
```

**约束**：
- `profile` 字段为可选字段，不存在时行为与 v2.0.2 一致
- 同一角色在不同项目中可能映射到不同 Profile（由 AGENTS.md 覆盖决定）
- Profile 名称在 delegate_task 调用时解析，不缓存

---

### 需求 R7：工具集最小权限

**描述**：每个 Profile 仅授予其适用角色所需的最小工具集，遵循最小权限原则。

**工具集矩阵**：

| Profile | file | skills | terminal | github | web |
|:--------|:---:|:---:|:---:|:---:|:---:|
| `sdd-flash` | ✓ | ✓ | ✗ | ✗ | ✗ |
| `sdd-pro` | ✓ | ✓ | ✓ | ✓ | ✗ |
| `sdd-reviewer` | ✓ | ✓ | ✓ | ✓ | ✗ |

**约束**：
- `sdd-flash` 不得包含 `terminal` 和 `github` 工具——PO/BA/QA 无需代码执行或版本控制权限
- Profile 创建时一次性配置，运行时不动态修改
- 工具集锁定后，用户需通过 `hermes profile` 命令手动调整

---

### 需求 R8：Reviewer 独立会话

**描述**：Reviewer 委托使用独立 Profile `sdd-reviewer`，启动新的独立会话，不继承 Coder 阶段或任何前置阶段的对话上下文。

**输入**：Reviewer 委托上下文（仅包含前置产物路径：spec.md、design.md、completion-report.md、Git commit 列表）

**输出**：review-report.md

**约束**：
- Reviewer 委托的上下文中不包含前置阶段的对话历史
- Reviewer 仅基于产物文件（spec、design、code diff）进行评审
- 即使 `role_to_profile` 未配置导致回退到无 Profile 模式，Reviewer 委托的上下文也仅包含产物路径（此行为 v2.0.2 已实现）

---

## Acceptance Criteria（验收标准）

### 角色 Profile 创建（AC1-AC3）

| 编号 | 场景 | Given | When | Then |
|:---:|------|-------|------|------|
| AC1 | sdd-flash 创建 | Hermes v2.1.0+ 已安装，Profile 不存在 | `hermes profile create sdd-flash` | 模型=flash，预加载 Skills=po-agent,ba-agent,qa-agent，工具集=file,skills |
| AC2 | sdd-pro 创建 | Profile 不存在 | `hermes profile create sdd-pro` | 模型=pro，预加载 Skills=architect-agent,coder-agent,tdd,local-verifier，工具集=file,terminal,skills,github |
| AC3 | sdd-reviewer 创建 | Profile 不存在 | `hermes profile create sdd-reviewer` | 模型=pro，预加载 Skills=reviewer-agent,post-coding-review，工具集=file,terminal,skills,github |

### 角色委托正确性（AC4-AC9）—— 覆盖所有 6 个角色

| 编号 | 场景 | Given | When | Then |
|:---:|------|-------|------|------|
| AC4 | **PO** 委托使用 sdd-flash | 默认映射生效，sdd-flash 已创建 | Orchestrator 发起 PO 阶段委托 | `delegate_task` 携带 `profile: "sdd-flash"`，子 Agent 模型=flash，工具集=file,skills |
| AC5 | **BA** 委托使用 sdd-flash | 默认映射生效，sdd-flash 已创建 | Orchestrator 发起 BA 阶段委托 | `delegate_task` 携带 `profile: "sdd-flash"`，子 Agent 模型=flash，工具集=file,skills |
| AC6 | **Architect** 委托使用 sdd-pro | 默认映射生效，sdd-pro 已创建 | Orchestrator 发起 Architect 阶段委托 | `delegate_task` 携带 `profile: "sdd-pro"`，子 Agent 模型=pro，工具集=file,terminal,skills |
| AC7 | **Coder** 委托使用 sdd-pro | 默认映射生效，sdd-pro 已创建 | Orchestrator 发起 Coder 阶段委托 | `delegate_task` 携带 `profile: "sdd-pro"`，子 Agent 模型=pro，技能预载含 coder-agent+tdd+local-verifier，工具集=file,terminal,skills,github |
| AC8 | **Reviewer** 委托使用 sdd-reviewer | 默认映射生效，sdd-reviewer 已创建，Coder 已完成 | Orchestrator 发起 Reviewer 委托 | `delegate_task` 携带 `profile: "sdd-reviewer"`，子 Agent 模型=pro，技能预载含 reviewer-agent，委托上下文仅含产物路径，不含 Coder 对话历史 |
| AC9 | **QA** 委托使用 sdd-flash | 默认映射生效，sdd-flash 已创建 | Orchestrator 发起 QA 阶段委托 | `delegate_task` 携带 `profile: "sdd-flash"`，子 Agent 模型=flash，工具集=file,terminal,skills,github |

### 向后兼容与边界条件（AC10-AC15）

| 编号 | 场景 | Given | When | Then |
|:---:|------|-------|------|------|
| AC10 | 无配置时保持当前行为 | AGENTS.md 无 `sdd_config.role_to_profile` 段 | 发起任意阶段委托 | `delegate_task` 不携带 `profile` 参数，行为与 v2.0.3 完全一致 |
| AC11 | Profile 不存在时回退并警告 | 默认映射中 `po: sdd-flash` 但 profile 未创建 | 发起 PO 阶段委托 | 输出 WARNING，`delegate_task` 不携带 `profile`，PO 正常执行 |
| AC12 | AGENTS.md 覆盖生效 | AGENTS.md 声明 `sdd_config.role_to_profile.po: sdd-pro` | 发起 PO 阶段委托 | `delegate_task` 携带 `profile: "sdd-pro"`（覆盖了默认的 flash） |
| AC13 | 工具集最小化验证 | sdd-flash 已创建 | 检查 sdd-flash 工具集 | 仅含 `file,skills`，不含 `terminal` 或 `github` |
| AC14 | sdd-rules.md 默认映射段 | sdd-rules.md 已更新 | 统计 `ROLE_TO_PROFILE_DEFAULT` 行数 | ≤ 20 行（含注释） |
| AC15 | orchestrator SKILL.md 版本号 | 已修改 | 读取 version + 标题 | `version: 2.1.0`，标题含 `v2.1.0` |

---

## 数据模型

### role_to_profile 映射表

将 6 个 SDD 角色映射到 3 个 Hermes Profile。

**定义位置**：
1. **默认映射**：`skills/sdd/shared/sdd-rules.md` 中的 `ROLE_TO_PROFILE_DEFAULT` 常量
2. **项目覆盖**（可选）：AGENTS.md 中的 `sdd_config.role_to_profile` 段

**优先级**：AGENTS.md 覆盖 > 默认映射（浅合并，只覆盖指定角色）
        po:
          type: string
          pattern: "^[a-z][a-z0-9-]*$"
          description: "PO 角色使用的 Profile 名称"
        ba:
          type: string
          pattern: "^[a-z][a-z0-9-]*$"
          description: "BA 角色使用的 Profile 名称"
        architect:
          type: string
          pattern: "^[a-z][a-z0-9-]*$"
          description: "Architect 角色使用的 Profile 名称"
        coder:
          type: string
          pattern: "^[a-z][a-z0-9-]*$"
          description: "Coder 角色使用的 Profile 名称"
        reviewer:
          type: string
          pattern: "^[a-z][a-z0-9-]*$"
          description: "Reviewer 角色使用的 Profile 名称"
        qa:
          type: string
          pattern: "^[a-z][a-z0-9-]*$"
          description: "QA 角色使用的 Profile 名称"
  additionalProperties: false
```

**默认值**（定义在 `shared/sdd-rules.md`，AGENTS.md 未覆盖时使用）：

```yaml
sdd_config:
  role_to_profile:
    po: "sdd-flash"
    ba: "sdd-flash"
    architect: "sdd-pro"
    coder: "sdd-pro"
    reviewer: "sdd-reviewer"
    qa: "sdd-flash"
```

> **设计说明**：默认映射定义在 `shared/sdd-rules.md` 中，作为编排器的内置常量。当 AGENTS.md 无覆盖时不启用 Profile 模式（保持完全向后兼容）；当 AGENTS.md 主动声明 `sdd_config.role_to_profile` 时，与默认映射浅合并，覆盖指定角色。未来可通过 `sdd-init --upgrade` 一键启用 Profile 模式（自动创建 3 个 Profile）。

### Profile 定义

```yaml
HermesProfile:
  type: object
  required: [name, model, toolsets]
  properties:
    name:
      type: string
      enum: ["sdd-flash", "sdd-pro", "sdd-reviewer"]
      description: "Profile 唯一标识"
    model:
      type: string
      description: "绑定的模型标识符，格式: provider/model-name"
    preload_skills:
      type: array
      items:
        type: string
      description: "启动时预加载的 Skills 列表"
    toolsets:
      type: array
      items:
        type: string
        enum: ["file", "terminal", "skills", "github", "web"]
      description: "授予的工具集列表"
    applicable_roles:
      type: array
      items:
        type: string
        enum: ["po", "ba", "architect", "coder", "reviewer", "qa"]
      description: "适用该 Profile 的角色列表（仅文档参考，不由程序强制执行）"
```

### .sdd-state.json Schema 扩展

在现有 Schema 上新增 `profile` 字段：

```yaml
sdd_state:
  properties:
    # ... 现有字段 ...
    profile:
      type: string
      required: false
      description: "当前委托阶段使用的 Profile 名称，阶段完成后记录"
    profile_history:
      type: array
      required: false
      items:
        type: object
        properties:
          state: { type: string }
          profile: { type: string }
          resolved_at: { type: string, format: "date-time" }
      description: "各阶段使用的 Profile 历史记录"
```

---

## Delegate 协议新格式

### 完整委托格式（v2.1.0）

```yaml
delegate_task:
  goal: "[明确的目标描述]"
  
  profile: "sdd-flash"        # 新增 — 可选字段，指定使用的 Hermes Profile
  
  context: |
    ## 变更上下文
    change_id: "{change_id}"
    current_state: "{current_state}"
    flow_level: "{Quick|Standard|Enhanced}"
    incremental_mode: "{true|false}"
    
    ## 前置产物（必须提供完整路径）
    prerequisites:
      - type: "prd"
        path: "docs/changes/{change_id}/prd.md"
      - type: "spec"
        path: "docs/changes/{change_id}/spec.md"
    
    ## 约束条件（来自 AGENTS.md/CONSTITUTION）
    constraints:
      tech_stack: "{from AGENTS.md}"
      naming_conventions: "{from AGENTS.md}"
      disabled_rules: "{from AGENTS.md convention_overrides}"
    
    ## 产出要求
    deliverables:
      - file: "docs/changes/{change_id}/{output_file}"
        template: "{skill_name}/templates/{template_file}"
        required_sections:
          - "section1"
          - "section2"
  
  toolsets: ["file", "terminal", "skills"]
  
  role: "leaf"
```

### 与 v2.0.2 的差异

| 字段 | v2.0.2 | v2.1.0 | 说明 |
|:---|:---|:---|:---|
| `profile` | 不存在 | **新增**，可选 | 指定委托使用的 Hermes Profile |
| 其他字段 | 不变 | 不变 | 完全向后兼容 |

### Profile 委托流程

```
Orchestrator.delegate_agent(role, context)
  │
  ├─ 1. 读取 AGENTS.md
  │     ├─ 加载默认映射 + 合并覆盖 → resolve_profile(role)
  │     │   ├─ Profile 存在     → profile = "sdd-xxx"
  │     │   └─ Profile 不存在   → profile = None + WARNING
  │     └─ 无 role_to_profile  → profile = None（回退）
  │
  ├─ 2. 构建 delegate_task 调用
  │     ├─ profile = "sdd-xxx"  → delegate_task(..., profile="sdd-xxx")
  │     └─ profile = None       → delegate_task(...)   # 不传 profile 参数
  │
  ├─ 3. 等待委托完成
  │     ├─ 成功 → 更新 .sdd-state.json (含 profile/success)
  │     └─ 失败 → 记录失败 + 重试/阻断
  │
  └─ 4. 状态推进 → 下一阶段
```

---

## 非功能需求细化

| 类别 | 原始 NFR | 细化指标 | 验证方式 |
|------|---------|---------|---------|
| 性能 | Profile 选择不增加委托延迟 | `resolve_profile()` 执行时间 < 10ms；整体委托调用额外延迟 < 100ms | 在 orchestrator.py 中插桩计时，运行 3 次取平均值 |
| 性能 | AGENTS.md 解析不阻塞 | AGENTS.md 解析 + Profile 验证总耗时 < 50ms | 使用 Python `time.perf_counter()` 测量 `load_profile_mapping()` 函数耗时 |
| 安全 | 最小权限原则 | `sdd-flash` 工具集 ⊆ {file, skills}；`sdd-pro` ⊆ {file, terminal, skills, github} | 通过 `hermes profile inspect` 验证各 Profile 工具集，不与设计矩阵冲突 |
| 安全 | Profile 间隔离 | `sdd-reviewer` 会话不包含 Coder 阶段对话历史 | 检查 Reviewer 委托的 context 中 prerequisites 字段，确认仅包含产物路径，不含对话历史 |
| 可用性 | 无配置时自动回退 | 缺少 `role_to_profile` 时 100% 回退到当前行为 | 删除 AGENTS.md 中的 `role_to_profile` 配置后，运行完整 SDD Standard 流程，所有阶段正常完成 |
| 可用性 | Profile 不存在时优雅降级 | Profile 名称无效时输出级别为 WARNING 的日志，不抛出异常 | 配置不存在的 Profile 名称后启动任意 SDD 阶段，验证日志输出和流程推进 |
| 可维护性 | 配置清晰可读 | AGENTS.md 新增配置段 ≤ 20 行，包含注释说明 | 统计 AGENTS.md 中 `## SDD Profile` 起至下一 `##` 的行数 |
| 可维护性 | 新增角色低成本 | 新增第 7 个角色仅需：1）在 `role_to_profile` 添加 1 行映射；2）目标 Profile 已存在；无需修改代码 | 模拟新增角色 `security`，验证添加 `security: sdd-pro` 后无需修改 orchestrator.py 即可生效 |
| 可扩展性 | Profile 数量扩展 | 支持未来新增第 4 个 Profile（如 `sdd-experimental`）而不需要修改编排器逻辑 | 创建第 4 个 Profile，在 AGENTS.md 中将任意角色指向它，验证委托成功 |

---

## 边界条件

| 边界场景 | 预期行为 |
|---------|---------|
| AGENTS.md 文件不存在 | 回退到无 Profile 模式，输出 WARNING "AGENTS.md 未找到，使用默认配置" |
| AGENTS.md 包含非标准 YAML 结构导致解析失败 | 回退到无 Profile 模式，输出 ERROR 日志但不断流程 |
| `role_to_profile` 中指向不存在的 Profile | 回退到无 Profile 模式，输出 WARNING "Profile 'xxx' 不存在，请运行 hermes profile create xxx" |
| `role_to_profile` 中 profile 名称包含非法字符 | 回退到无 Profile 模式，输出 ERROR "Profile 名称 'xxx' 不合法" |
| 同一 Profile 被多个角色使用（正常设计） | 正常委托——Profile 为角色分组共享，3 个 Profile 覆盖 6 个角色 |
| 用户在 AGENTS.md 中覆盖默认映射（如 `po: sdd-pro`） | 委托使用用户指定的 Profile，不强制默认值，因为 Profile 名称在设计中支持覆盖 |
| `hermes profile create` 创建失败（如磁盘满） | sdd-init 输出 ERROR 信息，跳过该 Profile 继续处理下一个 |
| orchestrator.py 在无 `role_to_profile` 配置时运行 | 所有委托不传 `profile` 参数，行为与 v2.0.3 完全一致 |

---

## 外部依赖

| 依赖 | 版本要求 | 用途 | 缺失时的影响 |
|:---|:---|:---|:---|
| Hermes Core | ≥ v2.1.0 | `hermes profile create` 命令、`delegate_task` 的 `profile` 参数 | Profile 创建和委托均不可用，整体回退到无 Profile 模式 |
| `hermes profile` CLI | 包含在 Hermes ≥ v2.1.0 | 创建和管理 Profile | sdd-init 无法自动创建 Profile |
| `delegate_task` tool | 支持 `profile` 参数 | Profile 感知委托 | 核心功能不可用，需降级为无 Profile 模式 |
| DeepSeek-v4-flash API | — | sdd-flash Profile 模型 | PO/BA/QA 阶段委托超时或失败 |
| DeepSeek-v4-pro API | — | sdd-pro / sdd-reviewer Profile 模型 | Architect/Coder/Reviewer 阶段委托超时或失败 |

---

> **下一阶段**：用户确认 Spec 后，进入 Architect 阶段产出 design.md 和 tasks.md。
