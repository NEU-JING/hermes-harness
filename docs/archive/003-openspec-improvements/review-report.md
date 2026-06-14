# Review Report — OpenSpec 启发改进

> **变更 ID**: 003-openspec-improvements
> **变更分支**: feat/003-openspec-improvements
> **PR**: #8
> **评审日期**: 2026-06-09
> **评审人**: Reviewer Agent
> **评审范围**: 10 files, +828/−71 (SKILL.md + references/*.md)
> **评审类型**: Initial Review（三阶段全量评审）

---

## 评审结论

**❌ 不通过** — 存在 2 个 CRITICAL 问题（Spec-Design 矛盾），需打回修正后重新 Review。

| 指标 | 数值 |
|------|:----:|
| CRITICAL | 2 |
| MAJOR | 0 |
| MINOR | 5 |
| INFO | 2 |
| AC 覆盖 | 21/23（AC6、AC11 未覆盖） |

---

## Phase 1: Spec 合规

> 逐个检查 AC1-AC23 是否被变更文件覆盖，验证功能行为与 Spec 描述一致。

### AC 覆盖矩阵

| AC | 描述 | 覆盖文件 | 状态 | 证据 |
|:--:|------|---------|:----:|------|
| **AC1** | 启动 `/explore` 进入自由对话 | explore-agent/SKILL.md (Workflow Step 1-2) | ✅ | "不创建任何文件" + "支持：代码库分析、方案对比" |
| **AC2** | 代码库调研 | explore-agent/SKILL.md (Step 2) + explore-guide.md | ✅ | "代码库调研引导" 章节含具体引导问题 |
| **AC3** | 方案对比 | explore-guide.md (方案对比引导) | ✅ | 结构化对比表模板 + 推荐格式 |
| **AC4** | 放弃探索 | explore-agent/SKILL.md (Step 3) | ✅ | "\"放弃\" 或 \"取消\" → 清理对话状态，不留产物" |
| **AC5** | 进入 SDD | explore-agent/SKILL.md (Step 3-4) | ✅ | "/sdd start → PO_ENTRY，探索摘要可选传递" |
| **AC6** | 中断恢复 | — | ❌ | **未实现**：explore-agent 无对话持久化/恢复机制 |
| **AC7** | WHEN/THEN 格式识别 | sdd-structure-lint 3.2 + AC 提取规则 | ✅ | 正则 `/#### Scenario AC(\d+):/` 正确提取 |
| **AC8** | 双格式共存 | — | ❌ | **Spec-Design 矛盾**: Spec 要求双格式兼容，Design 选定方案 A（单一格式） |
| **AC9** | 项目格式偏好 | — | ❌ | **Spec-Design 矛盾**: `convention_overrides.spec_format` 在设计中被移除 |
| **AC10** | 默认格式 | ba-agent/SKILL.md (Step 3) + spec-template.md | ✅ | 默认使用 OpenSpec WHEN/THEN 格式 |
| **AC11** | AC 提取一致性 | — | ⚠️ | 依赖 AC8（双格式），当前单格式实现下无法验证 |
| **AC12** | Delta 目录创建 | orchestrator Step 2 + sdd-init | ✅ | `docs/specs/` 创建 + Change 内 specs/ 目录 |
| **AC13** | 增量修改标记 | delta-spec.md (## MODIFIED Requirements) | ✅ | "必须包含完整更新内容（非仅 diff）" |
| **AC14** | 新增 AC 标记 | delta-spec.md (## ADDED Requirements) | ✅ | "完整内容（非仅新增行）" |
| **AC15** | 删除 AC 标记 | delta-spec.md (## REMOVED Requirements) | ✅ | "必须包含 Reason 和 Migration 字段" |
| **AC16** | 归档合并 | orchestrator ARCHIVE_ENTRY Step 2 + Step 4 | ✅ | sync 报告含 added/modified/removed/renamed 统计 |
| **AC17** | 向后兼容 | delta-spec.md 向后兼容规则 + orchestrator Step 2 skip | ✅ | "存 Change 无 delta 结构时跳过 spec sync" |
| **AC18** | 默认关闭 | sdd-init (AGENTS.md template) + telemetry.md | ✅ | `# telemetry:\n#   enabled: false`（注释状态） |
| **AC19** | 显式启用 | telemetry.md + orchestrator telemetry 代码 | ✅ | AGENTS.md `telemetry: enabled: true` |
| **AC20** | 数据范围限制 | telemetry.md 隐私承诺 | ✅ | "绝不记录文件内容、路径、项目名" |
| **AC21** | 本地存储 | telemetry.md 数据存储章节 | ✅ | `~/.hermes/telemetry/{change_id}/events.ndjson` |
| **AC22** | TELEMETRY_DISABLE 退出 | orchestrator telemetry 代码 + telemetry.md | ✅ | `HERMES_TELEMETRY_DISABLE` 环境变量检查 |
| **AC23** | DO_NOT_TRACK 隐私 | orchestrator telemetry 代码 + telemetry.md | ✅ | `DO_NOT_TRACK` 优先于任何配置 |

### CRITICAL 问题详解

#### C1: AC6 未覆盖 — 探索模式中断恢复

| 项 | 内容 |
|----|------|
| **AC** | AC6：探索被意外中断 → 用户重新进入 `/explore` → 可查看上次探索的对话摘要 |
| **现状** | explore-agent/SKILL.md 无任何会话持久化或恢复机制。Workflow 仅描述开始→对话→退出三步 |
| **Spec 要求** | "中断恢复：探索被意外中断 → 可查看上次探索的对话摘要" |
| **影响** | 用户意外退出后探索内容丢失，需从头开始 |
| **修复建议** | (1) 若 AC6 确需实现：在 explore-agent SKILL.md 增加 Step 5 "中断恢复"，说明如何持久化探索摘要到临时文件 (2) 若 AC6 暂不实现：在 Spec 中将 AC6 标记为 "Out of Scope for v1" 或降级到后续变更 |

#### C2: AC8/AC9 Spec-Design 矛盾 — 双格式兼容被移除

| 项 | 内容 |
|----|------|
| **AC** | AC8：spec.md 混合两种格式 → Lint 正确识别两种格式的 AC |
| **AC** | AC9：`convention_overrides.spec_format` 设置为偏好格式 → BA Agent 使用偏好格式 |
| **Design 决策** | "选定方案 A：单一 OpenSpec WHEN/THEN + AND 链格式…不兼容原生 Hermes 表格式（存量项目需迁移）" |
| **实现** | ba-agent SKILL.md 明确写 "**不保留** Hermes 原生表格式"；lint 规则移除了表格式检查 |
| **冲突** | Spec 要求支持双格式共存，Design 和实现选择了单一格式 |
| **影响** | AC8 和 AC9 无法验证，Spec 文档与实际功能不匹配 |
| **修复建议** | **方案 A（推荐）**: 更新 Spec，将 AC8 改为"单格式迁移：存量项目 spec 以 OpenSpec 格式重写"，将 AC9 改为"存量项目通过 convention_overrides 声明迁移窗口"；**方案 B**: 回退 Design 和实现，改为双格式兼容 |

---

## Phase 2: 文档质量

> 检查 YAML frontmatter、引用路径、内容质量和格式规范。

### YAML Frontmatter 验证

**结果**: ✅ 全部 10 个 SKILL.md 通过 YAML frontmatter 验证（name + description 完整）。

### References 引用路径验证

| 引用声明 | 位置 | 目标存在 | 状态 |
|---------|------|:---:|:----:|
| `references/explore-guide.md` | explore-agent/SKILL.md L11-12 | ✅ | ✅ |
| `references/delta-spec.md` | sdd-orchestrator/SKILL.md L17 | ✅ | ✅ |
| `references/design-baseline.md` | sdd-orchestrator/SKILL.md L18 | ✅ | ✅ |
| `references/telemetry.md` | sdd-orchestrator/SKILL.md L19 | ✅ | ✅ |
| `references/spec-template.md` | ba-agent/SKILL.md L13 | ✅ | ✅ |
| `references/ac-writing-guide.md` | ba-agent/SKILL.md L12 | ✅ | ✅ |

### 文件行数统计

| 文件 | 行数 | 目标 | 状态 |
|------|:---:|------|:----:|
| explore-agent/SKILL.md | 77 | ~70 (PRD) | ⚠️ 略超 |
| explore-guide.md | 111 | 无限制 | ✅ |
| delta-spec.md | 175 | 无限制 | ✅ |
| design-baseline.md | 115 | 无限制 | ✅ |
| telemetry.md | 97 | 无限制 | ✅ |

### MINOR 问题

#### M1: explore-agent SKILL.md 略超行数目标

| 项 | 内容 |
|----|------|
| **严重级别** | MINOR |
| **文件** | `skills/sdd/explore-agent/SKILL.md` |
| **问题** | 77 行，PRD NFR 要求 "新增 SKILL.md ≤ 70 行" |
| **建议** | 可精简 Step 4 的探索摘要模板（当前 7 行）或 When to Use 列表 |

#### M2: ba-agent SKILL.md 拼写错误

| 项 | 内容 |
|----|------|
| **严重级别** | MINOR |
| **文件** | `skills/sdd/ba-agent/SKILL.md:48` |
| **问题** | `Acceptence Criteria` → 应为 `Acceptance Criteria` |
| **建议** | 修正拼写 |

#### M3: orchestrator References 章节不同步

| 项 | 内容 |
|----|------|
| **严重级别** | MINOR |
| **文件** | `skills/sdd/sdd-orchestrator/SKILL.md:491-497` |
| **问题** | 底部 `## References` 手动列表未包含 3 个新增引用（delta-spec.md, design-baseline.md, telemetry.md），但 frontmatter 已正确列出 |
| **建议** | 在 `## References` 小节补充 3 个新文件的链接和描述 |

#### M4: Spec 模板中 Requirement 命名不一致

| 项 | 内容 |
|----|------|
| **严重级别** | MINOR |
| **文件** | `skills/sdd/ba-agent/references/spec-template.md:15` vs `docs/changes/003-openspec-improvements/spec.md:18` |
| **问题** | 模板使用 `### Requirement: {需求名称}` 但本变更自己的 spec.md 详细需求仍用 `### 需求 1：` 中文格式（AC 部分已改为新格式） |
| **建议** | 本变更的 spec.md 的详细需求章节也应改为 `### Requirement:` 格式以自我示范 |

#### M5: Telemetry 保留策略 Spec-Design 不一致

| 项 | 内容 |
|----|------|
| **严重级别** | MINOR |
| **文件** | `references/telemetry.md:86` vs `spec.md` AC21 |
| **问题** | telemetry.md 写 "60 天后自动清理"，Spec AC21 写 "可查询最近 30 天"；虽然 60>30 功能不受影响，但文档不一致 |
| **建议** | 统一为 30 天（与 Spec 对齐）或更新 Spec 为 60 天 |

---

## Phase 3: 架构一致性

> 检查实现是否偏离 Design 文档，模块划分、数据流、关键技术决策是否一致。

### 模块实现对照

| Design 模块 | 实现文件 | 一致性 | 说明 |
|:-----------|---------|:---:|------|
| 模块 1: explore-agent | `skills/sdd/explore-agent/SKILL.md` + `references/explore-guide.md` | ✅ | 独立 Skill，触发词 `/explore`，无依赖，AC 覆盖与设计一致 |
| 模块 2: ba-agent 增强 | `skills/sdd/ba-agent/SKILL.md` + `references/spec-template.md` | ✅ | 模板改为 OpenSpec 格式，SKILL.md Step 3 更新，Quality Standards 更新 |
| 模块 3: orchestrator 增强 | `skills/sdd/sdd-orchestrator/SKILL.md` | ✅ | 6 步归档流程完整，telemetry 记录，delta sync 逻辑 |
| 模块 4: 基线结构迁移 | `skills/sdd/sdd-init/SKILL.md` + `sdd-structure-lint/SKILL.md` | ✅ | `docs/specs/` 多文件基线，sdd-init 创建空目录，lint L1 检查 |
| 模块 5: telemetry 子系统 | `references/telemetry.md` + orchestrator telemetry 代码 | ✅ | NDJSON 格式，环境变量控制，隐私边界清晰 |

### 关键决策验证

| Design 决策 | 选择 | 实现 | 状态 |
|------------|------|------|:---:|
| 探索模式实现 | Skill | explore-agent SKILL.md | ✅ |
| Spec 格式 | openspec-when-then（单一格式） | ba-agent + spec-template.md | ✅ |
| 基线结构 | 按 capability 分目录 | `docs/specs/<capability>/` | ✅ |
| Delta 操作方式 | ## 操作头 | delta-spec.md ADDED/MODIFIED/REMOVED/RENAMED | ✅ |
| Telemetry 存储 | JSON 文件 | NDJSON 追加 | ✅ |
| Telemetry 默认 | 关闭 | sdd-init 注释状态 | ✅ |

### 跨 Skill 一致性检查

| 检查项 | 涉及文件 | 状态 |
|--------|---------|:---:|
| `docs/specs/` 目录 | sdd-init (创建) ↔ sdd-structure-lint (L1 检查) ↔ orchestrator (Step 2 sync) | ✅ |
| AC 提取正则 | ba-agent (产出) ↔ sdd-structure-lint (提取) | ✅ 同一正则 |
| Telemetry 事件类型 | orchestrator (记录) ↔ telemetry.md (定义) | ✅ transition/delegate/user_confirm/lint_check |
| Manifest.json 字段 | orchestrator Step 4 ↔ design-baseline.md | ✅ 格式一致 |

### 向后兼容验证

| 场景 | 机制 | 状态 |
|------|------|:---:|
| 存量 Change 无 delta specs/ | orchestrator Step 2 skip | ✅ |
| 存量项目无 `docs/specs/` | sdd-init upgrade 模式创建 | ✅ |
| `docs/specs/` 初始为空 | lint 标记为 "可空目录" | ✅ |
| design.md 不存在 | design-baseline.md "自动创建" | ✅ |

### INFO 问题

#### I1: SDD 状态文件未更新

| 项 | 内容 |
|----|------|
| **严重级别** | INFO |
| **文件** | `docs/changes/003-openspec-improvements/.sdd-state.json` |
| **问题** | `current_phase` 仍为 `coder_entry`，各 phase status 为 `not_started`，与实际完成状态不一致 |
| **说明** | 这是运行时状态文件，由 orchestrator 维护。作为 INFO 记录，提示实施完成但状态机未推进 |

#### I2: 本次变更自身未使用 Delta Spec 结构

| 项 | 内容 |
|----|------|
| **严重级别** | INFO |
| **问题** | 本变更 `docs/changes/003-openspec-improvements/` 下无 `specs/` 子目录，使用了传统全量 spec.md |
| **说明** | 合理 — 这是基线变更，首次引入 delta 概念，无需自举。但应在归档时作为首个变更填充 `docs/specs/` |

---

## 问题汇总

| # | 严重级别 | 类别 | 文件 | 问题 | 修复建议 |
|:--:|:----:|------|------|------|---------|
| C1 | **CRITICAL** | Phase 1 | explore-agent/SKILL.md | AC6 中断恢复未实现 | 实现会话持久化或将 AC6 标记为 Out of Scope |
| C2 | **CRITICAL** | Phase 1 | spec.md vs design.md | AC8/AC9 Spec-Design 矛盾：双格式 vs 单格式 | 更新 Spec 对齐 Design（推荐）或回退实现 |
| M1 | MINOR | Phase 2 | explore-agent/SKILL.md | 行数 77 > 目标 70 | 精简内容 |
| M2 | MINOR | Phase 2 | ba-agent/SKILL.md:48 | "Acceptence" 拼写错误 | 改为 "Acceptance" |
| M3 | MINOR | Phase 2 | sdd-orchestrator/SKILL.md:491 | References 小节缺失新引用 | 补充 3 个新 reference 文件的链接 |
| M4 | MINOR | Phase 2 | 003 自身的 spec.md:18 | 详细需求仍用中文格式 | 改为 `### Requirement:` 格式 |
| M5 | MINOR | Phase 2 | telemetry.md:86 vs spec.md AC21 | 保留策略 60 天 vs 30 天 | 统一数字 |
| I1 | INFO | Phase 3 | .sdd-state.json | 状态文件未推进 | 由 orchestrator 归档时更新 |
| I2 | INFO | Phase 3 | — | 本变更未使用 delta spec 结构 | 归档时填充 docs/specs/ |

---

## SDD 状态

```yaml
change_id: "003-openspec-improvements"
current_state: REVIEWER_CHECK
review_status: not_passed
review_url: "docs/changes/003-openspec-improvements/review-report.md"
review_conclusion: "不通过（C1: AC6 未覆盖, C2: AC8/AC9 Spec-Design 矛盾）"
next_action: "打回 Coder 修复 CRITICAL 问题后重新 Review"
updated_at: "2026-06-09"
```
