---
name: sdd-orchestrator
description: Use as the central orchestrator for the SDD workflow. Determines flow level (Quick/Standard/Enhanced), dispatches role agents in sequence, enforces phase gates via sdd-structure-lint, handles archiving and interrupt recovery.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sdd, orchestrator, workflow, gate, archive]
    related_skills: [sdd-init, sdd-structure-lint, po-agent, ba-agent, architect-agent, coder-agent, reviewer-agent, qa-agent]
---

# SDD Orchestrator — 编排器

## Overview

编排器是 SDD 流程的中央调度器。负责判定流程级别、按序调度角色 Agent、在每个阶段门禁检查、最终归档。

**核心职责**：保证 SDD 流程按规范执行，任何阶段不跳过必选门禁。

## When to Use

- 用户发起一个新变更：`/sdd start {描述}`
- 用户说 "用 SDD 流程做这个功能"
- 从中断状态恢复：编排器自动检测 `.sdd-state.json`

## Workflow

### Phase 0: 流程判定

1. 读取用户输入的变更描述
2. 加载 `sdd/shared/flow-level-rules.md`（通过 skill_view）
3. 调用判定逻辑 `determine_flow_level(description, changed_files, user_flag)`
4. 输出判定结果：
   ```
   🔍 SDD 流程判定: Standard (变更涉及多个模块)
   阶段: PO → BA → Architect → Coder → Reviewer → QA → 用户验收 → 归档
   ```

### Phase 1-7: 阶段调度

每个阶段的调度模板：

```
1. 调用门禁检查（当前阶段前置条件）
2. 加载对应角色 Skill
3. 执行角色工作流
4. 等待角色完成（产出文件写入）
5. 调用门禁检查（当前阶段后置条件 = 下一阶段前置条件）
6. 更新 .sdd-state.json
```

#### Standard 流程阶段

| 阶段 | 角色 Skill | 前置门禁 | 后置门禁（产物） |
|------|-----------|---------|----------------|
| PO | `po-agent` | 无 | prd.md + 用户确认 |
| BA | `ba-agent` | prd.md | spec.md + 用户确认 |
| Architect | `architect-agent` | spec.md | design.md + tasks.md + 用户确认 |
| Coder | `coder-agent` | tasks.md | 代码 commits + Task 完成报告 |
| Reviewer | `reviewer-agent` | 代码 commits | review-report.md |
| QA | `qa-agent` | review-report.md (通过/有条件通过) | qa-report.md |
| 用户验收 | — | qa-report.md (通过) | 用户明确确认 |

#### Quick 流程阶段

| 阶段 | 角色 Skill | 说明 |
|------|-----------|------|
| Architect（轻量） | `architect-agent` | 跳过 Brainstorming，产出简化 tasks.md |
| Coder | `coder-agent` | 正常执行 |
| QA（轻量） | `qa-agent` | 跳过 E2E，仅单元测试 |

#### Enhanced 流程额外阶段

Standard 全部 + 安全审查（Architect 之后）+ 性能测试（QA 之后）+ 灰度验证（用户验收前）

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

`docs/current/README.md` 不存在 → 按基线模板完整初始化。存在 → 按以下步骤逐章节更新。

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

---

## 门禁检查

每个阶段切换前，编排器调用 sdd-structure-lint：

```
skill_view(name='sdd-structure-lint')
→ 根据当前阶段执行对应 Level 检查
→ Level 1: 基础文件存在性
→ Level 2: 当前阶段产物存在性
→ Level 3: 内容质量（归档前）
→ 通过 → 继续
→ 不通过 → 阻断，输出错误报告
```

---

## 规则检查

编排器在以下时机检查 R1-R10（加载 `sdd/shared/sdd-rules.md`）：

| 时机 | 检查规则 |
|------|---------|
| Coder 阶段启动前 | R1（spec.md 存在）|
| Coder 每 Task 执行 | R3（TDD 自检，由 coder-agent 执行）|
| Reviewer 阶段后 | R4（review-report.md 存在）|
| QA 阶段 | R6（测试自包含）、R7（E2E-AC 映射）、R9（CI-only 标记）|
| Git push 时 | R8（pre-commit hook）|
| 归档前 | R10（PR 不直接 push main）|

**规则覆盖**：读取 AGENTS.md 的 `convention_overrides`：
```python
disable_rules = parse_agents_md("convention_overrides.disable_rules")
effective_rules = [r for r in R1_R10 if r.id not in disable_rules]
```

---

## 中断恢复

编排器可能因 Agent 重启、用户中断等原因中止。恢复机制：

### 状态文件

文件：`docs/changes/{change_id}/.sdd-state.json`

```json
{
  "change_id": "001-sdd-init",
  "flow_level": "Standard",
  "current_phase": "architect",
  "phases_completed": ["po", "ba"],
  "started_at": "2026-05-25T10:00:00Z",
  "updated_at": "2026-05-25T11:30:00Z"
}
```

### 恢复逻辑

```
1. 读取 .sdd-state.json
2. 确定 current_phase
3. 检查当前阶段产物是否存在：
   - 产物完整 → 从当前阶段继续
   - 产物不完整 → 回退到上一个已完成阶段
   - 无产物 → 从 Phase 0 重新开始
4. 输出恢复提示：
   "🔄 检测到中断，从 Architect 阶段恢复..."
```

### 状态更新时机

每完成一个阶段，立即更新 `.sdd-state.json`。

---

## 使用方式

### 发起新变更

用户说：
```
"用 SDD 流程做用户登录功能"
```

编排器响应：
```
🔍 流程判定: Standard
📋 阶段: PO → BA → Architect → Coder → Reviewer → QA → 用户验收 → 归档
📁 变更目录: docs/changes/002-user-login/

开始 PO 阶段...
→ 加载 po-agent skill
→ 产出 PRD 等待用户确认
```

### 恢复中断

```
编排器自动检测 .sdd-state.json
→ "🔄 检测到中断，从 Reviewer 阶段恢复..."
```

---

## Common Pitfalls

1. **门禁检查缺失**：阶段切换前不检查前置条件 → 下一阶段缺少输入
2. **规则覆盖未读取**：AGENTS.md 声明了 disable_rules 但编排器未处理 → R5 在无前端项目中被执行
3. **中断恢复不清**：.sdd-state.json 未更新 → 恢复时从错误阶段开始
4. **Quick 流程未豁免规则**：Quick 流程仍检查 R1（Spec 存在）→ 应豁免
5. **归档前未全量 lint**：直接归档而未检查 → 不完整的变更目录进入归档
