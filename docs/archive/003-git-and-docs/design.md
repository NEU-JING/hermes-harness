# Design: Git 工作流 + 基线维护 + README 升级（Coder-Ready）

> 版本：V2.0 — Coder 可直接照此实现
> 日期：2026-05-25
> 作者：Architect Agent

---

## 变更总览

| # | 文件 | 操作 | 内容 |
|---|------|:---:|------|
| F1 | `skills/sdd/shared/git-workflow.md` | **新建** | Git 工作流规范文档（全文给出） |
| F2 | `skills/sdd/sdd-orchestrator/SKILL.md` | **修改** | Phase 8 的 L77-85 替换为含 R10+基线融合的新 Phase 8（全文给出） |
| F3 | `docs/current/README.md` | **新建** | 基线文档地图（全文给出） |
| F4 | `README.md` | **重写** | 全面升级为生产级 README（全文给出） |

---

## F1: skills/sdd/shared/git-workflow.md — 新建

**操作**：使用 `write_file` 创建，路径 `/root/workspace/hermes-harness/skills/sdd/shared/git-workflow.md`。

**完整内容**：

```markdown
# Git 工作流规范

> SDD 项目的 Git 分支、PR、合并策略规范。所有贡献者（人或 Agent）必须遵守。

---

## 分支命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 功能开发 | `feat/{change-id}` | `feat/003-git-and-docs` |
| Bug 修复 | `fix/{change-id}` | `fix/004-typo-in-readme` |
| 紧急修复 | `hotfix/{简短描述}` | `hotfix/install-sh-permission` |

> 紧急修复（hotfix）可豁免 R10 检查，使用 `--bypass-r10` 归档。

---

## PR 流程

```
1. 从 main 创建 feature 分支
   git checkout -b feat/{change-id} main

2. 开发 + 提交（按 tasks.md 逐 Task commit）
   git commit -m "feat(scope): T{n} 描述"

3. Push feature 分支
   git push origin feat/{change-id}

4. 在 GitHub 创建 Pull Request
   - 标题：feat({scope}): {变更简述}
   - 描述：使用 PR 模板

5. Reviewer 评审
   - 通过 → Squash merge
   - 有条件通过 → 修复后更新 PR
   - 不通过 → 修复 CRITICAL 后更新 PR

6. Squash Merge → main
   所有 commit 压缩为一个，保持 main 线性历史
```

---

## PR 描述模板

```markdown
## 变更 ID
docs/changes/{change-id}/

## 变更概述
（一句话描述）

## AC 覆盖声明
- [ ] AC1: （描述）
- [ ] AC2: （描述）
...

## SDD 产物
- PRD: docs/changes/{change-id}/prd.md
- Spec: docs/changes/{change-id}/spec.md
- Design: docs/changes/{change-id}/design.md
- Tasks: docs/changes/{change-id}/tasks.md

## 影响范围
（修改/新增的文件清单）
```

---

## 合并策略

- **Squash merge**（推荐）：将所有 commit 压缩为一个，保持 main 线性且可读
- **禁止**直接 push 到 main
- **禁止**force push 到 main

---

## main 分支保护

需仓库管理员在 GitHub Settings → Branches 中配置：

- [ ] Require a pull request before merging
- [ ] Require approvals (≥ 1)
- [ ] Do not allow bypassing the above settings

> 此配置需手动操作，非代码可自动化。

---

## 紧急修复豁免

hotfix 可通过 `--bypass-r10` 豁免 PR 流程：

```bash
# 归档时跳过 R10 检查
# orchestrator Phase 8 检测到 --bypass-r10 标志 → 跳过 git merge 检测
```

豁免记录写入 `docs/current/README.md` 变更历史，标注 `HOTFIX`。
```

**验证**：
```bash
test -f skills/sdd/shared/git-workflow.md
grep -q "分支命名" skills/sdd/shared/git-workflow.md
grep -q "PR 流程" skills/sdd/shared/git-workflow.md
grep -q "PR 描述模板" skills/sdd/shared/git-workflow.md
grep -q "Squash merge" skills/sdd/shared/git-workflow.md
grep -q "main 分支保护" skills/sdd/shared/git-workflow.md
```

---

## F2: sdd-orchestrator Phase 8 替换

**文件**：`skills/sdd/sdd-orchestrator/SKILL.md`
**操作**：使用 `patch` 工具，将 L77-85 的旧 Phase 8 替换为新内容。

### old_string（L77-85，精确匹配）

```
### Phase 8: 归档

```
1. 最终门禁检查：sdd-structure-lint Level 1+2+3（全量）
2. 移动变更目录: docs/changes/{id}/ → docs/archive/{id}/
3. 更新引用: docs/current/ → docs/archive/{id}/
4. 清理状态文件: rm docs/changes/{id}/.sdd-state.json
5. 输出归档摘要
```
```

### new_string（完整替换）

```markdown
### Phase 8: 归档

#### Step 8.0: R10 检查（PR 流程合规）

加载 `sdd/shared/git-workflow.md` 规范，执行以下检查：

1. **检测当前分支**：
   执行 `git branch --show-current`，获取 `$BRANCH`
   - 若 `$BRANCH` != `main` → **阻断归档**，输出：
     ```
     ❌ R10 阻断: 当前在 {BRANCH} 分支。
        请先合并到 main 后重新归档：
        git checkout main
        git merge --squash {BRANCH}
     ```
     退出码 1，终止归档。
   - 若 `$BRANCH` = `main` → 继续下一步。

2. **检测 PR merge 记录**（检查最近 5 个 commit）：
   执行 `git log -5 --oneline --merges`
   - 若无 merge commit → **阻断归档**，输出：
     ```
     ❌ R10 阻断: 未检测到 PR merge 记录。
        SDD 要求所有变更通过 PR 合并到 main。
        git checkout -b feat/{change_id}
        git push origin feat/{change_id}
        # 在 GitHub 创建 PR 并 squash merge
        # 紧急修复可使用 --bypass-r10 豁免
     ```
     退出码 1，终止归档。
   - 若有 merge commit → 通过，继续下一步。

3. **--bypass-r10 豁免**：
   若用户传入 `--bypass-r10` 标志 → 跳过 R10 检查，输出：
   ```
   ⚠️ R10 豁免: --bypass-r10 已激活，跳过 PR 流程检查。
   此豁免将记录到归档日志。
   ```
   在 `docs/current/README.md` 变更历史中标注 `HOTFIX`。

#### Step 8.1: 基线融合（PRD + Spec + Design → 当前生产基线）

基线文档 `docs/current/README.md` 是**当前生产版本的唯一真相源**——它不是变更日志，而是所有已归档变更融合后的"项目全貌"。每次归档时，将 PRD/Spec/Design 的关键内容**融合进**基线对应章节。

**融合逻辑（按章节）**：

##### 8.1.1: 初始化检查

`docs/current/README.md` 不存在 → 按 F3 模板完整初始化。存在 → 按以下步骤逐章节更新。

##### 8.1.2: 融合「项目状态」

从 PRD 的"背景与目标"章节提取：
- 新增了什么能力（一句描述）
- 解决了什么问题

若该变更引入了新的项目级属性（如新流程级别、新规则类型），追加到现状描述中。

##### 8.1.3: 融合「架构概览」

从 Design 的"产出物清单"和"架构设计"章节提取：
- 新增了哪些文件/目录 → 追加到架构树
- 删除了哪些文件/目录 → 从架构树中移除
- 修改了哪些模块的职责 → 更新对应描述

架构树应始终反映**当前仓库根目录的实际结构**。

##### 8.1.4: 融合「Skill 清单」+「共享规范」

从 Design 的"产出物清单 → 无需修改"和"修改文件"章节判断：
- 若变更涉及 `skills/sdd/` 下文件修改 → 重新扫描 `skills/sdd/` 目录，刷新 Skill 清单表格和共享规范表格
- 若变更不涉及 → 保持不变

##### 8.1.5: 追加「变更历史」记录

在变更历史表格末尾追加一行：
```markdown
| {change_id} | {PRD 标题} | {Design 影响范围摘要} | {当前日期} |
```

---

**融合原则**：
- **增量更新，不重写全量**：只更新受影响的章节，保持基线文档的历史连续性
- **Design 为权威源**：架构决策和文件变更以 Design 为准
- **PRD 为上下文源**：项目目标和能力描述以 PRD 为准
- **变更历史为追溯源**：保留每次变更的记录，但不替代融合内容

#### Step 8.2: 最终门禁检查

调用 sdd-structure-lint Level 1+2+3（全量检查）。通过则继续，不通过则阻断并输出错误报告。

#### Step 8.3: 文件移动

移动变更目录：
```bash
mv docs/changes/{change_id} docs/archive/{change_id}
```

#### Step 8.4: 清理

```bash
rm docs/archive/{change_id}/.sdd-state.json
```

#### Step 8.5: 输出归档摘要

```
✅ 归档完成: {change_id}
📁 归档位置: docs/archive/{change_id}/
📄 基线更新: docs/current/README.md
🔒 R10 检查: {通过/豁免(HOTFIX)}
```
```

### 验证

```bash
grep -q "Step 8.0: R10 检查" skills/sdd/sdd-orchestrator/SKILL.md && echo "✓ 8.0"
grep -q "Step 8.1: 基线融合" skills/sdd/sdd-orchestrator/SKILL.md && echo "✓ 8.1"
grep -q "git branch --show-current" skills/sdd/sdd-orchestrator/SKILL.md && echo "✓ branch check"
grep -q "git log -5 --oneline --merges" skills/sdd/sdd-orchestrator/SKILL.md && echo "✓ merge check"
grep -q "bypass-r10" skills/sdd/sdd-orchestrator/SKILL.md && echo "✓ bypass"
grep -q "Step 8.5: 输出归档摘要" skills/sdd/sdd-orchestrator/SKILL.md && echo "✓ 8.5"
```

---

## F3: docs/current/README.md — 新建

**操作**：使用 `write_file` 创建，路径 `/root/workspace/hermes-harness/docs/current/README.md`。

**完整内容**：

```markdown
# Hermes Harness — 项目基线

> 最后更新：2026-05-25
> 当前版本：参考 `main` 分支最新 commit
> 本文档由 SDD 归档流程自动维护（sdd-orchestrator Phase 8.1）

---

## 项目状态

- **SDD 流程**：Standard（8 阶段：PO → BA → Architect → Coder → Reviewer → QA → 验收 → 归档）
- **角色 Skill**：8 个（po-agent, ba-agent, architect-agent, coder-agent, reviewer-agent, qa-agent, sdd-orchestrator, sdd-init）
- **辅助 Skill**：1 个（sdd-structure-lint）
- **已归档变更**：2（001-sdd-init, 002-project-onboarding）

---

## 架构概览

Hermes Harness 是一个 Agentic SDD 开发框架，结构如下：

```
用户项目
  ├── AGENTS.md               ← SDD 配置（项目入口）
  ├── CONSTITUTION.md          ← 不可违背的核心原则
  ├── QUIRKS.md                ← 陷阱与怪癖记录
  └── docs/
      ├── changes/             ← 进行中的 SDD 变更
      ├── current/             ← 当前基线（本文件）
      └── archive/             ← 已归档变更

Hermes Agent
  └── ~/.hermes/skills/sdd/    ← 8 角色 Skill + shared/
      ├── sdd-orchestrator/    ← 编排器（Phase 0-8）
      ├── po-agent/            ← PRD 产出
      ├── ba-agent/            ← Spec + AC
      ├── architect-agent/     ← Design + Tasks
      ├── coder-agent/         ← TDD 实现
      ├── reviewer-agent/      ← 三阶段评审
      ├── qa-agent/            ← 测试验证
      ├── sdd-init/            ← 项目初始化/升级
      ├── sdd-structure-lint/  ← 结构检查
      └── shared/              ← 共享规则与规范
```

---

## Skill 清单

| Skill | 阶段 | 职责 |
|------|:---:|------|
| [sdd-orchestrator](../skills/sdd/sdd-orchestrator/SKILL.md) | 编排 | 流程判定、阶段调度、门禁检查、归档 |
| [po-agent](../skills/sdd/po-agent/SKILL.md) | 定义 | 产出 PRD，明确用户场景与范围 |
| [ba-agent](../skills/sdd/ba-agent/SKILL.md) | 定义 | 产出 Spec，细化 AC（Given-When-Then） |
| [architect-agent](../skills/sdd/architect-agent/SKILL.md) | 设计 | Brainstorming + Design + Tasks 拆分 |
| [coder-agent](../skills/sdd/coder-agent/SKILL.md) | 实现 | 按 Tasks 逐步实现，TDD 强制 |
| [reviewer-agent](../skills/sdd/reviewer-agent/SKILL.md) | 评审 | 三阶段评审（Spec 合规/代码质量/架构一致性） |
| [qa-agent](../skills/sdd/qa-agent/SKILL.md) | 测试 | AC 覆盖矩阵、测试执行、环境差异、熔断 |
| [sdd-init](../skills/sdd/sdd-init/SKILL.md) | 基础设施 | 项目初始化 + 升级（init/upgrade 双模式） |
| [sdd-structure-lint](../skills/sdd/sdd-structure-lint/SKILL.md) | 基础设施 | 文件结构合规检查（3 级：文件/产物/内容） |

---

## 共享规范

| 文档 | 说明 |
|------|------|
| [sdd-rules.md](../skills/sdd/shared/sdd-rules.md) | 10 条通用规则（R1-R10） |
| [flow-level-rules.md](../skills/sdd/shared/flow-level-rules.md) | Quick/Standard/Enhanced 判定逻辑 |
| [handoff-protocol.md](../skills/sdd/shared/handoff-protocol.md) | Agent 间交接协议 |
| [convention-overrides.md](../skills/sdd/shared/convention-overrides.md) | 项目级规则覆盖机制 |
| [git-workflow.md](../skills/sdd/shared/git-workflow.md) | Git 分支/PR/合并策略规范 |

---

## 变更历史

| 变更 ID | 标题 | 影响范围 | 归档日期 |
|------|------|------|------|
| 001-sdd-init | SDD 项目初始化 | 8 个角色 Skill + shared/ | 2026-05-24 |
| 002-project-onboarding | 项目上手体验 | README + INSTALL + install.sh + templates/ + sdd-init 修改 | 2026-05-25 |
```

**验证**：
```bash
test -f docs/current/README.md
grep -q "项目状态" docs/current/README.md
grep -q "架构概览" docs/current/README.md
grep -q "Skill 清单" docs/current/README.md
grep -q "变更历史" docs/current/README.md
grep -q "001-sdd-init" docs/current/README.md
grep -q "002-project-onboarding" docs/current/README.md
```

---

## F4: README.md — 全面重写

**操作**：使用 `write_file` **完全覆盖** `/root/workspace/hermes-harness/README.md`。

**完整内容**：

```markdown
# Hermes Harness

> **让 AI Agent 按工程规范协作——把软件工程流程编码为 Agent 可执行的 Skill。**

AI Agent 写代码很快，但写完就忘、质量不稳、流程不透明。SDD（Spec-Driven Development）把需求→规格→设计→任务→实现→评审→测试→验收的全流程编码为 8 个角色 Skill，让 Agent 像一支工程团队一样工作。

---

## SDD 流程

```mermaid
graph LR
    PO[PO: 需求定义] --> BA[BA: Spec+AC]
    BA --> AR[Architect: 设计+Task]
    AR --> CO[Coder: TDD实现]
    CO --> RE[Reviewer: 三阶段评审]
    RE --> QA[QA: 测试验证]
    QA --> UA[用户验收]
    UA --> ARV[归档]
```

8 个阶段，3 种流程级别：**Quick**（Bug 修复）→ **Standard**（常规功能，默认）→ **Enhanced**（安全/性能关键）。

---

## 快速开始

<details>
<summary><b>Hermes Agent（推荐）</b></summary>

```bash
# 1. 克隆
git clone https://github.com/NEU-JING/hermes-harness.git
cd hermes-harness

# 2. 安装
./install.sh

# 3. 在你的项目中初始化
cd /path/to/your-project
# 对 Hermes Agent 说："初始化 SDD"

# 4. 发起第一个变更
# 对 Hermes Agent 说："用 SDD 流程做 xxx"
```

</details>

<details>
<summary><b>手动安装</b></summary>

```bash
git clone https://github.com/NEU-JING/hermes-harness.git
cp -r hermes-harness/skills/sdd ~/.hermes/skills/sdd/
```

</details>

<details>
<summary><b>其他 Agent 兼容</b></summary>

Skills 是纯 Markdown 文件（SKILL.md + references/），兼容任何支持 system prompt 或 instruction file 的 Agent。将 `skills/sdd/` 目录内容作为 context 注入即可。

</details>

---

## 完整 Skill 目录

### 编排

| Skill | 职责 |
|------|------|
| [sdd-orchestrator](skills/sdd/sdd-orchestrator/SKILL.md) | 流程判定、阶段调度、门禁检查、归档 |

### 定义（Define）

| Skill | 职责 |
|------|------|
| [po-agent](skills/sdd/po-agent/SKILL.md) | 产品负责人——产出 PRD，定义用户场景与功能范围 |
| [ba-agent](skills/sdd/ba-agent/SKILL.md) | 业务分析师——产出 Spec，细化 AC（Given-When-Then） |

### 设计（Design）

| Skill | 职责 |
|------|------|
| [architect-agent](skills/sdd/architect-agent/SKILL.md) | 技术架构师——Brainstorming + Design + Tasks 拆分 |

### 实现（Build）

| Skill | 职责 |
|------|------|
| [coder-agent](skills/sdd/coder-agent/SKILL.md) | 开发者——按 Tasks 逐步实现，TDD 强制 |

### 评审（Review）

| Skill | 职责 |
|------|------|
| [reviewer-agent](skills/sdd/reviewer-agent/SKILL.md) | 代码评审员——三阶段评审（Spec 合规/代码质量/架构一致性） |

### 测试（Verify）

| Skill | 职责 |
|------|------|
| [qa-agent](skills/sdd/qa-agent/SKILL.md) | 测试工程师——AC 覆盖矩阵、测试执行、环境差异、熔断 |

### 基础设施

| Skill | 职责 |
|------|------|
| [sdd-init](skills/sdd/sdd-init/SKILL.md) | 项目初始化 + 升级（支持 init/upgrade 双模式） |
| [sdd-structure-lint](skills/sdd/sdd-structure-lint/SKILL.md) | 文件结构合规检查（3 级：文件/产物/内容） |

### 共享规范

| 文档 | 说明 |
|------|------|
| [sdd-rules.md](skills/sdd/shared/sdd-rules.md) | 10 条通用规则（R1-R10） |
| [flow-level-rules.md](skills/sdd/shared/flow-level-rules.md) | Quick/Standard/Enhanced 判定逻辑 |
| [handoff-protocol.md](skills/sdd/shared/handoff-protocol.md) | Agent 间交接协议 |
| [convention-overrides.md](skills/sdd/shared/convention-overrides.md) | 项目级规则覆盖机制 |
| [git-workflow.md](skills/sdd/shared/git-workflow.md) | Git 分支/PR/合并策略规范 |

---

## 项目结构

```
hermes-harness/
├── README.md                          ← 项目门面
├── INSTALL.md                         ← 安装指南
├── install.sh                         ← 一键安装脚本
├── AGENTS.md                          ← SDD 配置
├── CONSTITUTION.md                    ← 项目宪法
├── templates/                         ← 项目级模板
│   ├── AGENTS.md
│   ├── CONSTITUTION.md
│   ├── QUIRKS.md
│   ├── .pre-commit-config.yaml
│   ├── pytest.ini
│   └── conftest.py
├── skills/sdd/                        ← 8 角色 Skill + shared/
│   ├── sdd-orchestrator/
│   ├── po-agent/
│   ├── ba-agent/
│   ├── architect-agent/
│   ├── coder-agent/
│   ├── reviewer-agent/
│   ├── qa-agent/
│   ├── sdd-init/
│   ├── sdd-structure-lint/
│   └── shared/
└── docs/
    ├── changes/                       ← 进行中的 SDD 变更
    ├── current/                       ← 当前基线（文档地图）
    └── archive/                       ← 已归档变更
```

---

## 设计哲学

### 为什么需要 SDD？

AI Agent 默认走最短路径——跳过 Spec、忽略测试、忘记 Review、直接 push main。这些"捷径"在原型阶段无伤大雅，但在生产级项目中累积成技术债。

SDD 不做 Agent 的替代品——它做 Agent 的**工程规范层**。每个角色 Skill 将软件工程的最佳实践（TDD、Brainstorming、三阶段评审、AC 覆盖矩阵）编码为 Agent 可逐步执行的结构化流程。

### 与 ad-hoc Agent 编码的区别

| 维度 | ad-hoc Agent 编码 | SDD |
|------|------|------|
| 需求 | "帮我做个登录" | PRD → 用户确认 → Spec（Given-When-Then） |
| 设计 | Agent 自定架构 | Brainstorming ≥ 2 方案 + Design 文档 |
| 实现 | 跳过测试直接写 | TDD（RED → GREEN → REFACTOR） |
| 质量 | 写完即忘 | 三阶段评审 + AC 覆盖矩阵 |
| 流程 | 直接 push main | feature 分支 → PR → Review → squash merge |
| 追溯 | 无 | 完整 SDD 产物链（PRD→Spec→Design→Tasks→Review→QA） |

---

## 要求

- **Hermes Agent >= v2.0**

## 文档

| 文档 | 说明 |
|------|------|
| [安装指南](INSTALL.md) | 详细安装步骤、卸载、升级 |
| [项目模板](templates/) | 接入 SDD 的项目需要的模板文件 |
| [项目基线](docs/current/README.md) | 当前生产状态概览 |

## License

MIT — 在项目、团队、工具中自由使用。
```

**验证**：
```bash
# 首屏 Hero
head -5 README.md | grep -q "Hermes Harness" && echo "✓ Hero title"
head -5 README.md | grep -q "让 AI Agent" && echo "✓ Hero tagline"

# 章节完整性
grep -q "SDD 流程" README.md && echo "✓ SDD flow"
grep -q "<details>" README.md && echo "✓ Collapsible sections"
grep -q "完整 Skill 目录" README.md && echo "✓ Skill catalog"
grep -q "项目结构" README.md && echo "✓ Project structure"
grep -q "设计哲学" README.md && echo "✓ Philosophy"
grep -q "License" README.md && echo "✓ License"

# Skill 目录覆盖所有 9 个 Skill
for skill in sdd-orchestrator po-agent ba-agent architect-agent coder-agent reviewer-agent qa-agent sdd-init sdd-structure-lint; do
    grep -q "$skill" README.md && echo "✓ $skill" || echo "✗ $skill MISSING"
done

# 设计哲学含对比表
grep -q "ad-hoc Agent" README.md && echo "✓ ad-hoc comparison"
grep -q "TDD（RED → GREEN → REFACTOR）" README.md && echo "✓ TDD mention"
```

---

## 实现顺序

```
F1: git-workflow.md  ─┐
F3: docs/current/     ─┤  并行（无依赖）
F4: README.md         ─┘
                        ↓
                  F2: orchestrator Phase 8 替换
                        ↓
                    全量验证
```

F2 必须最后做——因为它引用了 F1（加载 `sdd/shared/git-workflow.md`）和 F3（基线模板初始化），虽然引用是"运行时"的（F1 和 F3 文件先存在即可），但按依赖链应排在 F1/F3/F4 之后。
