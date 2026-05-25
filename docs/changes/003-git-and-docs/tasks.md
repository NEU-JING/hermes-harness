# Tasks: Git 工作流 + 基线维护 + README 升级

> 版本：V2.0 — 匹配 Coder-Ready Design
> 日期：2026-05-25
> 前置 Design：`design.md`（含每文件完整内容）
> 估时：55 分钟

---

## 执行约定

1. **工作目录**：`/root/workspace/hermes-harness`
2. **分支**：`feat/003-git-and-docs`（dogfooding PR 流程）
3. **每 Task 完成后**：commit
4. **实现方式**：每个 F{n} 直接从 design.md 复制完整内容进行 `write_file` 或 `patch`

---

## T1: F1 + F3 + F4 — 并行创建 3 个新文件

**估时**：20min
**依赖**：无
**AC 覆盖**：AC1, AC5, AC8-AC12
**产出**：`skills/sdd/shared/git-workflow.md` + `docs/current/README.md` + 重写 `README.md`

### Step 1: F1 — git-workflow.md

使用 `write_file`，路径 `skills/sdd/shared/git-workflow.md`，内容从 design.md **F1 完整内容**复制。

验证：
```bash
test -f skills/sdd/shared/git-workflow.md && echo "✓"
grep -q "分支命名" skills/sdd/shared/git-workflow.md && grep -q "PR 流程" skills/sdd/shared/git-workflow.md && grep -q "PR 描述模板" skills/sdd/shared/git-workflow.md && grep -q "Squash merge" skills/sdd/shared/git-workflow.md && grep -q "main 分支保护" skills/sdd/shared/git-workflow.md && echo "✓ all sections"
```

### Step 2: F3 — docs/current/README.md

使用 `write_file`，路径 `docs/current/README.md`，内容从 design.md **F3 完整内容**复制。

验证：
```bash
test -f docs/current/README.md && echo "✓"
grep -q "项目状态" docs/current/README.md && grep -q "架构概览" docs/current/README.md && grep -q "Skill 清单" docs/current/README.md && grep -q "变更历史" docs/current/README.md && grep -q "001-sdd-init" docs/current/README.md && grep -q "002-project-onboarding" docs/current/README.md && echo "✓ all sections"
```

### Step 3: F4 — README.md 重写

使用 `write_file` **完全覆盖** `README.md`，内容从 design.md **F4 完整内容**复制。

验证：
```bash
head -5 README.md | grep -q "Hermes Harness" && echo "✓ Hero title"
head -5 README.md | grep -q "让 AI Agent" && echo "✓ Hero tagline"
grep -q "完整 Skill 目录" README.md && grep -q "项目结构" README.md && grep -q "设计哲学" README.md && echo "✓ all sections"
for skill in sdd-orchestrator po-agent ba-agent architect-agent coder-agent reviewer-agent qa-agent sdd-init sdd-structure-lint; do
    grep -q "$skill" README.md || echo "✗ $skill MISSING"
done && echo "✓ all 9 skills"
```

### Step 4: Commit

```bash
git add skills/sdd/shared/git-workflow.md docs/current/README.md README.md
git commit -m "feat(git+docs): T1 git-workflow + docs/current/ 基线 + README 重写"
```

---

## T2: F2 — orchestrator Phase 8 替换

**估时**：10min
**依赖**：T1（F1/F3 文件先存在，F2 引用它们）
**AC 覆盖**：AC2, AC3, AC4, AC6, AC7
**产出**：修改 `skills/sdd/sdd-orchestrator/SKILL.md`

### Step 1: 执行 patch

使用 `patch` 工具，文件 `skills/sdd/sdd-orchestrator/SKILL.md`。

**old_string**（来自 design.md F2）：
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

**new_string**（来自 design.md F2，以 `#### Step 8.0: R10 检查` 开头的完整内容块）。

### Step 2: 验证

```bash
grep -q "Step 8.0: R10 检查" skills/sdd/sdd-orchestrator/SKILL.md && echo "✓ 8.0 R10"
grep -q "Step 8.1: 基线融合" skills/sdd/sdd-orchestrator/SKILL.md && echo "✓ 8.1 baseline"
grep -q "git branch --show-current" skills/sdd/sdd-orchestrator/SKILL.md && echo "✓ branch detection"
grep -q "git log -5 --oneline --merges" skills/sdd/sdd-orchestrator/SKILL.md && echo "✓ merge detection"
grep -q "bypass-r10" skills/sdd/sdd-orchestrator/SKILL.md && echo "✓ bypass"
grep -q "Step 8.5: 输出归档摘要" skills/sdd/sdd-orchestrator/SKILL.md && echo "✓ 8.5 summary"
```

### Step 3: Commit

```bash
git add skills/sdd/sdd-orchestrator/SKILL.md
git commit -m "feat(git): T2 orchestrator Phase 8 — R10 检查 + 基线融合"
```

---

## T3: 全量验证 + PR

**估时**：10min
**依赖**：T1, T2
**AC 覆盖**：全 12 AC

### Step 1: 文件完整性

```bash
echo "=== 新增文件 ==="
test -f skills/sdd/shared/git-workflow.md && echo "✓ git-workflow.md" || echo "✗"
test -f docs/current/README.md && echo "✓ docs/current/README.md" || echo "✗"
echo "=== 修改文件 ==="
grep -q "Step 8.0" skills/sdd/sdd-orchestrator/SKILL.md && echo "✓ orchestrator updated" || echo "✗"
grep -q "设计哲学" README.md && echo "✓ README rewritten" || echo "✗"
```

### Step 2: R10 逻辑烟火测试

```bash
BRANCH=$(git branch --show-current)
echo "Current branch: $BRANCH"
MERGE_COUNT=$(git log -5 --oneline --merges 2>/dev/null | wc -l)
echo "Recent merges: $MERGE_COUNT"
# 在 feature 分支上，MERGE_COUNT 应为 0，归档时应被 R10 阻断
```

### Step 3: Commit + Push feature 分支

```bash
git add -A
git diff --cached --stat
git commit -m "feat(git): T3 验证 — 全 AC 文件完整性 + R10 烟火测试"
git push origin feat/003-git-and-docs
```

### Step 4: 创建 PR（dogfooding）

在 GitHub 创建 Pull Request：
- **base**: `main` ← **head**: `feat/003-git-and-docs`
- **标题**: `feat(git+docs): 003 Git 工作流 + 基线维护 + README 升级`
- **描述**: 使用 git-workflow.md 中定义的 PR 模板

### Step 5: Review + Squash Merge

评审通过后，在 GitHub Web UI 执行 **Squash merge**。

---

## 汇总

| # | Task | 估时 | 产出 | AC 覆盖 |
|---|------|:---:|------|:---:|
| T1 | F1 + F3 + F4 并行创建 | 20min | 3 文件 (2 新 + 1 重写) | AC1, AC5, AC8-AC12 |
| T2 | F2 orchestrator Phase 8 patch | 10min | 1 修改 | AC2-AC7 |
| T3 | 验证 + PR + merge | 10min | PR | 全 AC |
| **总计** | | **40min** | **4 文件** | **12 AC** |
