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

4. 在 GitHub 创建 Pull Request（保持 OPEN）
   - 标题：feat({scope}): {变更简述}
   - 描述：使用 PR 模板

5. Reviewer 评审（在 PR 上进行）
   - 通过 → 进入 QA 阶段
   - 有条件通过 → 修复后更新 PR
   - 不通过 → 修复 CRITICAL 后更新 PR

6. QA 验证（在 PR 合并前完成）

7. 用户验收

8. 验收通过 → Squash merge → main
   所有 commit 压缩为一个，保持 main 线性历史

9. 归档（此时 R10 检测到 merge commit → 通过）
```

> ⚠️ **PR 在验收通过前不合并**。合并后的归档阶段，R10 通过 git log 检测 merge commit 来验证 PR 流程。
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
