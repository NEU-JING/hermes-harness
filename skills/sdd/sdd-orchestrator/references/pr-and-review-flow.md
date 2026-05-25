# PR 与 Review 回退流程

> 本文档记录 Coder → Reviewer → QA → 验收 阶段的 Git PR 工作流和回退机制。
> 这是 003-git-and-docs 变更中实际踩过的坑和修正方案。

---

## PR 生命周期

```
Coder push feature 分支 → GitHub 创建 PR（保持 OPEN）
  → Reviewer 在 PR 上评审
  → QA 验证
  → 用户验收
  → 验收通过 → Squash merge → main
  → 归档（R10 检测到 merge commit → 通过）
```

**关键原则**：PR 在验收通过前**不合并**。

---

## Reviewer 不通过的修复循环

```
Coder → Reviewer（第 1 轮）
  ├── 通过 → QA
  └── 不通过 → Coder 修复 → Reviewer（第 2 轮）
       ├── 通过 → QA
       └── 不通过 → 用户介入决策（不自动循环）
```

**.sdd-state.json 增强字段**：
```json
{
  "review_round": 2,
  "previous_review_outcome": "不通过 — 1 CRITICAL (描述)"
}
```

**熔断规则**：连续 2 轮 Reviewer 不通过 → 用户介入，不复自动循环。

---

## 本次 003 变更的实战案例

### 问题 1: PR merge 时机错误

- **现象**：Coder T3 中直接 squash merge 了 PR #1
- **根因**：git-workflow.md 第 1 版写的是"Reviewer 通过 → Squash merge"
- **修正**：PR 流程改为 9 步，merge 在第 8 步（验收通过后）

### 问题 2: Reviewer 第 1 轮不通过

- **现象**：Reviewer 发现 CRITICAL #1 — orchestrator R10 检查依赖加载 git-workflow.md
- **修复**：改为纯 git 命令检测，git-workflow.md 降级为人类可读参考
- **结果**：修复后第 2 轮 Review 通过

### 问题 3: 基线融合概念纠正

- **现象**：初始设计将基线融合理解为"变更日志追加"
- **纠正**：基线 = PRD + Spec + Design 逐章节融合后的"当前生产全貌"
- **修复**：Step 8.1 改为 5 个子步骤的融合逻辑（8.1.1-8.1.5）

### 问题 4: Commit 落在 main 而非 feature 分支（本次 session）

- **现象**：SDD 003 的 commits 直接 commit 到了 main 分支，用户反馈"我没有看到 pr 请求呢"
- **根因**：Coder 阶段未切到 feature 分支就开始编码；git-workflow 规范尚未生效（本身是 003 的产出）
- **影响**：无 PR 可审查，违反 R10
- **修复流程**（恢复技巧）：
  1. `git reset --hard <SDD 003 之前的 commit>` — 回退 main
  2. `git checkout feat/###-xxx && git reset --hard <same base>` — 重置 feature 分支
  3. `git cherry-pick <c1> <c2> ... <cn>` — 把 SDD 003 的 commits 搬到 feature 分支
  4. `git push origin main --force` — 推送干净 main
  5. `git push origin feat/###-xxx --force` — 推送 feature 分支
  6. `gh pr create --base main --head feat/###-xxx ...` — 创建 PR
- **教训**：git-workflow 规范需在 SDD 流程**开始前**就绪，不能是"自己成为自己的产出"
