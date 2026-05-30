# Spec — Hermes Harness（SDD 通用开发机制）

> **Specification Document — 功能规格与验收标准**
> 版本：1.0 | 最后更新：2026-05-25

---

## R1: 流程编排器

### 概述
`sddsdd-orchestrator` 是整个流程的中央调度器，负责流程判定、阶段调度、门禁检查和归档。

### AC1.1 流程判定
- **Given** 用户发起变更描述
- **When** 编排器加载 `shared/flow-level-rules.md`
- **Then** 输出流程级别（Quick/Standard/Enhanced）及对应阶段列表

### AC1.2 阶段调度
- **Given** 当前阶段完成
- **When** 编排器调用 sdd-structure-lint 检查门禁
- **Then** 门禁通过 → 加载下一角色 Skill → 执行；门禁不通过 → 阻断并输出错误报告

### AC1.3 中断恢复
- **Given** Agent 重启或用户中断
- **When** 编排器读取 `.sdd-state.json`
- **Then** 产物完整 → 从当前阶段继续；产物不完整 → 回退到上一个已完成阶段；无产物 → 从 Phase 0 重新开始

### AC1.4 规则检查
- **Given** 各阶段切换时机
- **When** 编排器加载 `shared/sdd-rules.md`（R1-R10）
- **Then** Coder 启动前检查 R1（spec.md 存在）；Reviewer 后检查 R4（review-report.md）；QA 阶段检查 R6/R7/R9；归档前检查 R10（PR 合规）

---

## R2: 角色 Skill 系统

### 概述
8 个角色 Skill，每个包含：触发条件、前置依赖、执行流程、禁止行为、退出条件。

### AC2.1 PO Agent
- **Given** 用户发起新变更
- **When** 编排器调度 PO Agent
- **Then** 产出 `prd.md`（含背景与目标、用户场景、功能范围、非功能需求、验收标准、风险与假设）

### AC2.2 BA Agent
- **Given** PRD 已产出且用户确认
- **When** 编排器调度 BA Agent
- **Then** 产出 `spec.md`（含 AC 编号 Given-When-Then 格式）

### AC2.3 Architect Agent
- **Given** Spec 已产出且用户确认
- **When** 编排器调度 Architect Agent
- **Then** Standard/Enhanced 流程产出 ≥2 个方案对比；最终产出 `design.md` + `tasks.md`

### AC2.4 Coder Agent
- **Given** Design + Tasks 已产出且用户确认
- **When** 编排器调度 Coder Agent
- **Then** 按 Task 逐个执行 TDD（RED→GREEN→REFACTOR）；每个 Task 完成后输出 Completion Report；禁止跳过测试直接写实现

### AC2.5 Reviewer Agent
- **Given** 代码已提交
- **When** 编排器调度 Reviewer Agent
- **Then** 执行三阶段评审（Spec 合规/代码质量/架构一致性）；产出 `review-report.md`（含结论 + 严重级别）

### AC2.6 QA Agent
- **Given** Review 通过或有条件通过
- **When** 编排器调度 QA Agent
- **Then** 产出 AC 覆盖矩阵；执行全量测试（Quick 流程跳过 E2E）；产出 `qa-report.md`；QA 不通过 ≤4 轮回退 Coder

### AC2.7 角色 Skill 格式
- **Given** 任意角色 Skill 文件
- **When** 加载该 Skill
- **Then** 必含 YAML frontmatter（name/description/version）；必含章节（触发条件/前置依赖/执行流程/禁止行为/退出条件）；SKILL.md ≤100 行

---

## R3: 项目初始化与升级

### 概述
`sddsdd-init` 支持新项目交互式搭建和存量项目无痛升级。

### AC3.1 新项目初始化
- **Given** 项目目录无 AGENTS.md 或 AGENTS.md 中无 `flow_engine` 字段
- **When** 用户运行 sdd-init
- **Then** 交互式询问（项目名称/技术栈/数据库/流程级别）；自动生成 AGENTS.md、CONSTITUTION.md、QUIRKS.md、docs/{changes,current,archive}/、.pre-commit-config.yaml、pytest.ini+conftest（Python 项目）

### AC3.2 存量项目升级
- **Given** 项目已有 AGENTS.md 但结构不完整
- **When** 用户运行 sdd-upgrade
- **Then** 扫描现有状态 → 生成升级计划（新建/移动/修改/冲突）→ 用户确认后执行；不删除任何现有文件；移动操作用 git mv

### AC3.3 升级冲突检测
- **Given** 存量项目已有 .pre-commit-config.yaml 或自定义 post-commit hook
- **When** sdd-upgrade 检测到冲突
- **Then** 标注为 ⚠️ 冲突项，由用户选择保留/覆盖/合并

---

## R4: 结构验证

### 概述
`sddsdd-structure-lint` 提供三级验证，在编排器启动时和阶段交接前自动运行。

### AC4.1 Level 1 — 文件级
- **Given** 项目目录
- **When** 执行 Level 1 检查
- **Then** 验证 AGENTS.md/CONSTITUTION.md/QUIRKS.md 存在；验证 docs/{changes,current,archive}/ 目录存在

### AC4.2 Level 2 — 交接级
- **Given** 当前阶段
- **When** 阶段切换前执行 Level 2 检查
- **Then** 验证当前阶段必选产物存在（如 Architect → design.md + tasks.md）

### AC4.3 Level 3 — 内容级
- **Given** 归档前
- **When** 执行 Level 3 检查
- **Then** 验证 PRD 含必要章节、Spec AC 编号连续、Design 方案数 ≥2、Tasks 表格格式正确、Review Report 含结论和严重级别、QA Report 含 AC 覆盖矩阵

### AC4.4 Lint 不通过处理
- **Given** Lint 检查失败
- **When** 任一 Level 不通过
- **Then** 阻断流程，输出标准化错误报告（含严重级别 + 修复建议）


## R5: 门禁卡点与闭环

### 概述
SDD 流程包含 3 个用户门禁和 2 个自动回退闭环。

### AC5.1 用户确认门禁
- **Given** PO / BA / Architect 阶段完成
- **When** 产物产出
- **Then** 必须用户确认才能进入下一阶段；用户修改则回到当前阶段重新产出

### AC5.2 Reviewer ↔ Coder 闭环
- **Given** Reviewer 评审不通过
- **When** 第 1 轮不通过 → Coder 修复
- **Then** 第 2 轮仍不通过 → 熔断，用户介入决策；通过则进入 QA

### AC5.3 QA ↔ Coder 闭环
- **Given** QA 测试不通过
- **When** ≤4 轮不通过 → Coder 修复
- **Then** 第 5 轮仍不通过 → 熔断，用户介入决策

### AC5.4 用户验收打回
- **Given** 用户验收不通过
- **When** 场景实现不正确 → 按问题分类
- **Then** 需求问题 → 打回 PO；设计问题 → 打回 Architect；代码问题 → 打回 Coder；修复循环 ≤2 轮


## R6: Git 工作流集成

### AC6.1 Feature 分支
- **Given** Coder 阶段开始
- **When** 代码变更
- **Then** 必须在 `feat/{change-id}-{description}` 分支上工作；禁止直接 commit main

### AC6.2 PR 生命周期
- **Given** Coder 完成
- **When** 代码 push
- **Then** 创建 PR（保持 OPEN）→ Reviewer 评审 → QA 验证 → 用户验收 → 验收通过后 squash merge

### AC6.3 R10 归档检查
- **Given** 归档阶段
- **When** 执行 `git branch --show-current`
- **Then** 非 main 分支 → 阻断；无 merge commit → 阻断；`--bypass-r10` 标志 → 记录 HOTFIX 后放行


## R7: 基线文档维护

### AC7.1 基线融合
- **Given** 变更归档
- **When** 执行 Phase 8 归档
- **Then** PRD → 融合到 `docs/current/prd.md` 的功能范围章节；Spec → 融合到 `docs/current/spec.md` 的新增需求；Design → 融合到 `docs/current/design.md` 的架构变更；变更历史追加追溯记录

### AC7.2 基线 = 生产全貌
- **Given** `docs/current/` 目录
- **When** 任意时刻查看
- **Then** 反映当前生产版本的完整状态，非变更日志堆砌


## R8: 安装与分发

### AC8.1 一键安装
- **Given** 已 clone hermes-harness 仓库
- **When** 运行 `./install.sh`
- **Then** Skills 复制到 `~/.hermes/skills/sdd/`；包含 shared/ 和 references/ 子目录

### AC8.2 覆盖更新
- **Given** 已有安装
- **When** 运行 `./install.sh --force`
- **Then** 覆盖已有安装；列出所有已安装 Skill 和 shared 文件

### AC8.3 非 Hermes Agent 兼容
- **Given** 任意支持 system prompt 的 Agent
- **When** 加载 `skills/sdd/` 目录内容
- **Then** 纯 Markdown 格式，无平台锁定依赖


## R9: 项目配置

### AC9.1 AGENTS.md 最小格式
- **Given** 任意接入 SDD 的项目
- **When** 编排器启动
- **Then** AGENTS.md 必含：项目信息（name/description）、技术栈、路径约定、flow_engine、constitution 引用

### AC9.2 规则覆盖
- **Given** 项目有特殊约束
- **When** AGENTS.md 声明 `convention_overrides.disable_rules` 或 `custom_rules`
- **Then** 编排器在相应时机加载并执行覆盖规则；不影响通用规则的其他项目


## R10: 增量交付（Phase 级交付）

### 概述
支持大型变更分 Phase 独立交付，每 Phase 完成后可验收上线。

### AC10.1 Phase 状态追踪
- **Given** 增量模式启用
- **When** 创建 `.sdd-state.json`
- **Then** 包含 `phase_status` 字段，记录每个 Phase 的 `status`（coding_done/review_passed/qa_passed/accepted）；包含 `sub_phases_completed` 数组；包含 `current_sub_phase` 字段

### AC10.2 Phase 依赖检查
- **Given** Phase N 开始前
- **When** 执行门禁检查
- **Then** 检查 `phase_status[Phase N-1].status == "accepted"`；依赖未满足 → 阻断并提示先完成前一 Phase

### AC10.3 Phase 内嵌套 Review
- **Given** Phase N Coding 完成
- **When** 触发 Phase Reviewer
- **Then** 执行该 Phase 的代码评审；产出合并到主 `review-report.md`（Phase 章节）

### AC10.4 Phase 内嵌套 QA
- **Given** Phase N Review 通过
- **When** 触发 Phase QA
- **Then** 执行该 Phase 的测试（含回归测试）；产出合并到主 `qa-report.md`（Phase 章节）

### AC10.5 Tasks.md Phase 标记
- **Given** Architect 产出 tasks.md
- **When** 启用增量模式
- **Then** 每个 Phase 标题含 `[可独立交付]` 或 `[依赖 Phase X]`；每个 Phase 含交付标准（测试数、AC 覆盖）；每个 Phase 含检查点（Review/QA/用户确认）

### AC10.6 增量模式启用
- **Given** 用户发起变更
- **When** 指定 `--incremental` 或 Architect 在 tasks.md 中标记 Phase
- **Then** Orchestrator 进入增量流程；每 Phase 完成后询问用户是否进入下一 Phase；支持 `--phase=N` 从指定 Phase 恢复

---

## R5: 严格状态机（v2.0 新增）

### 概述
编排器维护 18 状态严格状态机，每个状态有明确的 ENTRY/EXIT 条件。

### AC5.1 状态定义
- **Given** 状态机定义
- **When** 检查任意状态
- **Then** 必含 Entry 条件、Execution、Exit 条件、Transitions

### AC5.2 状态转换
- **Given** 当前状态完成
- **When** 检查 Exit 条件 + 执行门禁
- **Then** 条件满足 → 推进到下一状态；不满足 → 保持当前状态或 BLOCKED

### AC5.3 中断恢复
- **Given** Agent 重启或流程中断
- **When** 读取 `.sdd-state.json`
- **Then** 根据 `current_state` 恢复，产物完整则继续，不完整则回退

---

## R6: 5 级门禁检查（v2.0 新增）

### 概述
每个状态转换必须通过对应 Level 的 lint 检查。

### AC6.1 L0 初始化检查
- **Given** IDLE → PO_ENTRY 转换
- **When** 执行 L0 检查
- **Then** 目录结构创建成功，状态文件初始化完成

### AC6.2 L1 基础检查
- **Given** PO/BA 阶段完成
- **When** 执行 L1 检查
- **Then** 产物文件存在、非空、格式正确

### AC6.3 L2 设计检查
- **Given** Architect 阶段完成
- **When** 执行 L2 检查
- **Then** Design/Tasks 完整、Task 拆分合理

### AC6.4 L2.5 代码检查
- **Given** Coder 阶段完成
- **When** 执行 L2.5 检查
- **Then** 所有 Task 完成、commits 存在、测试通过

### AC6.5 L3 质量检查
- **Given** Reviewer/QA 阶段完成
- **When** 执行 L3 检查
- **Then** 报告质量合格、AC 覆盖完整

### AC6.6 R10 归档检查
- **Given** 归档前
- **When** 执行 R10 检查
- **Then** PR 已合并、目录结构正确、current/ 已更新

---

## R7: Agent 委托协议（v2.0 新增）

### 概述
编排器使用 `delegate_task` 调用各角色 Agent。

### AC7.1 委托格式
- **Given** 任意阶段委托
- **When** 构建 delegate_task 参数
- **Then** 必含 goal、context（prerequisites/deliverables/constraints）、toolsets

### AC7.2 前置检查
- **Given** 委托前
- **When** orchestrator 执行前置检查
- **Then** 检查前置产物存在性、创建输出目录（不预加载 skill）

### AC7.3 Agent 自主加载
- **Given** Agent 被委托
- **When** Agent 内部执行
- **Then** 自主调用 `skill_view(name='{agent}-agent')` 加载自己的 skill

---

## R8: Skill 精简与 references 分离（v2.0.1 新增）

### 概述
SKILL.md 精简为摘要，详细内容移至 references/。

### AC8.1 SKILL.md 行数
- **Given** 任意角色 Skill
- **When** 统计 SKILL.md 行数
- **Then** ≤150 行（不含 references/）

### AC8.2 references 完整性
- **Given** SKILL.md 声明了 references
- **When** 通过 `skill_view(name, file_path)` 加载
- **Then** 文件存在、路径正确、内容完整

### AC8.3 链接有效性
- **Given** SKILL.md 中的 references 链接
- **When** 点击或解析
- **Then** 指向正确的 references/ 文件

---

> **版本更新记录**：
> - v1.0 (2026-05-25): 初始规格（001-sdd-init）
> - v2.0 (2026-05-30): 严格状态机、5 级门禁、delegate 协议（006-orchestrator-v2）
> - v2.0.1 (2026-05-30): Skill 精简、references 分离（007-orchestrator-refine）
> - v2.0.2 (2026-05-30): Agent 自主加载模式（007-orchestrator-refine 快速修复）
