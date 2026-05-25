# PRD: Git 工作流 + 基线维护 + README 升级

> 版本：V1.0
> 日期：2026-05-25
> 作者：PO Agent

---

## 背景与目标

**背景**：

在 dogfooding（用自己的 SDD 框架开发 SDD 框架本身）过程中，暴露了三个工程实践缺陷：

1. **无 Git 工作流约束**：002 变更的 8 个 commit 直接 push 到 `main` 分支，跳过了 PR Review 流程。R10 规则虽然定义了"PR 不直接 push main"，但实际执行中未生效——编排器在归档前只检查了 R10 的存在性，未阻断直接 push。
2. **`docs/current/` 空置**：002 变更归档后，`docs/archive/` 有完整产物，但 `docs/current/` 仍然是空的。设计上 `docs/current/` 应该是"当前生产状态基线"——反映所有已归档变更融合后的文档快照，但归档流程缺少这一步。
3. **README 简陋**：对比 `addyosmani/agent-skills` 等同类项目，我们的 README 缺乏 Skill 目录、多平台安装说明、项目结构展示、设计哲学等章节，显得不够"生产级"。

**目标**：

- 所有代码变更走 feature 分支 + PR 流程，`main` 分支受保护
- `docs/current/` 随每次归档自动更新，以文档地图方式融合已归档变更
- README 达到同类开源项目水准，让来访者在首屏建立信任

---

## 用户场景

### 场景 1：贡献者提交变更

- **角色**：hermes-harness 贡献者（人或 Agent）
- **前置条件**：本地完成开发，有多个 commit
- **操作流程**：
  1. 创建 feature 分支 `feat/003-git-and-docs`
  2. Push 到远程 feature 分支
  3. 创建 PR（含变更说明 + AC 覆盖声明）
  4. Reviewer 评审通过后合并到 `main`
  5. `main` 分支受保护，禁止直接 push
- **期望结果**：所有变更通过 PR 进入 `main`，有可追溯的评审记录

### 场景 2：变更归档后基线自动更新

- **角色**：SDD 编排器
- **前置条件**：一个变更通过全部 SDD 阶段，进入归档
- **操作流程**：
  1. 移动 `docs/changes/{id}/` → `docs/archive/{id}/`
  2. 从归档产物中提取关键信息（变更标题、影响范围、产出物清单）
  3. 更新 `docs/current/` 下的基线文档（项目状态、架构描述、Skill 清单等）
  4. 以文档地图方式组织，保持可读性
- **期望结果**：`docs/current/` 始终反映项目当前状态，新贡献者打开即可了解全局

### 场景 3：开发者浏览项目 README

- **角色**：GitHub 来访者
- **前置条件**：打开仓库首页
- **操作流程**：
  1. 首屏看到 Hero 区域（标题 + 金句 + 定位）
  2. 看到完整的 Skill 目录表格（按阶段分组：定义→分析→设计→实现→评审→测试）
  3. 看到按平台分类的安装说明（Hermes Agent / 其他 Agent 兼容）
  4. 看到项目结构树
  5. 看到"为什么需要 SDD"设计哲学章节
- **期望结果**：5 秒建立信任，30 秒理解全部能力，2 分钟完成安装

---

## 功能范围

### In Scope（本次包含）

- ✅ **PR 工作流落地**：
  - 强化 `sdd-orchestrator` 的 R10 检查逻辑，归档前阻断非 PR 路径的 push
  - 新增 `skills/sdd/shared/git-workflow.md`：Git 工作流规范（分支命名、PR 模板、合并策略）
  - 引导贡献者使用 feature 分支 + PR 流程
- ✅ **`docs/current/` 基线维护**：
  - `sdd-orchestrator` 归档阶段新增"基线融合"步骤
  - `docs/current/` 初始化为文档地图（README 式索引）
  - 每次归档自动更新基线文档
- ✅ **README 升级**：
  - 首屏 Hero 区域（标题 + 金句）
  - 完整 Skill 目录表格（按 SDD 阶段分组）
  - 多平台安装说明（Hermes Agent / 手动复制 / 其他 Agent 兼容）
  - 项目结构树
  - 设计哲学章节

### Out of Scope（本次不包含）

- ❌ GitHub Branch Protection Rules 配置（需 repo admin 在 GitHub Settings 操作，非代码可自动化）
- ❌ CI/CD 流水线（GitHub Actions）
- ❌ 多语言 README（仅中文）
- ❌ 项目 Logo/Hero 图片设计
- ❌ 修改 Skill 内部逻辑（仅改 orchestrator 的 R10 检查和归档流程）

---

## 非功能需求（NFR）

| 类别 | 要求 | 指标 |
|------|------|------|
| 可维护性 | 基线文档可自动更新 | 归档时无需手动编辑 docs/current/ |
| 可读性 | README 结构对标同类项目 | 包含 Skill 目录表、项目结构树、设计哲学章 |
| 流程合规 | 100% 变更走 PR | main 分支不接受直接 push |
| 可追溯性 | 每个 PR 关联 SDD 变更 ID | PR 描述包含 `docs/changes/{id}/` 引用 |

---

## 验收标准（高层级）

1. **AC-1**：`sdd-orchestrator` 归档前检查当前分支，若非 `main` 且变更涉及代码 → 要求创建 PR
2. **AC-2**：新增 `git-workflow.md` 规范文档，含分支命名、PR 模板、合并策略
3. **AC-3**：`docs/current/` 包含项目基线文档（项目状态、架构概览、Skill 清单），格式为文档地图
4. **AC-4**：归档流程自动更新 `docs/current/`（sdd-orchestrator 归档阶段新增融合步骤）
5. **AC-5**：README 首屏含 Hero 区域（标题 + 金句描述）
6. **AC-6**：README 含完整 Skill 目录表格（按 SDD 阶段分组，每个含一句话描述）
7. **AC-7**：README 含多平台安装说明（Hermes Agent / 手动 / 其他 Agent 兼容）
8. **AC-8**：README 含项目结构树（ASCII）
9. **AC-9**：README 含设计哲学章节（为什么需要 SDD、与其他方案的区别）

---

## 风险与假设

### 风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|:---:|------|
| R10 强制执行后 Agent 无法 push | 开发流程阻塞 | 低 | 保留 `--bypass-r10` 豁免机制用于紧急修复 |
| 基线文档自动融合逻辑不完善 | docs/current/ 质量下降 | 中 | 初始版本提供手动编辑入口，逐步自动化 |
| README 信息过载 | 首屏失去焦点 | 低 | 采用 agent-skills 的折叠式 + 表格设计，核心信息前置 |

### 假设

- 用户（老师）有 GitHub repo admin 权限，可手动配置 Branch Protection
- `docs/current/` 的文档地图设计参考 `agent-skills` README 的结构
- 本次变更本身将通过 PR 流程提交（dogfooding R10）
