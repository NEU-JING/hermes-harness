# Spec: SDD 通用开发机制

> 版本：V1.0
> 日期：2026-05-24
> 作者：BA Agent
> 前置 PRD：docs/changes/001-sdd-init/prd.md
>
> ⚠️ 本文档只描述系统行为，不包含任何技术方案、API 路径、数据库表设计。

---

## 验收场景

### AC1: 新项目初始化（正常路径）

- **Given** 当前目录为空（不存在 AGENTS.md），用户触发项目初始化
- **When** 系统交互式询问项目信息（名称、技术栈、流程级别偏好），用户逐一回答
- **Then** 系统自动生成 AGENTS.md、CONSTITUTION.md、QUIRKS.md、docs/changes/、docs/current/、docs/archive/ 目录。生成完成后提示"SDD 就绪"

### AC2: 存量项目升级（正常路径）

- **Given** 当前目录已有 AGENTS.md 但不包含 flow_engine 字段，且目录下有散落的 PRD 文档和代码
- **When** 用户触发升级，系统分析现有文件后输出迁移计划（列出哪些文件移动、哪些新建、哪些保留、哪些冲突），用户确认
- **Then** 系统执行迁移：散落文档移动到约定路径（使用 git mv 保留历史）、补充缺失的 CONSTITUTION.md 和 QUIRKS.md、更新 AGENTS.md 增加 flow_engine 等字段。执行后提示"升级完成"

### AC3: 存量升级用户拒绝计划（边界条件）

- **Given** 存量项目状态与 AC2 相同
- **When** 系统输出迁移计划，用户选择拒绝
- **Then** 系统不执行任何文件操作，提示"升级已取消"

### AC4: 存量升级检测到用户修改的文件冲突

- **Given** 存量项目中有文件既在迁移范围内，又被用户本地修改过（git status 显示 modified）
- **When** 系统生成迁移计划
- **Then** 该文件在计划中标记为"冲突：需人工决策"，不自动移动或覆盖

### AC5: 再次初始化已就绪项目

- **Given** 当前目录已有完整的 AGENTS.md（含 flow_engine 字段）和目录骨架
- **When** 用户触发初始化
- **Then** 系统提示"项目已处于 SDD 就绪状态，无需重复初始化"

---

### AC6: 完整 SDD 流程调度（正常路径）

- **Given** 项目处于 SDD 就绪状态，用户开始一个新变更
- **When** 编排器按 PRD → Spec → Design → Tasks → Implement → Review → QA → 验收 → 归档 顺序调度
- **Then** 每个阶段完成后自动触发下一阶段，阶段交接前执行合规检查。全部通过后自动归档

### AC7: 流程级别判定 — Quick

- **Given** 用户提出一个 bug 修复任务（预计 ≤ 2 小时）
- **When** 编排器分析任务特征（规模、影响范围、是否需要变更数据库）
- **Then** 判定为 Quick 级别，跳过 Spec、Design、Review 阶段，直接进入 Implement → QA

### AC8: 流程级别判定 — Standard

- **Given** 用户提出一个新功能（预计 2-20 小时），不涉及数据库结构变更
- **When** 编排器分析任务特征
- **Then** 判定为 Standard 级别，按完整流程执行

### AC9: 流程级别判定 — Enhanced

- **Given** 用户提出一个涉及数据库结构变更或跨模块重构的功能
- **When** 编排器分析任务特征
- **Then** 判定为 Enhanced 级别，按完整流程执行，且 Design 阶段强制 Brainstorming，Review 阶段增加人工审查

### AC10: PRD 确认门禁

- **Given** PO Agent 已完成并输出 prd.md
- **When** 编排器检查门禁状态
- **Then** 流程暂停，等待用户确认。用户确认后进入 Spec 阶段。用户拒绝时注明原因，PO Agent 修改后重新提交确认

### AC11: Spec 确认门禁

- **Given** BA Agent 已完成并输出 spec.md
- **When** 编排器检查门禁状态
- **Then** 流程暂停，等待用户确认。用户确认后进入 Design 阶段。用户拒绝时注明原因，BA Agent 修改后重新提交确认

### AC12: QA 自动修复 — 4 轮内成功

- **Given** QA Agent 运行测试发现 3 个失败用例
- **When** 编排器将失败列表返回给 Coder Agent 修复，修复完成后 QA 重新运行
- **Then** 第 2 轮 QA 全部通过，流程继续进入人工验收

### AC13: QA 熔断 — 第 5 轮仍失败

- **Given** QA Agent 连续 4 轮发现失败用例，Coder Agent 已修复 4 次
- **When** 第 5 轮 QA 仍有失败
- **Then** 编排器触发熔断，流程暂停，向用户输出失败摘要和每轮修复记录，等待用户决策

### AC14: 人工验收 — 需求偏差打回 PRD

- **Given** QA 通过，用户进行人工验收
- **When** 用户发现实现的功能与原始需求不一致（需求理解偏差）
- **Then** 编排器将变更状态重置为 PRD 阶段，PO Agent 重新修改 prd.md，后续阶段重新执行

### AC15: 人工验收 — 设计缺陷打回 Design

- **Given** QA 通过，用户进行人工验收
- **When** 用户发现技术方案有缺陷（如选型不当、扩展性不足）
- **Then** 编排器将变更状态重置为 Design 阶段，Architect Agent 重新 Brainstorming 和修改 design.md，后续阶段重新执行

### AC16: 人工验收 — 代码 Bug 打回 Implement

- **Given** QA 通过，用户进行人工验收
- **When** 用户发现具体功能点的代码实现有 Bug
- **Then** 编排器将变更状态重置为 Implement 阶段（仅重置对应 Task），Coder Agent 修复后重新走 Review → QA → 验收

### AC17: 归档

- **Given** 人工验收通过，CI 全部绿色
- **When** 编排器执行归档
- **Then** 变更目录从 changes/ 移动到 archive/，current/ 目录更新为本次变更的产物

---

### AC18: PO Agent 产出 PRD

- **Given** 编排器调度 PO Agent，传入用户需求描述
- **When** PO Agent 读取项目配置（AGENTS.md + CONSTITUTION.md），加载 PRD 模板
- **Then** 产出 prd.md，包含：背景、目标、目标用户、核心功能点、Non-Goals、成功指标。文件写入 `{changes_dir}/{change-id}/prd.md`

### AC19: BA Agent 产出 Spec

- **Given** 编排器调度 BA Agent，传入已确认的 prd.md
- **When** BA Agent 读取 prd.md 和项目配置，加载 Spec 模板
- **Then** 产出 spec.md，包含：Given-When-Then 验收场景、业务规则、边界条件、错误文案、非功能需求。**不包含任何技术实现描述**

### AC20: Architect Agent 产出 Design + Tasks

- **Given** 编排器调度 Architect Agent，传入已确认的 spec.md
- **When** Architect Agent 读取 spec.md 和项目代码结构，执行 Brainstorming（≥ 2 种方案对比），加载 Design 和 Tasks 模板
- **Then** 产出 design.md（含推荐方案、数据模型、关键流程）和 tasks.md（按业务场景拆分 Task，每 Task 可独立上线）

### AC21: Coder Agent TDD 实现

- **Given** 编排器调度 Coder Agent，传入 design.md 和当前 Task
- **When** Coder Agent 按 TDD 流程（红→绿→重构）实现该 Task，完成后输出 Task Completion Report（测试数、AC 覆盖、NFR 勾选）
- **Then** 全量测试通过（新增 + 回归），Task Completion Report 写入变更目录

### AC22: Reviewer Agent 三阶段评审

- **Given** 编排器调度 Reviewer Agent，传入代码 diff 和 spec.md
- **When** Reviewer Agent 执行 Phase 1（自动化检查：lint/format/测试覆盖）、Phase 2（独立审查：对照 Design 和 NFR）、Phase 3（回归验证）
- **Then** 产出评审报告，问题按 CRITICAL / WARNING / INFO 分级

### AC23: QA Agent 触发 CI + 报告

- **Given** 编排器调度 QA Agent，传入代码和 spec.md
- **When** QA Agent 触发 CI 执行集成测试和 E2E 测试，等待 CI 结果，验证 AC 覆盖矩阵（逐条核对 spec.md 的 AC 是否都有对应用例）
- **Then** 产出 qa-report.md，包含：测试通过/失败/跳过分类、AC 覆盖状态、环境差异标记（如 SQLite skip 的用例）

---

### AC24: 项目级检查 — 通过

- **Given** 项目目录包含 AGENTS.md、CONSTITUTION.md、docs/changes/、docs/current/、docs/archive/
- **When** 合规验证在编排器启动时执行
- **Then** 检查通过，无提示

### AC25: 项目级检查 — 失败

- **Given** 项目目录缺少 CONSTITUTION.md
- **When** 合规验证执行
- **Then** 输出"缺失文件：CONSTITUTION.md"，提示"运行项目初始化以补全"，流程不继续

### AC26: 变更级检查 — change-id 格式错误

- **Given** 变更目录名为 `my-feature`（不符合 NNN-short-name 格式）
- **When** 合规验证执行
- **Then** 输出"change-id 格式错误：应为 NNN-short-name（如 001-add-login），当前为 my-feature"

### AC27: 交接级检查 — 前置产物缺失

- **Given** 编排器准备从 Spec 阶段进入 Design 阶段，但 `{changes_dir}/{change-id}/` 下没有 prd.md
- **When** 合规验证执行
- **Then** 输出"前置产物缺失：prd.md 不存在"，交接阻断

---

### AC28: 精简 AGENTS.md 配置有效

- **Given** 项目 AGENTS.md 声明了 `changes_dir: "docs/changes/"`、`flow_engine: "sdd/sdd-orchestrator"` 等字段
- **When** 编排器读取 AGENTS.md 获取项目配置
- **Then** 编排器使用声明的路径和引擎，不需要 AGENTS.md 中包含任何流程描述

### AC29: convention_overrides 覆盖默认约定

- **Given** 项目 AGENTS.md 的 `convention_overrides` 中声明了 `tasks_split_rule: "按模块拆分，禁止按技术层次拆分"`
- **When** Architect Agent 拆分 Task
- **Then** 遵循项目声明的拆分规则，而非 SDD 默认规则

---

## 业务规则

| 规则编号 | 规则描述 | 涉及场景 |
|:---:|------|:---:|
| BR1 | change-id 必须为 NNN-short-name 格式（3 位数字 + 短横线 + 英文短名） | AC26 |
| BR2 | 所有变更产物必须在 `{changes_dir}/{change-id}/` 下，归档后在 `archive/{change-id}/` | AC17, AC24-27 |
| BR3 | 阶段交接前必须通过合规检查，不通过不推进 | AC25-27 |
| BR4 | PRD 和 Spec 产出后必须经用户确认，不可自动跳过 | AC10, AC11 |
| BR5 | QA 失败时自动返回 Coder 修复，最多 4 轮；第 5 轮仍失败则熔断，等待用户决策 | AC12, AC13 |
| BR6 | 人工验收发现问题时，按类型打回：需求偏差→PRD，设计缺陷→Design，代码Bug→对应Task | AC14-16 |
| BR7 | 归档条件：人工验收通过 + 所有 CI 检查通过 | AC17 |
| BR8 | 角色 Skill 采用文档地图模式：SKILL.md 核心指令 ≤ 80 行；references 按需通过 skill_view 加载 | AC18-23 |
| BR9 | 存量项目升级时，不覆盖用户已修改的文件（git modified），冲突项标记为"需人工决策" | AC4 |
| BR10 | 每个角色 Skill 必须声明禁止行为清单，Agent 执行时不可违反 | AC18-23 |

---

## 边界条件

| 边界 | 条件 | 预期行为 | 涉及场景 |
|------|------|---------|:---:|
| 空目录初始化 | 目录下无任何文件 | 正常生成骨架 | AC1 |
| 已有 AGENTS.md 但无 flow_engine | 项目有旧版 AGENTS.md | 进入升级模式 | AC2 |
| 重复初始化 | 项目已配置 flow_engine | 提示无需重复操作 | AC5 |
| 存量升级时用户取消 | 用户看到迁移计划后拒绝 | 不执行任何操作 | AC3 |
| 存量升级时有未提交的修改 | 迁移范围内的文件被本地修改 | 标记冲突，不覆盖 | AC4 |
| Quick 流程 | 任务规模小且无 DB 变更 | 跳过 Spec/Design/Review | AC7 |
| Enhanced 流程 | 涉及 DB 变更或跨模块 | 强制 Brainstorming + 人工审查 | AC9 |
| QA 熔断时无用户响应 | 用户长时间不回复熔断通知 | 流程保持暂停状态，直到用户决策 | AC13 |
| 多次人工验收打回 | 同一变更被连续打回 3 次 | 编排器建议用户重新评估需求或方案 | AC14-16 |
| 归档时 CI 不绿 | CI 中有失败检查 | 拒绝归档，列出失败项 | AC17 |

---

## 错误场景与用户提示文案

| 错误场景 | 触发条件 | 用户看到的提示文案 |
|---------|---------|-----------------|
| 项目未初始化 | 编排器启动时检测不到 AGENTS.md | "项目未初始化。请先运行'项目初始化'来接入 SDD 框架。" |
| 目录骨架不完整 | 合规检查发现缺少必要目录 | "SDD 目录骨架不完整。缺失：`docs/changes/`。请运行'项目初始化'补全。" |
| change-id 格式错误 | 变更目录名不符合约定 | "变更目录名格式错误。正确格式：NNN-short-name（如 001-add-login）。" |
| 前置产物缺失 | 阶段交接前发现上游文件不存在 | "无法进入 {阶段名}：前置产物 {文件名} 不存在。请先完成 {上游阶段}。" |
| PRD 未确认 | 编排器尝试进入 Spec 阶段但 PRD 未被用户确认 | "PRD 尚未经用户确认。请确认 prd.md 后再继续。" |
| QA 熔断 | 连续 5 轮 QA 失败 | "QA 已连续 5 轮失败，流程熔断。请查看失败摘要并决定：继续修复 / 回退方案 / 放弃变更。" |
| 人工验收未通过 | 用户验收发现问题 | "验收未通过。问题类型：{需求/设计/代码}。流程回退到 {PRD/Design/Implement} 阶段。" |
| 归档条件不满足 | 用户尝试归档但 CI 不绿 | "无法归档：CI 检查未通过。请修复后再试。" |
| 存量升级冲突 | 迁移计划中有文件冲突 | "以下文件存在冲突，需要人工决策：{文件列表}。请解决冲突后重新运行升级。" |

---

## 关键非功能需求

| 需求类型 | 要求 | 衡量方式 |
|---------|------|:---:|
| 通用性 | 同一套 Skills 在 AILP（FastAPI）和 mock 项目（Go）中均可正常运作 | 分别在两个项目中走完整 SDD 流程 |
| Token 效率 | 每个角色 Skill 核心指令 ≤ 80 行（不含 frontmatter） | 统计 SKILL.md 正文行数 |
| 可恢复性 | 编排器状态在中断后可恢复（通过变更目录中的产物判断当前阶段） | 模拟中断后重启编排器，验证正确恢复 |
| 响应时间 | 项目初始化和存量升级的交互询问部分，用户无需等待超过 10 秒 | 计时 |
