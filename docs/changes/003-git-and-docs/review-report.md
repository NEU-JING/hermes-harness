# Review Report: Git 工作流 + 基线维护 + README 升级

**变更 ID**：003-git-and-docs
**评审日期**：2026-05-25
**评审范围**：4 files，+458/-14（dfa8e11 + fbcfac4）

---

## 评审结论

**结论：❌ 不通过 — 1 CRITICAL**

CRITICAL 问题需修复后重新提交 Review。

---

## Phase 1: Spec 合规

| AC | 描述 | 验证 | 结果 |
|:---:|------|------|:---:|
| AC1 | git-workflow.md 存在且完整 | 文件存在，含分支命名/PR流程/模板/合并策略/main保护 | ✅ |
| AC2 | orchestrator 阻断非 main 归档 | `git branch --show-current` 逻辑正确 | ✅ |
| AC3 | orchestrator 通过 PR merge 检测 | `git log -5 --oneline --merges` 逻辑正确 | ✅ |
| AC4 | --bypass-r10 豁免 | 代码中存在 bypass 分支 | ✅ |
| AC5 | docs/current/ 初始化 | 文件存在，含项目状态/架构/Skill清单/变更历史 | ✅ |
| AC6 | 归档时基线追加变更历史 | Step 8.1.5 逻辑正确 | ✅ |
| AC7 | 归档时 Skill 清单更新 | Step 8.1.4 逻辑正确 | ✅ |
| AC8 | README Hero 区域 | 首屏含标题 + "让 AI Agent 按工程规范协作" | ✅ |
| AC9 | README Skill 目录表 | 9 个 Skill 全覆盖，按阶段分组 | ✅ |
| AC10 | README 多平台安装 | 3 种折叠式（Hermes/手动/兼容） | ✅ |
| AC11 | README 项目结构树 | ASCII 树完整 | ✅ |
| AC12 | README 设计哲学 | 含"为什么需要 SDD"和 ad-hoc 对比表 | ✅ |

**Phase 1 结果：12/12 AC** ✅

---

## Phase 2: 代码/文档质量

| 检查项 | 结果 | 说明 |
|------|:---:|------|
| DRY | ✅ | 无重复 |
| YAGNI | ✅ | 每文件职责明确 |
| 命名清晰 | ✅ | git-workflow.md, docs/current/README.md |
| 结构完整 | ✅ | 4 文件各章节齐全 |

### 发现的问题

| # | 严重级别 | 文件 | 问题 | 修复建议 |
|---|:---:|------|------|------|
| 1 | **CRITICAL** | `skills/sdd/sdd-orchestrator/SKILL.md` Step 8.0 | R10 检查引用了 `sdd/shared/git-workflow.md`，但该文件在 F1 中定义——这意味着 **orchestrator 的 R10 检查依赖 sdd-init 已将 git-workflow.md 安装到 `~/.hermes/skills/sdd/shared/`**。如果用户跳过 install.sh 或 git-workflow.md 未被 Skill 系统索引，R10 检查将因"文件不存在"而失败，而非正确判定为"应阻断"或"应通过" | 增加容错：若 git-workflow.md 不可用，退化为纯 git 命令检测（分支检查 + merge 记录），并输出警告"git-workflow.md 未安装，使用基本检测" |

---

## Phase 3: 架构一致性

| 检查项 | Design 约定 | 实际实现 | 结果 |
|------|------|------|:---:|
| git-workflow.md 位置 | `skills/sdd/shared/` | `skills/sdd/shared/` | ✅ |
| orchestrator Phase 8 结构 | 8.0→8.5 五步 | 五步齐全 | ✅ |
| 基线融合逻辑 | 逐章节增量融合 | 8.1.1-8.1.5 完整 | ✅ |
| README 章节 | Hero+流程+安装+目录+结构+哲学 | 6 章齐全 | ✅ |

### 架构偏离

无。

---

## 总结

| 阶段 | 结果 |
|------|:---:|
| Phase 1: Spec 合规 | ✅ 12/12 AC |
| Phase 2: 代码质量 | ❌ 1 CRITICAL |
| Phase 3: 架构一致性 | ✅ 无偏离 |

**需要修复**：CRITICAL #1 — orchestrator R10 对 git-workflow.md 的依赖缺少容错。修复后重新提交 Review。
