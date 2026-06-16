# Spec — SDD 框架全量一致性修复（D1-D10）

> **Specification Document — 功能规格与验收标准**
> Change ID: `001-修复sdd框架一致性缺陷-quirks-md缺失-agent`
> 版本：1.0 | 状态：Draft

---

## 功能概述

修复 SDD 框架的 **10 项一致性缺陷**（D1-D10），核心目标：
1. 补全缺失文件（QUIRKS.md）和清理 AGENTS.md（去文档化、统一版本/模型引用）
2. 升级源码 skills/sdd/sdd-orchestrator/ 到 v2.6.0（Kanban+Profile），补全缺失参考文件
3. 迁移 6 个旧参考文件的 delegate_task 引用至 Kanban+Profile
4. 实现跨阶段上下文传播机制（D9）
5. 修复 Profile API Key 配置问题（D10）

---

## 详细需求

### Requirement R1: 项目根目录补全与修复

**描述**：QUIRKS.md 缺失会导致 L1 门禁阻断；AGENTS.md 版本和注释不匹配会迷惑新用户。

**输入**：`templates/QUIRKS.md`

**输出**：`/project/root/QUIRKS.md`（存在、合规）

**约束**：不修改 CONSTITUTION.md；QUIRKS.md 内容必须与 AGENTS.md 声明的约束一致

---

### Requirement R2: AGENTS.md 精简与去文档化

**描述**：AGENTS.md 目前 174 行，其中 ~120 行为 Profile 架构概述、Soul 模式配置、Workspace 配置规范等纯文档内容。这些应移至 `docs/current/architecture.md`。AGENTS.md 应恢复为纯配置文件。

**输入**：当前 AGENTS.md（174 行）

**输出**：AGENTS.md（≤ 50 行，纯配置）；docs/current/architecture.md（补充 Profile+Soul 章节）

**约束**：role_to_profile 映射保持不变；constitution 和 quirks 声明路径不变

---

### Requirement R3: 源码 SKILL.md 升级至 v2.6.0（Kanban+Profile）

**描述**：`/root/workspace/hermes-harness/skills/sdd/sdd-orchestrator/SKILL.md` 当前为 v2.1.0，全篇 delegate_task 引用。需升级至 v2.6.0，与 installed skill 同步。同步 8 个缺失参考文件。

**输入**：当前 SOURCE SKILL.md（v2.1.0）+ installed SKILL.md（v2.6.0）

**输出**：SOURCE SKILL.md 升级，8 个参考文件补全

**约束**：版本号对齐（v2.6.0）；零 delegate_task 引用；新增 Kanban+Profile 委托章节

---

### Requirement R4: 参考文件 delegate_task 迁移

**描述**：6 个参考文件仍引用 delegate_task 协议，需替换为 Kanban+Profile 描述。

**文件列表**：
- `references/delegate-protocol.md`（10 处）
- `references/state-machine.md`（11 处）
- `references/incremental-mode.md`（2 处）
- `references/interrupt-recovery.md`（2 处）
- `references/skill-maintenance-pattern.md`（2 处）
- `references/pr-and-review-flow.md`（1 处）

**约束**：保持文件结构和章节标题不变，仅替换委托机制描述；添加 "Kanban+Profile" 标注

---

### Requirement R5: 跨阶段上下文传播机制

**描述**：当前 orchestrator 创建 Kanban 任务时，`--body` 仅包含 `change_id` + `change_dir` + `stage`，子 Agent 在独立会话执行时缺少前一阶段的决策依据。

**输出**：orchestrator 的 `delegate_agent()` 生成的 task body 增加 3 个元素：
- 前置产物摘要（PRD 的核心假设、Spec 的 AC 列表、Design 的方案选择理由）
- 关键决策记录（ADRs）
- 约束传递（哪些规则不能违反）

**约束**：body 长度不超过 2000 tokens；不需要改 Hermes 源码

---

### Requirement R6: Profile API Key 配置修复

**描述**：6 个 sdd-* Profile 的 config.yaml 都使用已过期的 DeepSeek API Key，导致 Kanban Worker 启动失败。

**输入**：6 个 Profile config.yaml（路径 `~/.hermes/profiles/sdd-*/config.yaml`）

**输出**：Profile config.yaml 修复（移除过期 api_key 或替换为有效组合）

**约束**：不硬编码任何项目路径；Reviewer 保持异构评审模式

---

## Acceptance Criteria（验收标准）

### 场景组：R1 — 项目根目录补全

#### Scenario AC1: QUIRKS.md 存在且合规
- **WHEN** 运行 `test -f /root/workspace/hermes-harness/QUIRKS.md`
- **THEN** 文件存在
- **AND** 文件内容非空
- **AND** 文件符合 AGENTS.md 引用的约束规范

#### Scenario AC2: AGENTS.md 版本号对齐
- **WHEN** 读取 AGENTS.md 的 version 字段
- **THEN** version 为 "2.6.0"
- **AND** 与 sdd-orchestrator SKILL.md 的 version 一致

#### Scenario AC3: AGENTS.md 模型注释与实际一致
- **WHEN** 读取 AGENTS.md role_to_profile 段的注释
- **THEN** 注释中的模型名与 Profile config.yaml 的 default 模型一致
- **AND** 不出现已弃用模型名（如 doubao-seed-2.0-pro、glm-5.1）

---

### 场景组：R2 — AGENTS.md 精简

#### Scenario AC4: AGENTS.md 移除文档内容
- **WHEN** 统计 AGENTS.md 行数
- **THEN** ≤ 60 行
- **AND** 不包含 Profile 架构概述、Soul 模式配置、Workspace 配置规范等纯文档章节

#### Scenario AC5: AGENTS.md 包含最小必要配置
- **WHEN** 读取 AGENTS.md
- **THEN** 包含：项目信息、技术栈、路径约定、SDD 配置（flow_engine + default_flow_level）、项目约束（constitution + quirks）、role_to_profile 映射
- **AND** 不包含 profile_enabled/soul_enabled/workspace_type（这些是运行时配置，非常量）

#### Scenario AC6: 文档内容已迁移到 architecture.md
- **WHEN** 读取 `docs/current/architecture.md`
- **THEN** 包含 Profile 架构概述章节
- **AND** 包含 Soul 模式配置章节
- **AND** 包含 Workspace 配置规范章节

---

### 场景组：R3 — 源码 SKILL.md 升级

#### Scenario AC7: SOURCE SKILL.md 升级至 v2.6.0
- **WHEN** 读取 `/root/workspace/hermes-harness/skills/sdd/sdd-orchestrator/SKILL.md` 的 frontmatter
- **THEN** version 字段为 2.6.0
- **AND** tags 包含 kanban、profile
- **AND** 不包含 delegate 标签

#### Scenario AC8: delegate_task 引用清零
- **WHEN** grep -c "delegate_task" /root/workspace/hermes-harness/skills/sdd/sdd-orchestrator/SKILL.md
- **THEN** 结果为 0
- **AND** grep -c "kanban" 同一文件 > 0

#### Scenario AC9: 8 个缺失参考文件已补全
- **WHEN** 检查 references/ 目录
- **THEN** 以下文件存在：
  - kanban-profile-integration.md
  - profile-soul-architecture.md
  - 4-layer-document-consistency.md
  - phase-consistency-audit.md
  - sdd-for-planning.md
  - model-output-truncation-bug.md
  - model-selection-production-validation.md
  - orchestrator-fix-patterns.md

#### Scenario AC10: install.sh 安装得到正确版本
- **WHEN** 运行 `cd /tmp && git clone https://github.com/NEU-JING/hermes-harness.git && ./install.sh --force 2>/dev/null`
- **THEN** `~/.hermes/skills/sdd/sdd-orchestrator/SKILL.md` 的 version 为 2.6.0
- **AND** 包含 "Kanban + Profile" 章节

---

### 场景组：R4 — 参考文件迁移

#### Scenario AC11: delegate-protocol.md 带头迁移
- **WHEN** 读取 `references/delegate-protocol.md`
- **THEN** 文件头部添加 `⚠️ 已迁移：原 delegate_task 协议已被 Kanban+Profile 替代`
- **AND** 核心章节描述改用 `hermes kanban create --assignee <profile>`
- **AND** 保留旧内容作为历史参考（用 `> **历史存档**` 标注）

#### Scenario AC12: 5 个参考文件同步更新
- **WHEN** 检查 state-machine.md、incremental-mode.md、interrupt-recovery.md、skill-maintenance-pattern.md、pr-and-review-flow.md
- **THEN** delegate_task 引用全部替换为 Kanban+Profile 对应描述
- **AND** 保持文件结构和章节连续性不受破坏

---

### 场景组：R5 — 上下文传播

#### Scenario AC13: BA 阶段 task body 包含 PRD 摘要
- **WHEN** orchestrator 创建 BA_ENTRY Kanban 任务
- **THEN** body 包含：
  - PRD 核心假设（≤ 200 字）
  - 变更范围摘要（D1-D10 列表）
  - 前置产物路径（prd.md 绝对路径）

#### Scenario AC14: Architect 阶段 task body 包含 Spec 关键信息
- **WHEN** orchestrator 创建 ARCHITECT_ENTRY Kanban 任务
- **THEN** body 包含：
  - AC 列表摘要（编号 + 场景名）
  - 关键设计约束（来自 Spec 的约束段）
  - 前置产物路径（spec.md 绝对路径）

#### Scenario AC15: Coder 阶段 task body 包含 Design 决策
- **WHEN** orchestrator 创建 CODER_ENTRY Kanban 任务
- **THEN** body 包含：
  - 方案选择理由（哪个方案被选中及其原因）
  - 架构决策记录（ADRs）
  - 关键风险标注

---

### 场景组：R6 — Profile API Key

#### Scenario AC16: Profile 无硬编码过期密钥
- **WHEN** 检查 `~/.hermes/profiles/sdd-*/config.yaml`
- **THEN** 不含 `api_key` 字段（继承主配置）
- **OR** api_key 对应的 Provider 可成功认证

#### Scenario AC17: Profile 模型可用性验证
- **WHEN** 运行 `echo "test" | hermes -p sdd-ba chat -q "Hello"` 和 `echo "test" | hermes -p sdd-reviewer chat -q "Hello"`
- **THEN** 2 秒内返回非空响应
- **AND** 不出现 401/403 认证错误

---

## 非功能需求细化

| 类别 | 原始 NFR | 细化指标 | 验证方式 |
|------|---------|---------|---------|
| 兼容性 | install.sh 安装后 SKILL.md 正确 | installed 版本与 repo 源码版 SKILL.md 内容 diff 为零（除路径差异） | `diff <(grep -v path installed) <(grep -v path source)` |
| 可维护性 | AGENTS.md 不包含冗余文档 | 下次变更只需修改 AGENTS.md 的 role_to_profile 映射，不改文档部分 | 架构文档在 `docs/current/` 中 |
| 可测试性 | Profile API Key 验证可编程化 | 提供验证脚本 | `scripts/validate-profile-isolation.sh` 包含 API Key 验证 |
