# PRD — 007: 基于 Hermes v2.1.0 Profile 的 SDD 多 Agent 委托协议升级

> **变更 ID**: `007-profile-delegation`
> **流程级别**: Standard
> **创建时间**: 2026-05-31
> **版本**: v1.0

---

## 背景与目标

### 背景

Hermes v2.1.0 引入了 **Profile** 特性——允许在同一 Hermes 安装下运行多个独立的 Agent 实例，每个实例拥有隔离的配置、会话、Skills 和 Memory。这为 SDD 的多 Agent 协作提供了天然的能力提升：

1. **当前痛点**：SDD Orchestrator 在委托各角色 Agent 时，所有角色共享同一个模型、同一个会话上下文，导致：
   - **Reviewer 自我妥协**：Reviewer 与 Coder 共享会话上下文，评审时可能受编码阶段上下文影响，无法做到真正的"独立评审"
   - **模型不匹配**：PO/BA/QA 等文档密集型角色和 Architect/Coder 等编码密集型角色对模型能力需求不同，统一用高能力模型浪费资源，统一用低成本模型则影响编码质量
   - **工具集污染**：所有角色共享同一个 toolsets 列表，部分角色获得不需要的工具权限（如 PO 获得 terminal 写权限），违反最小权限原则
   - **上下文膨胀**：8 阶段流程中所有角色共享一个会话，上下文窗口被多阶段产物占满，后期阶段面临 token 不足

2. **能力就绪**：Hermes v2.1.0 的 `hermes profile create` 命令可以创建独立 Profile，每个 Profile 可绑定：
   - 独立模型（如 DeepSeek-v4-flash / DeepSeek-v4-pro）
   - 预加载 Skills（启动时自动加载）
   - 工具集（最小权限原则）
   - 独立会话上下文（解决 Reviewer 自我妥协）

3. **项目已有讨论基础**：sdd-orchestrator SKILL.md 和 delegate-protocol.md 中已预留 "Hermes v2.1 扩展：Profile 委托模式" 章节（标记为 "Planned"），变更 007 将其从规划落地为实际能力。

### 目标

1. **模型分层**：文档密集型角色（PO/BA/QA）使用 flash 模型，编码/设计/评审角色使用 pro 模型，实现成本-质量平衡
2. **独立评审**：Reviewer 使用独立 Profile + 独立会话，从机制上杜绝"自我妥协"问题
3. **最小权限**：每个角色 Profile 仅授予所需工具集，降低安全风险
4. **向后兼容**：AGENTS.md 未配置 Profile 映射时，保持当前行为不变
5. **开箱即用**：sdd-init 升级后自动创建 3 个 SDD Profile（sdd-pro / sdd-flash / sdd-reviewer）

---

## 用户场景

### 场景 1：首次使用 SDD 的项目接入 Profile 委托

- **角色**：项目维护者
- **前置条件**：已安装 Hermes v2.1.0+，项目已通过 `sdd-init --upgrade` 升级
- **操作流程**：
  1. 运行 `sdd-init --upgrade`，自动创建 3 个 Profile 并更新 AGENTS.md
  2. 启动 SDD 流程：编排器根据 AGENTS.md 中的 `role_to_profile` 映射自动选择 Profile
  3. PO 阶段委托给 `sdd-flash` Profile（DeepSeek-v4-flash + 最小工具集）
  4. Architect 阶段委托给 `sdd-pro` Profile（DeepSeek-v4-pro + 终端权限）
  5. Reviewer 阶段委托给 `sdd-reviewer` Profile（独立会话，不受前面阶段影响）
- **期望结果**：
  - 每个角色使用匹配的模型和工具集
  - Reviewer 不会"看到"前面阶段的对话上下文
  - 资源利用更高效（文档编写不占用高成本模型）

### 场景 2：存量项目无缝过渡

- **角色**：已有 SDD 项目维护者
- **前置条件**：项目已有 AGENTS.md，但未配置 `role_to_profile`
- **操作流程**：
  1. 不修改 AGENTS.md（无 `role_to_profile` 配置）
  2. 正常启动 SDD 流程
  3. 编排器检测到无 Profile 配置，回退到当前委托模式
- **期望结果**：
  - 行为与变更前完全一致
  - 不影响任何正在进行的 SDD 变更
  - 用户可在任意时间通过添加配置启用 Profile 模式

### 场景 3：Reviewer 独立评审防止自我妥协

- **角色**：SDD Reviewer Agent
- **前置条件**：
  - Coder 阶段已完成所有 Task，代码已提交到 `feat/007-profile-delegation` 分支
  - Reviewer Profile（sdd-reviewer）已配置为独立模型 + 独立会话
- **操作流程**：
  1. Orchestrator 从 `CODER_CHECK` 推进到 `REVIEWER_ENTRY`
  2. Orchestrator 读取 AGENTS.md → reviewer role 映射到 `sdd-reviewer` Profile
  3. 调用 `delegate_task(profile="sdd-reviewer", goal="三阶段评审...")`
  4. Reviewer 在新会话中启动，看不到 Coder 阶段的对话上下文
  5. Reviewer 仅基于 Spec → Design → 代码 diff → 完成报告 进行评审
  6. 输出 review-report.md，结论为 passed/conditional/failed
- **期望结果**：
  - Reviewer 不会看到编码阶段的尝试、修正过程，避免"同情分"
  - 评审意见完全基于产物和代码本身
  - 如果 review failed，打回 Coder 重新进入 `CODER_ENTRY`

---

## 功能范围

### In Scope（本次包含）

| 编号 | 功能 | 说明 |
|:---:|------|------|
| F1 | **3 个 Hermes Profile 定义** | sdd-flash（PO/BA/QA）、sdd-pro（Architect/Coder）、sdd-reviewer（Reviewer），含模型、预加载 Skills、工具集 |
| F2 | **AGENTS.md `role_to_profile` 配置** | 新增配置段，定义 role → profile 映射关系，支持默认值和项目级覆盖 |
| F3 | **Orchestrator Profile 感知委托** | `delegate_task` 调用时根据 role 自动选择 Profile，传递到委托上下文 |
| F4 | **sdd-init Profile 创建** | 升级模式（--upgrade）自动执行 `hermes profile create` 创建 3 个 Profile |
| F5 | **向后兼容** | AGENTS.md 无 `role_to_profile` 时保持原委托行为，不指定 Profile |
| F6 | **delegate-protocol.md 更新** | Hermes v2.1 扩展章节从 "Planned" 更新为正式规范 |
| F7 | **orchestrator.py Profile 集成** | 脚本层支持读取 `role_to_profile` 映射并传递给 `delegate_task` |
| F8 | **sdd-orchestrator SKILL.md 版本更新** | v2.0.3 → v2.1.0，新增 Profile 委托章节和集成说明 |

### Out of Scope（本次不包含）

- ❌ **Profile 的模型自动切换**：3 个 Profile 的模型在创建时固定，运行时不变（用户可手动 `hermes profile` 调整）
- ❌ **备用模型自动切换**：kimi-k2.5 / glm-5 等备用模型的自动降级切换不在本次范围
- ❌ **运行时 Profile 动态创建**：不实现"根据变更类型自动创建临时 Profile"
- ❌ **Cross-Profile 上下文共享**：不实现 Profile 间的上下文传递机制（各 Profile 独立会话）
- ❌ **Profile 级并发委托**：不实现同一阶段的并行多 Profile 委托（如 3 个 Coder 同时工作）
- ❌ **Profile 健康监控**：不实现 Profile 的可用性检测和自动恢复
- ❌ **Gateway 平台的 Profile 感知**：本次仅覆盖 CLI 模式的委托，Gateway 模式适配不在范围

---

## 非功能需求（NFR）

| 类别 | 要求 | 指标 |
|------|------|------|
| 性能 | Profile 选择不增加委托延迟 | 委托调用额外延迟 < 100ms |
| 安全 | 最小权限原则 | 每个 Profile 仅授予其角色所需的最小工具集 |
| 可用性 | 无配置时自动回退 | 缺少 `role_to_profile` 时 100% 回退到当前行为 |
| 可维护性 | 配置清晰可读 | AGENTS.md 新增配置段不超过 20 行 |
| 可扩展性 | 支持未来新增角色 | 新增 Profile 只需添加一行映射配置 |

---

## 6 个角色对应的 Profile 设计

### Profile 总览

| Hermes Profile | 适用角色 | 模型 | 核心定位 |
|:---|:---|:---|:---|
| `sdd-flash` | PO、BA、QA | `deepseek/deepseek-v4-flash` | 快速文档产出，低延迟低成本 |
| `sdd-pro` | Architect、Coder | `deepseek/deepseek-v4-pro` | 高质量设计与编码 |
| `sdd-reviewer` | Reviewer | `deepseek/deepseek-v4-pro` | 独立会话，零上下文污染评审 |

### Profile 1: `sdd-flash`（PO / BA / QA）

| 配置项 | 值 | 说明 |
|:---|:---|:---|
| **模型** | `deepseek/deepseek-v4-flash` | 快速稳定，文档/需求/测试编写首选 |
| **预加载 Skills** | `po-agent`, `ba-agent`, `qa-agent`, `sdd-orchestrator` | 启动时自动加载，确保代理知道自己是哪个角色 |
| **工具集** | `file`, `skills`, `terminal`(read-only*) | 文件读写、技能加载、终端（仅读取命令） |
| **适用角色** | PO、BA、QA | 这三个角色以文档产出为主，无需代码执行权限 |

> *terminal read-only：仅允许 `cat`、`ls`、`grep`、`wc` 等非破坏性命令

### Profile 2: `sdd-pro`（Architect / Coder）

| 配置项 | 值 | 说明 |
|:---|:---|:---|
| **模型** | `deepseek/deepseek-v4-pro` | 高质量编码、技术设计必备 |
| **预加载 Skills** | `architect-agent`, `coder-agent`, `sdd-orchestrator` | 启动时自动加载 |
| **工具集** | `file`, `terminal`, `skills`, `github`, `web` | 全权限终端、Git 操作、代码搜索 |
| **适用角色** | Architect、Coder | 需要代码生成、构建、测试、Git 操作 |

### Profile 3: `sdd-reviewer`（Reviewer）

| 配置项 | 值 | 说明 |
|:---|:---|:---|
| **模型** | `deepseek/deepseek-v4-pro` | 高质量评审需要同等级模型 |
| **预加载 Skills** | `reviewer-agent`, `sdd-orchestrator` | 独立加载，不与其他角色共享会话 |
| **工具集** | `file`, `terminal`, `skills`, `github` | 代码阅读、Diff 查看、构建验证、Git 操作 |
| **适用角色** | Reviewer | **独立会话**——看不到 Coder 阶段的对话上下文 |

### Role → Profile 映射表

```
role_to_profile:
  po: sdd-flash
  ba: sdd-flash
  architect: sdd-pro
  coder: sdd-pro
  reviewer: sdd-reviewer
  qa: sdd-flash
```

### 模型分级策略

```
文档密集型（PO/BA/QA）  → DeepSeek-v4-flash  ← 低成本、低延迟
编码密集型（Architect）  → DeepSeek-v4-pro    ← 高质量设计
编码密集型（Coder）      → DeepSeek-v4-pro    ← 高质量编码
独立评审（Reviewer）     → DeepSeek-v4-pro    ← 独立会话 + 高质量
```

---

## 需修改的源文件清单

本次变更是对**现有文件**的修改，不创建新的 SKILL.md 文件。

| # | 文件路径 | 修改类型 | 变更内容 |
|:--:|------|:---:|------|
| 1 | `AGENTS.md` | 追加 | 新增 `role_to_profile` 映射配置段（约 15 行） |
| 2 | `skills/sdd/sdd-orchestrator/SKILL.md` | 修改 | 版本号 v2.0.3 → v2.1.0；更新 "Hermes v2.1.0 Profile 集成" 章节；新增 Profile 委托实践说明 |
| 3 | `skills/sdd/sdd-orchestrator/references/delegate-protocol.md` | 修改 | "Hermes v2.1 扩展" 章节从 "Planned" 更新为正式规范；补充 Profile 选择算法和回退逻辑 |
| 4 | `skills/sdd/sdd-orchestrator/scripts/orchestrator.py` | 修改 | 新增 `load_profile_mapping()`；修改 `delegate_agent()` 支持 Profile 参数；新增 `get_profile_for_role()` 方法 |
| 5 | `skills/sdd/sdd-init/SKILL.md` | 追加 | 新增 Step A2.7: 创建 3 个 Hermes Profile（`hermes profile create`）；升级模式（Step B）新增 Profile 检测与创建 |
| 6 | `skills/sdd/shared/sdd-state-schema.md` | 修改 | `.sdd-state.json` Schema 新增 `profile` 字段（可选） |
| 7 | `docs/current/prd.md` | 修改 | 更新项目基线描述，反映 Profile 委托能力 |
| 8 | `docs/current/README.md` | 修改 | 更新变更历史和架构概览 |

> **不修改的文件**：各角色 Agent 的 SKILL.md（po-agent、ba-agent 等）——它们不需要知道 Profile 的存在，Profile 的绑定是透明的基础设施层。

---

## 验收标准（高层级）

1. **AGENTS.md 配置生效**：人工设置 `role_to_profile.po: sdd-flash` 后，启动 PO 阶段时使用 `sdd-flash` Profile 委托
2. **向后兼容验证**：删除 AGENTS.md 中的 `role_to_profile` 配置段后，SDD 流程正常运行（不指定 Profile）
3. **Profile 不存在回退**：配置了不存在的 Profile 名称时，回退到当前委托模式并输出警告
4. **sdd-init 自动创建 Profile**：运行 `sdd-init --upgrade` 后，`hermes profile list` 中可见 `sdd-flash`、`sdd-pro`、`sdd-reviewer` 三个 Profile
5. **Reviewer 独立会话**：Reviewer 委托看不到 Coder 阶段的对话上下文（通过检查委托上下文中的 prerequisites 字段验证）
6. **orchestrator.py 可执行**：`python scripts/orchestrator.py start "测试功能"` 执行正常，输出中包含 Profile 信息
7. **delegate-protocol.md 状态更新**：文档中不再出现 "Planned" 标记，"Hermes v2.1 扩展" 章节包含完整规范
8. **工具集最小权限**：`sdd-flash` Profile 的工具集不包含 `github` 和写入类 `terminal` 命令

---

## 风险与假设

### 风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|:---:|------|
| Profile 创建失败（Hermes 未正确安装） | 阻断部署 | 低 | sdd-init 检测 `hermes profile` 命令可用性，不可用时跳过并提示手动创建 |
| `delegate_task` 不支持 Profile 参数 | 阻断核心功能 | 中 | 先确认 Hermes v2.1.0 `delegate_task` 的 API 签名；若不支持则用 `hermes --profile` 命令行方式降级 |
| DeepSeek-v4-flash 不稳定 | PO/BA/QA 阶段延迟 | 低 | 当前 flash 模型是主用模型，已验证稳定 |
| AGENTS.md 配置格式歧义引发解析错误 | 委托失败 | 低 | 使用标准 YAML 格式，与现有 AGENTS.md 风格一致 |
| Profile 间 Skills 同步问题 | 使用过期 Skill | 中 | 所有 Profile 共享 `~/.hermes/skills/sdd/` 目录，Skill 更新后所有 Profile 自动生效 |

### 假设

- **A1**：Hermes v2.1.0 的 `delegate_task` 工具支持 `profile` 参数（需在实现前确认 API）
- **A2**：`hermes profile create` 命令可用且支持 `--clone-from`（从默认 Profile 克隆基础配置）
- **A3**：DeepSeek-v4-flash 和 DeepSeek-v4-pro 在用户环境中均可访问（API key 已配置）
- **A4**：所有 6 个 SDD 角色 Agent 的 SKILL.md 已正确安装在 `~/.hermes/skills/sdd/` 下
- **A5**：Profile 的 `skills` 预加载配置不会覆盖 Agent 内部的 `skill_view()` 动态加载

---

## 成功指标

| 指标 | 目标值 | 测量方式 |
|------|:---:|------|
| Profile 委托成功率 | 100% | 记录每次 `delegate_task` 的 Profile 参数是否生效 |
| Reviewer 独立评审率 | 100% | 验证 Reviewer 委托的会话是否为独立会话（无前置阶段对话历史） |
| 向后兼容覆盖率 | 100% | 无 `role_to_profile` 配置时所有现有 SDD 测试用例通过 |
| 工具集合规率 | 100% | 各 Profile 工具集不超出设计范围 |
| sdd-init Profile 创建成功率 | ≥95% | `hermes profile list` 验证 3 个 Profile 存在 |

---

> **下一阶段**：转入 BA 阶段，产出 Spec 文档，细化每个 Profile 的技术规格和 AC（Given-When-Then 格式）。
