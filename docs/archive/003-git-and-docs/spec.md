# Spec: Git 工作流 + 基线维护 + README 升级

> 版本：V1.0
> 日期：2026-05-25
> 作者：BA Agent（基于 [PRD](./prd.md)）

---

## 功能概述

落地 Git PR 工作流、实现归档时 `docs/current/` 基线自动更新、参照 `addyosmani/agent-skills` 升级 README 至生产级标准。

---

## 详细需求

### 需求 1：Git 工作流规范文档

**描述**：创建 `skills/sdd/shared/git-workflow.md`，定义分支命名、PR 模板、合并策略。

**内容要求**：
- 分支命名规范：`feat/{change-id}` / `fix/{change-id}`
- PR 创建流程：push feature 分支 → 创建 PR → Reviewer 评审 → merge
- PR 描述模板：变更 ID、AC 覆盖声明、SDD 产物引用
- 合并策略：squash merge（保持 main 线性历史）
- `main` 分支保护说明（需 admin 在 GitHub Settings 手动配置）
- 紧急修复豁免：`hotfix/` 分支可走快速通道

---

### 需求 2：sdd-orchestrator R10 强制执行

**描述**：修改 `skills/sdd/sdd-orchestrator/SKILL.md` Phase 8 归档流程，在归档前增加 R10 检查。

**逻辑**：
1. 检测当前分支是否为 `main`
2. 若在 feature 分支（`feat/*`）→ 输出提示"请创建 PR 合并到 main 后重新归档"
3. 若在 `main` 分支 → 检查最近 commit 是否来自 PR merge（通过 git log 检测 `Merge pull request` 模式）
4. 若无 PR merge 记录 → 阻断归档，提示"此变更未通过 PR 流程，请先创建 PR"
5. 提供 `--bypass-r10` 豁免机制（仅限紧急修复）

---

### 需求 3：docs/current/ 基线文档

**描述**：初始化 `docs/current/` 为文档地图，并在归档流程中自动更新。

**初始化内容**：
- `docs/current/README.md`：文档地图索引（项目状态、架构概览、Skill 清单）
- 采用 agent-skills 式的分类表格组织

**归档时自动更新逻辑**：
1. 从 `docs/archive/{change_id}/prd.md` 提取变更标题和一句话摘要
2. 从 `design.md` 提取影响范围（修改/新增的文件清单）
3. 追加到 `docs/current/README.md` 的"变更历史"章节
4. 若变更涉及 Skill 新增/修改 → 更新"Skill 清单"章节

---

### 需求 4：README 升级

**描述**：参照 `addyosmani/agent-skills` 结构，重写 README 为生产级标准。

**章节结构**：
1. **Hero 区域**：标题 + 金句描述 + （可选：ASCII logo）
2. **SDD 流程**：保留 Mermaid 图
3. **快速开始**：按平台分类的折叠式安装说明
   - Hermes Agent（主推）
   - 手动安装（通用）
   - 其他 Agent 兼容说明
4. **完整 Skill 目录**：按 SDD 阶段分组表格（PO → BA → Architect → Coder → Reviewer → QA → 共享），每个含一句话描述
5. **项目结构**：ASCII 树
6. **设计哲学**：为什么需要 SDD、与 ad-hoc Agent 编码的区别
7. **文档**：链接到 INSTALL.md、templates/、SDD 规则
8. **要求 + License**

---

## Acceptance Criteria

| 编号 | 场景 | Given | When | Then |
|:---:|------|-------|------|------|
| AC1 | git-workflow.md 存在且内容完整 | 开发者打开仓库 | 查看 `skills/sdd/shared/git-workflow.md` | 包含：分支命名规范、PR 流程、PR 描述模板、合并策略、main 保护说明 |
| AC2 | orchestrator 归档前 R10 阻断 | Coder 直接 push main（非 PR merge） | orchestrator 执行 Phase 8 归档 | 输出"此变更未通过 PR 流程，请先创建 PR"，阻断归档 |
| AC3 | orchestrator 归档前 PR 检测通过 | 变更通过 `git merge --squash` 从 PR 合并 | orchestrator 执行 Phase 8 归档 | R10 检查通过，正常归档 |
| AC4 | orchestrator 支持 --bypass-r10 | 紧急 hotfix 需要直接 push | 归档时传入 `--bypass-r10` | 跳过 R10 检查，正常归档并记录豁免日志 |
| AC5 | docs/current/ 初始化 | 首次执行归档 | 归档流程运行 | `docs/current/README.md` 创建，含项目状态 + 架构概览 + Skill 清单 |
| AC6 | 归档后基线自动更新 | 003 变更归档 | 归档流程运行 | `docs/current/README.md` 的变更历史追加 003 条目（标题 + 摘要 + 影响范围） |
| AC7 | 归档后 Skill 清单更新 | 003 涉及 Skill 修改 | 归档流程运行 | `docs/current/README.md` 的 Skill 清单反映最新状态 |
| AC8 | README Hero 区域 | 开发者打开 GitHub 首页 | 看到 README 渲染 | 首屏含标题 + 金句描述（≤ 2 行），视觉上与 agent-skills 同级 |
| AC9 | README Skill 目录表 | 开发者滚动 README | 看到"完整 Skill 目录"章节 | 按 SDD 阶段分组表格，8 个 Skill 均有一句话描述 |
| AC10 | README 多平台安装 | 开发者滚动 README | 看到"快速开始"章节 | 含折叠式安装说明（Hermes Agent / 手动 / 其他兼容），至少 3 种方式 |
| AC11 | README 项目结构树 | 开发者滚动 README | 看到"项目结构"章节 | ASCII 树包含全部顶级目录和关键文件 |
| AC12 | README 设计哲学 | 开发者滚动 README | 看到"设计哲学"章节 | 含"为什么需要 SDD"和"与 ad-hoc Agent 编码的区别"两段 |

---

## 边界条件

| 条件 | 预期行为 |
|------|------|
| PR 合并时使用了非 squash merge | orchestrator 仍能检测到 `Merge pull request` 模式 |
| docs/current/ 首次创建时目录不存在 | 自动 `mkdir -p` |
| 变更仅涉及文档（无 Skill 修改） | Skill 清单不更新 |
| `git-workflow.md` 被用户自定义覆盖 | orchestrator 读取 AGENTS.md 的 convention_overrides |
| 无 `docs/current/` 时的首次归档 | 完整初始化文档地图 |

---

## 非功能需求细化

| 类别 | 原始 NFR | 细化指标 | 验证方式 |
|------|---------|---------|---------|
| 流程合规 | 100% 变更走 PR | 归档前 R10 检查不通过则阻断 | 自动化（AC2/AC3） |
| 可维护性 | 基线文档自动更新 | 归档时无需手动编辑 docs/current/ | 自动化（AC6/AC7） |
| 可读性 | README 对标 agent-skills | 含 Hero + Skill 目录 + 项目结构 + 哲学 | 人工（AC8~AC12） |
| 可追溯性 | PR 关联变更 ID | PR 描述模板含 `docs/changes/{id}/` | 人工审查 |
