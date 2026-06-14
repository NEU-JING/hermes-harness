# Tasks — OpenSpec 启发改进

> **实施任务清单（增量模式）**
> 变更 ID：003-openspec-improvements
> 版本：2.0 | 最后更新：2026-06-08
> AC 总数：23（AC1-AC23）

---

## Phase 1: 探索模式 [可独立交付]

**AC 覆盖**: AC1-AC6
**估时**: 3 个 Task × ~5min = 15min
**交付标准**: `/explore` 可正常启动 → 自由对话 → 可退出或进入 SDD

### T1: 创建 explore-agent SKILL.md

- **路径**: `skills/sdd/explore-agent/SKILL.md`
- **内容**:
  - YAML frontmatter（name、description、tags）
  - 角色定义：探索模式 Agent
  - 触发方式：`/explore` 命令
  - 行为规则：不创建文件、支持代码分析、方案对比
  - 退出方式：放弃 或 过渡到 SDD 流程
  - 交付物：探索摘要（可选传递给 PO Agent）
- **验证**: `skill_view(name='explore-agent')` 正常加载
- **依赖**: 无

### T2: 创建探索引导参考文档

- **路径**: `skills/sdd/explore-agent/references/explore-guide.md`
- **内容**: 探索引导问题模板（帮助用户展开需求）
  - "请描述你想做什么"
  - "需要调研代码库吗？"
  - "对比哪些方案？"
  - "是否需要可视化图表？"
- **验证**: 文件存在、格式正确

### T3: 集成到 sdd-orchestrator 入口流程

- **路径**: `skills/sdd/sdd-orchestrator/SKILL.md`
- **修改**：
  - 在 IDLE → PO_ENTRY 路径旁增加 optional `/explore` 分支
  - 状态说明中增加 EXPLORE 状态说明（非正式状态，仅标注存在）
  - 注明探索结束后如何过渡到 PO_ENTRY
- **验证**: 阅读 SKILL.md，确认路径描述清晰

---

## Phase 2: Spec 格式统一（OpenSpec WHEN/THEN + AC 编号）[依赖 Phase 1]

**AC 覆盖**: AC7-AC11
**估时**: 3 个 Task × ~5min = 15min
**交付标准**: BA Agent 使用 `#### Scenario AC{n}:` + WHEN/THEN + AND 链格式；Lint 正确提取 AC 编号

### T4: 修改 spec-template.md 为 OpenSpec WHEN/THEN + AC 编号格式

- **路径**: `skills/sdd/ba-agent/references/spec-template.md`
- **修改**:
  - 模板从 Hermes 表格式改为 OpenSpec WHEN/THEN + AND 链格式
  - 示例使用 `#### Scenario AC{n}: <name>` 场景头
  - 条件使用 `- **WHEN** <condition>` / `- **AND** <condition>` / `- **THEN** <outcome>` bullet 列表
  - 需求头使用 `### Requirement: <name>` + SHALL/MUST 描述
  - **注意**：不保留 Hermes 原生表格式，不做双格式兼容
- **验证**: 打开模板，确认 WHEN/THEN/AND 示例清晰、AC 编号格式正确

### T5: 更新 BA Agent SKILL.md AC 编写规范

- **路径**: `skills/sdd/ba-agent/SKILL.md`
- **修改**:
  - Workflow Step 3 中更新 AC 编写规范：`#### Scenario AC{n}:` + WHEN/THEN + AND 链
  - 增加场景示例：多条件 AND 链的写法
  - 更新 Quality Standards：AC 编号连续性检查、WHEN/THEN/AND 完整性
  - 移除双格式兼容相关说明
- **验证**: 阅读 SKILL.md，确认 AC 编写指引完整正确

### T6: 更新 sdd-structure-lint AC 提取逻辑

- **路径**: `skills/sdd/sdd-structure-lint/SKILL.md`
- **修改**:
  - AC 提取规则改为正则 `/#### Scenario AC(\d+):/`
  - 提取 AC 编号 + 所属 Requirement（向上查找 `### Requirement:`）
  - 提取 WHEN/THEN/AND 条件内容
  - 检查 AC 编号连续性、不重复
  - 移除 Hermes 表格式检查规则
- **验证**: 用 OpenSpec 格式的 spec 样本测试，AC 提取结果正确

---

## Phase 3: Baseline 结构迁移 + Spec Delta 语义 [依赖 Phase 2]

**AC 覆盖**: AC12-AC17
**估时**: 5 个 Task × ~8min = 40min
**交付标准**: 基线从 `docs/current/spec.md` 单文件迁移到 `docs/specs/<capability>/spec.md` 多文件；Change 支持 delta 结构和归档 6 步流程

### T7: 创建 delta spec 格式参考文档

- **路径**: `skills/sdd/sdd-orchestrator/references/delta-spec.md`（新增）
- **内容**:
  - Delta 操作头定义：`## ADDED/MODIFIED/REMOVED/RENAMED Requirements`
  - 操作头内容要求：
    - ADDED：完整 requirement 内容
    - MODIFIED：**必须包含完整更新内容**（非仅 diff）
    - REMOVED：包含 **Reason** 和 **Migration** 字段
    - RENAMED：FROM:/TO: 格式
  - Delta 目录结构：`specs/<capability>/spec.md`（与基线一致）
  - 归档同步机制说明：6 步流程 + 示例
  - 向后兼容说明（存量 Change 无 delta 结构时不报错）
- **验证**: 文件存在，格式清晰

### T8: 更新 sdd-orchestrator SKILL.md 归档流程（6 步）

- **路径**: `skills/sdd/sdd-orchestrator/SKILL.md`
- **修改**: 将 ARCHIVE_ENTRY 阶段的归档流程更新为完整 6 步：
  - **Step 1**: 读取 .sdd-state.json，记录时间戳
  - **Step 2**: Spec Sync — 遍历 `changes/{id}/specs/<capability>/`，按 ## 操作头合并到 `docs/specs/<capability>/spec.md`，生成 sync 报告
  - **Step 3**: Design 基线合并 — 读取 `changes/{id}/design.md`，提取关键决策和架构变更，追加到 `docs/current/design.md`
  - **Step 4**: 生成 manifest.json（含 change_id、archived_at、sync_summary、artifacts 列表），删除 .sdd-state.json
  - **Step 5**: 整体迁移 `mv changes/{id} → archive/{id}/`
  - **Step 6**: R10 门禁检查（PR / archive 结构 / current 基线）
- **验证**: 阅读 SKILL.md 确认归档流程完整

### T9: 修改 sdd-init 初始化模板（支持新基线结构）

- **路径**: `skills/sdd/sdd-init/SKILL.md`
- **修改**:
  - 创建新项目时，基线结构从 `docs/current/spec.md` 改为 `docs/specs/` 目录
  - `docs/specs/` 初始为空目录，等待首个 Change 归档时创建第一个 capability spec
  - Change 初始化时（`/sdd start`），如果 `docs/specs/` 中存在基线，自动创建空的 `specs/<capability>/` 目录
  - `docs/current/` 保留用于 PRD / Design / Tasks 等非 spec 文档
  - 移除 `docs/current/spec.md` 创建逻辑
- **验证**: 初始化新项目，确认 `docs/specs/` 结构正确，`docs/current/` 无 spec.md

### T10: 更新 sdd-structure-lint 支持新基线路径

- **路径**: `skills/sdd/sdd-structure-lint/SKILL.md`
- **修改**:
  - Lint L1 检查：spec 基线路径从 `docs/current/spec.md` 改为 `docs/specs/`
  - Lint L2 检查：Change 内 `specs/` 目录结构（按 capability）
  - Lint L3 检查：delta 操作头格式（ADDED/MODIFIED/REMOVED/RENAMED）
- **验证**: 运行 lint 检查新旧结构项目，正确识别

### T11: 创建 design 基线合并参考文档

- **路径**: `skills/sdd/sdd-orchestrator/references/design-baseline.md`（新增）
- **内容**:
  - `docs/current/design.md` 的格式规范
  - 归档时 design.md 摘要模板（关键决策 / 架构变更 / 模块变更）
  - 追加写入规范（每次归档新增 ## 章节）
  - 参考 archive/{id}/design.md 完整版指引
- **验证**: 文件存在，格式清晰

---

## Phase 4: Telemetry 匿名统计 [可独立交付]

**AC 覆盖**: AC18-AC23
**估时**: 3 个 Task × ~5min = 15min
**交付标准**: 编排器在阶段转换时自动记录；默认关闭；退出机制生效

### T12: 创建 telemetry 配置参考文档

- **路径**: `skills/sdd/sdd-orchestrator/references/telemetry.md`（新增）
- **内容**:
  - 数据格式定义（JSON Lines）：`{timestamp, command, phase_from, phase_to, duration_ms}`
  - 数据存储位置（`~/.hermes/telemetry/{change_id}/events.ndjson`）
  - 启用方式（AGENTS.md: `telemetry: enabled: true`）
  - 禁用方式（`HERMES_TELEMETRY_DISABLE=1` / `DO_NOT_TRACK=1`）
  - 隐私承诺：仅记录命令名、阶段名、耗时，不记录文件内容/路径/项目名
- **验证**: 文件存在，格式清晰

### T13: 更新 sdd-orchestrator SKILL.md 添加 telemetry 步骤

- **路径**: `skills/sdd/sdd-orchestrator/SKILL.md`
- **修改**: 在每个阶段转换步骤中添加 telemetry 记录：
  - 转换前：检查 telemetry 是否启用 + `DO_NOT_TRACK`/`HERMES_TELEMETRY_DISABLE` 环境变量
  - 启用时：追加 JSON line 到 `~/.hermes/telemetry/{change_id}/events.ndjson`
  - 数据：`{timestamp, command, phase_from, phase_to, duration_ms}`
- **验证**: 阅读 SKILL.md 确认 telemetry 记录点完整

### T14: 更新 sdd-init 默认 telemetry 配置

- **路径**: `skills/sdd/sdd-init/SKILL.md`
- **修改**:
  - sdd-init 产出的 AGENTS.md 模板中增加 `# telemetry: enabled: false`（默认关闭注释）
  - 添加注释说明如何启用和退出
- **验证**: 执行 sdd-init，检查 AGENTS.md 是否包含 telemetry 注释行

---

## 执行顺序

```
Phase 1: T1 → T2 → T3  (探索模式)
                              ↓
Phase 2: T4 → T5 → T6  (Spec 格式统一)
                              ↓
Phase 3: T7 → T8 → T9 → T10 → T11  (Delta + Baseline 迁移)
                              ↓
Phase 4: T12 → T13 → T14  (Telemetry)
```

## Phase 依赖图

```
Phase 1 (探索模式)  ──►  Phase 2 (格式统一)  ──►  Phase 3 (Delta + 基线迁移)
                                                                              
Phase 4 (Telemetry)  ──  无依赖，可与 Phase 1 并行                          
```

## 变更清单（与旧 tasks.md 对照）

| 旧 Task | 新 Task | 变更说明 |
|:-------:|:-------:|---------|
| T1-T3 | T1-T3 | 基本不变 |
| T4 | T4 | 格式从 GIVEN/WHEN/THEN 改为 OpenSpec WHEN/THEN + AND 链 + `#### Scenario AC{n}:` |
| T5 | T5 | 从"双格式说明"改为"单一格式 AC 编写规范" |
| T6 | T6 | 从"双格式识别"改为"正则提取 `#### Scenario AC{n}:`" |
| T7 | T7 | 从 delta.md + .base.md 改为 `specs/<capability>/spec.md` 含 ## 操作头 |
| T8 | T8 | 从 4 行简化流程改为 6 步完整归档（含 design 基线合并、manifest.json） |
| T9 | T9 | 从 .base.md 快照改为 `docs/specs/` 多文件基线结构 |
| — | T10 | **新增**：lint 检查新基线路径 |
| — | T11 | **新增**：design 基线合并参考文档 |
| T10 | T12 | 不变 |
| T11 | T13 | 不变 |
| T12 | T14 | 不变 |
