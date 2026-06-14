# Design — OpenSpec 启发改进

> **技术设计方案**
> 变更 ID：003-openspec-improvements
> 版本：2.0 | 最后更新：2026-06-08
> 基于 Spec：`docs/changes/003-openspec-improvements/spec.md`

---

## 1. Brainstorming 方案对比

### P3 — 探索模式

| 方案 | 描述 | 复杂度 | 优点 | 缺点 |
|------|------|:------:|------|------|
| **A: 新增 Skill** | 创建 `explore-agent` Skill，加载后进入探索对话 | ⭐⭐ | 独立职责、可复用、低耦合 | 需新增一个 Skill 文件 |
| B: 修改 orchestrator | 在编排器中增加探索入口状态 | ⭐⭐⭐ | 状态机统一管理 | 增加编排器复杂度，偏离其职责 |
| C: AGENTS.md 提示词 | 在项目 AGENTS.md 中写探索指引 | ⭐ | 零代码改动 | 无结构化支持、不可跨项目复用 |

**选定方案 A**：新增 `explore-agent` Skill，SDD 流程入口前加载。

### P4 — Spec 格式统一（OpenSpec WHEN/THEN + AC 编号）

| 方案 | 描述 | 复杂度 | 优点 | 缺点 |
|------|------|:------:|------|------|
| **A: OpenSpec 单一格式** | BA Agent 直接采用 OpenSpec WHEN/THEN + AND 链格式，不再兼容原生表格式 | ⭐⭐ | 简洁、标准统一、与社区对齐 | 存量项目需迁移 |
| B: 双格式兼容 | BA Agent 同时支持 OpenSpec 格式和原生表格式，自动检测 | ⭐⭐⭐ | 过渡平滑 | 复杂度高、维护两套模板 |
| C: 仅表格式优化 | 保留原生表格，增加 AND 链支持 | ⭐⭐⭐ | 零迁移成本 | 与 OpenSpec 社区不兼容 |

**选定方案 A**：单一 OpenSpec WHEN/THEN + AND 链格式，AC 编号嵌入 `#### Scenario AC{n}:`。存量项目通过 convention_overrides 声明格式迁移计划。

### P8 — Spec Delta 语义

| 方案 | 描述 | 复杂度 | 优点 | 缺点 |
|------|------|:------:|------|------|
| **A: 按 capability 分目录** | Change 内 specs/ 按 capability 分目录，与主 spec 结构一致；使用 ## 操作头标记 delta | ⭐⭐⭐⭐ | 与 OpenSpec 完全对齐、语义清晰 | 合并逻辑需维护 |
| B: Git diff 方式 | 利用 git diff 作为 delta 语义 | ⭐⭐⭐ | 零开发 | 无法表达"新增/删除/修改"语义，只适用已提交的变更 |
| C: YAML 元数据文件 | 在 .openspec.yaml 中定义 spec 变更项 | ⭐⭐⭐ | 结构化明确 | 增加维护负担，不如 Markdown 直观 |

**选定方案 A**：Change 内 specs/ 按 capability 分目录，使用 `## ADDED/MODIFIED/REMOVED/RENAMED Requirements` 操作头。同步机制写入 sdd-orchestrator 归档流程。

### P7 — Telemetry

| 方案 | 描述 | 复杂度 | 优点 | 缺点 |
|------|------|:------:|------|------|
| **A: 本地 JSON 日志** | orchestrator 在关键阶段输出结构化日志到本地文件 | ⭐⭐ | 最简单、免依赖 | 无查询界面 |
| B: 本地 SQLite + CLI | 数据写入 SQLite，提供 `telemetry report` CLI | ⭐⭐⭐ | 可查询、可统计 | 需 SQLite 依赖 |
| C: Hub 上报 | 数据发送到中央服务 | ⭐⭐⭐⭐ | 全局统计 | 隐私风险、网络依赖 |

**选定方案 A**：阶段转换时 orchestrator 追加 JSON 行到本地日志文件。

---

## 2. 架构设计

### 整体架构

```
┌──────────────────────────────────────────────────────────┐
│                   Hermes-Harness v2.2                     │
│                                                           │
│  ┌──────────────────┐    ┌─────────────────────────────┐ │
│  │  explore-agent    │    │  sdd-orchestrator            │ │
│  │  (新 Skill)       │───▶│  (增强: delta sync + tele)   │ │
│  └──────────────────┘    └──────┬──────────────────────┘ │
│                                 │                        │
│  ┌──────────────────────────────▼──────────────────────┐ │
│  │  BA Agent (增强: OpenSpec WHEN/THEN 模板)            │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  docs/                                              │ │
│  │  ├── specs/                    ← 基线（按 capability 分目录）│
│  │  │   ├── <capability>/spec.md                      │ │
│  │  │   └── ...                                       │ │
│  │  ├── changes/{id}/                                  │ │
│  │  │   ├── specs/                ← Delta（结构与基线一致）│
│  │  │   │   └── <capability>/spec.md                   │ │
│  │  │   ├── proposal.md                                │ │
│  │  │   ├── design.md                                  │ │
│  │  │   ├── tasks.md                                   │ │
│  │  │   └── .sdd-state.json                            │ │
│  │  ├── archive/                                       │ │
│  │  └── current/ (deprecated)                          │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ~/.hermes/telemetry/*.log    ← 新 (本地日志)             │
└──────────────────────────────────────────────────────────┘
```

> **结构变化**：基线从单一 `docs/current/spec.md` 改为 `docs/specs/<capability>/spec.md` 多文件结构，与 OpenSpec `openspec/specs/` 对齐。`docs/current/` 保留用于 PRD/Design/Tasks 等非 spec 文档。

### P3 — 探索模式设计

**新增文件**：`skills/sdd/explore-agent/SKILL.md`

```
skills/sdd/explore-agent/
├── SKILL.md              # 角色定义 + prompt
└── references/
    └── explore-guide.md  # 探索引导问题模板
```

**SKILL.md 核心内容**：
- 触发词：`/explore`（用户输入）或 `explore-agent`（编排器触发）
- 行为：进入自由对话模式，AI 不主动创建任何文件
- 支持：代码库分析、方案对比、需求澄清
- 退出方式：
  - 用户说"放弃" → 清理对话状态，不留产物
  - 用户说"/sdd start" → 探索摘要（optionally）传递给 PO Agent 作为 PRD 输入源

**集成到编排器**：在 IDLE → PO_ENTRY 之间增加可选路径

```
IDLE → (用户输入 /explore) → EXPLORE_ENTRY → (探索结束) → 放弃 → IDLE
                                                          → /sdd start → PO_ENTRY
```

### P4 — Spec 格式统一（OpenSpec WHEN/THEN + AC 编号）

**OpenSpec 的 Spec 格式**：

需求与场景使用层次化 Markdown 结构，场景条件用 bullet 列表 + WHEN/THEN + AND 链。

```markdown
### Requirement: 命令执行追踪
系统 SHALL 在 CLI 命令执行时发送匿名统计事件。

#### Scenario AC1: 标准命令执行
- **WHEN** 用户运行任意 openspec 命令
- **THEN** 系统发送 `command_executed` 事件

#### Scenario AC2: 环境变量生效
- **WHEN** 用户之前使用过 CLI（config 存在）
- **AND** 用户设置了 `OPENSPEC_TELEMETRY=0`
- **THEN** 无论 config 如何，telemetry 关闭
```

**格式要素**：

| 要素 | 格式 | 说明 |
|------|------|------|
| 需求头 | `### Requirement: <name>` + 自然语言描述 | 使用 SHALL/MUST（RFC 2119） |
| 场景头 | `#### Scenario AC{n}: <name>`（**严格 4 个 #**） | AC 编号嵌入标题 |
| 前置条件 | `- **WHEN** <condition>`（bullet 格式） | 每个条件一行 |
| 多条件链 | `- **AND** <additional>` | 多前置用 AND 连接 |
| 预期结果 | `- **THEN** <outcome>` | |
| 规范强度 | SHALL / MUST | RFC 2119 词汇表 |

**设计决策**：
- 单一格式：OpenSpec WHEN/THEN + AND 链
- 不兼容原生 Hermes 表格式（存量项目需迁移）
- AC 编号直接嵌入 `#### Scenario AC{n}:`，无需在状态文件中独立维护编号

**修改文件**：
1. `skills/sdd/ba-agent/references/spec-template.md` → 改为 OpenSpec WHEN/THEN + AND 链 + AC 编号格式
2. `skills/sdd/ba-agent/SKILL.md` → 更新 AC 编写规范，注明格式要求
3. `skills/sdd/sdd-structure-lint/SKILL.md` → 更新 AC 提取逻辑

**AC 提取逻辑**：
```
正则匹配 /#### Scenario AC(\d+):/ 
→ 提取 AC 编号 + 所属 Requirement + 后续 WHEN/THEN/AND 内容
→ 用于 Lint 检查和 QA 覆盖率验证
```

### P8 — Spec Delta 语义设计

**OpenSpec 的 Delta 机制**：

OpenSpec 的 spec 系统采用 **按 capability 分目录** 结构，基线（主 spec）和变更（delta）的结构一致：

```
openspec/
├── specs/                          # 主 spec（基线，已合并的最新版本）
│   ├── telemetry/spec.md
│   └── cli-init/spec.md
│
└── changes/<name>/
    ├── specs/                      # Delta spec（只存变更）
    │   ├── cli-init/spec.md        # 与主 spec 同名目录
    │   └── profiles/spec.md
    ├── proposal.md
    ├── design.md
    └── tasks.md
```

**Delta spec 格式**：使用 `##` 级操作头标记变更类型

```markdown
## ADDED Requirements

### Requirement: 技能生成（新增）
系统 SHALL 根据 active profile 生成技能，而非固定集。

#### Scenario AC24: Core profile 技能生成
- **WHEN** 用户以 profile `core` 运行 init
- **THEN** 系统为核心工作流生成技能

## MODIFIED Requirements

### Requirement: 工具自动检测
系统 SHALL 通过扫描项目根目录来检测已安装的 AI 工具。

#### Scenario AC10: 从目录检测
- **WHEN** 扫描工具
- **THEN** 检查 .claude/ .cursor/ .windsurf/ 等目录

## REMOVED Requirements

### Requirement: 遗留导出功能
**Reason**: 被新导出系统替代
**Migration**: 使用 /api/v2/export

## RENAMED Requirements
- FROM: `旧名称`
- TO: `新名称`
```

**Delta 操作头类型**：

| 操作头 | 语义 | 内容要求 |
|--------|------|---------|
| `## ADDED Requirements` | 新增 capability 或 requirement | 完整 requirement 内容 |
| `## MODIFIED Requirements` | 修改已有 requirement | **必须包含完整更新内容**（非仅 diff），Requirement 标题应与基线精确匹配 |
| `## REMOVED Requirements` | 废弃 requirement | 包含 **Reason** 和 **Migration** 字段 |
| `## RENAMED Requirements` | 仅重命名 | FROM:/TO: 格式 |

**同步机制**（归档时 sdd-orchestrator 执行）：

1. 读取 `changes/<name>/specs/<capability>/spec.md`（delta）
2. 查找 `docs/specs/<capability>/spec.md`（主 spec）
3. 根据 delta 操作头逐条处理：
   - **ADDED**：如果 requirement 不存在 → 添加；如果已存在 → 更新
   - **MODIFIED**：替换主 spec 中的对应 requirement
   - **REMOVED**：从主 spec 中移除
   - **RENAMED**：重命名 requirement
4. 新的 capability → 创建 `docs/specs/<capability>/spec.md`
5. 输出变更摘要：`Added: N, Modified: M, Removed: D, Renamed: R`

**Hermes-Harness 适配后全貌**：

基线结构（从 `docs/current/spec.md` 单文件改为 `docs/specs/` 多文件）：

```
docs/
├── specs/                          # 基线 spec（按 capability 分目录）
│   ├── <capability>/
│   │   └── spec.md
│   └── ...
├── changes/{change_id}/            # 活跃变更
│   ├── specs/                      # Delta spec（与基线结构一致）
│   │   └── <capability>/
│   │       └── spec.md             # 使用 ## ADDED/MODIFIED/REMOVED/RENAMED
│   ├── proposal.md                 # 变更动机
│   ├── design.md                   # 技术方案（归档时保留）
│   ├── tasks.md                    # 实施清单
│   └── .sdd-state.json             # 状态机快照
├── archive/                        # 归档变更（只读历史）
│   └── <change_id>/
│       ├── proposal.md             # 保留
│       ├── design.md               # 保留原始版本（含 Brainstorming + 关键决策）
│       ├── tasks.md                # 保留（含已完成标记）
│       ├── qa-report.md            # 保留（如 QA 阶段产生）
│       ├── review-report.md        # 保留（如 Review 阶段产生）
│       ├── specs/                   # Delta spec（保留原始 delta，不合并为全量）
│       │   └── <capability>/
│       │       └── spec.md
│       └── manifest.json           # 归档元数据（新增）
└── current/                        # 基线文档（持续累积）
    ├── prd.md                      # 产品需求基线
    ├── design.md                   # 设计基线（每次归档追加/合并关键决策）
    └── ...
```

**完整归档流程**（sdd-orchestrator ARCHIVE_ENTRY 阶段）：

```
ARCHIVE_ENTRY:
  │
  ├─ Step 1: 读取 .sdd-state.json
  │   └─ 记录归档时间戳、最终状态
  │
  ├─ Step 2: 检查 docs/changes/{id}/specs/ 是否存在
  │   ├─ 存在 → 执行 Spec Sync:
  │   │      1. 遍历 changes/{id}/specs/<capability>/
  │   │      2. 查找 docs/specs/<capability>/spec.md（基线）
  │   │      3. 按 ## ADDED/MODIFIED/REMOVED/RENAMED 操作头逐条合并
  │   │      4. 生成 sync 报告: Added N / Modified M / Removed D / Renamed R
  │   │      5. 写入 docs/changes/{id}/.sync-report.md
  │   └─ 不存在 → 跳过（向后兼容传统全量模式）
  │
  ├─ Step 3: 合并 design.md 到设计基线
  │   ├─ 检查 docs/changes/{id}/design.md 是否存在
  │   ├─ 读取 docs/current/design.md（如不存在则创建）
  │   ├─ 追加变更的设计摘要：
  │   │      ## {change_name} ({archived_at})
  │   │      参考: archive/{id}/design.md（完整版）
  │   │      ### 关键决策
  │   │      - {决策1}: {选择} — {理由}
  │   │      - {决策2}: {选择} — {理由}
  │   │      ### 架构变更
  │   │      - {变更描述}
  │   │      ### 模块变更
  │   │      - {变更描述}
  │   ├─ 写入 docs/current/design.md（追加模式）
  │   └─ 原始 design.md 保留在 archive/{id}/ 供查阅
  │
  ├─ Step 4: 生成归档元数据
  │   ├─ 写入 manifest.json:
  │   │   {
  │   │     "change_id": "...",
  │   │     "archived_at": "2026-06-08T12:00:00Z",
  │   │     "phase_count": 4,
  │   │     "specs_synced": true,
  │   │     "sync_summary": {"added": 2, "modified": 1, "removed": 0, "renamed": 0},
  │   │     "state": "done",
  │   │     "artifacts": ["proposal.md", "design.md", "tasks.md", ...]
  │   │   }
  │   └─ 删除 .sdd-state.json（状态已固化到 manifest.json）
  │
  ├─ Step 5: 整体迁移
  │   ├─ mv docs/changes/{id} → docs/archive/{id}/
  │   └─ 确认目标目录无冲突
  │
  └─ Step 6: R10 门禁检查
      ├─ PR 已合并 ✅
      ├─ archive/ 结构完整 ✅
      └─ current/ 基线已更新 ✅
```

**各产物在归档中的处理**：

| 产物 | 活跃期 | 归档后 | 原因 |
|------|--------|--------|------|
| `proposal.md` | changes/{id}/ | archive/{id}/ | 保留"为什么做"的历史 |
| **`design.md`** | changes/{id}/ | → 摘要 → **docs/current/design.md**（基线追加） + **archive/{id}/design.md**（完整版） | 关键决策融入设计基线，完整版本存档备查 |
| `tasks.md` | changes/{id}/ | archive/{id}/ | 保留实施清单（含完成标记） |
| `specs/<capability>/spec.md` | changes/{id}/ → sync → docs/specs/ | archive/{id}/specs/ | 原始 delta 和基线同步两份都保留 |
| `.sdd-state.json` | changes/{id}/ | → 转为 manifest.json 后删除 | 状态固化 |
| `review-report.md` | changes/{id}/ | archive/{id}/ | 保留评审记录 |
| `qa-report.md` | changes/{id}/ | archive/{id}/ | 保留 QA 记录 |

**向后兼容**：存量 Change 无 delta spec 结构时，跳过 Step 2，直接执行 Step 3-5，保留传统归档行为。

### P7 — Telemetry 设计

**新增文件**：`skills/sdd/sdd-orchestrator/references/telemetry.md`

**数据格式**（JSON Lines）：
```json
{"timestamp": "2026-06-08T10:00:00Z", "command": "/sdd start", "phase_from": null, "phase_to": "PO_ENTRY", "duration_ms": 0}
{"timestamp": "2026-06-08T10:05:00Z", "command": null, "phase_from": "PO_ENTRY", "phase_to": "PO_CHECK", "duration_ms": 300000}
{"timestamp": "2026-06-08T10:06:00Z", "command": null, "phase_from": "PO_CHECK", "phase_to": "PO_DONE", "duration_ms": 60000}
```

**数据存储位置**：`~/.hermes/telemetry/{change_id}/events.ndjson`

**控制方式**：
- AGENTS.md: `telemetry: enabled: true`（默认 false）
- 环境变量：`HERMES_TELEMETRY_DISABLE=1` → 强制关闭
- 环境变量：`DO_NOT_TRACK=1` → 强制关闭

---

## 3. 模块设计

### 模块 1：explore-agent（新增）

| 属性 | 值 |
|------|-----|
| 目录 | `skills/sdd/explore-agent/` |
| 核心文件 | `SKILL.md`（~50 行） |
| 依赖 | 无 |
| AC 覆盖 | AC1-AC6 |
| 验证方式 | 加载 skill 后测试 `/explore` 流程 |

### 模块 2：ba-agent 增强（修改）

| 属性 | 值 |
|------|-----|
| 修改文件 | `SKILL.md` + `references/spec-template.md` |
| 变更内容 | spec-template.md 改为 OpenSpec WHEN/THEN + AND 链 + `#### Scenario AC{n}:` 格式；SKILL.md 更新 AC 编写规范 |
| AC 覆盖 | AC7-AC11 |
| 验证方式 | 用新模板生成 spec，确认 AC 编号顺序正确、WHEN/THEN/AND 格式符合规范 |

### 模块 3：sdd-orchestrator 增强（修改）

| 属性 | 值 |
|------|-----|
| 修改文件 | `SKILL.md` |
| 变更内容 | ARCHIVE_ENTRY 阶段增加 6 步完整归档流程：spec sync（delta→docs/specs/)、design.md 摘要合并到 docs/current/design.md（设计基线）、manifest.json 生成、整体迁移、R10 门禁；基线从单文件 `docs/current/spec.md` 改为 `docs/specs/<capability>/spec.md` 多文件；阶段转换时记录 telemetry |
| AC 覆盖 | AC12-AC17（delta）+ AC18-AC23（telemetry） |
| 验证方式 | 创建带 delta 的 Change，执行归档，检查 spec sync 结果 + manifest.json + design.md 在 archive/ 中保留 |

### 模块 4：baseline spec 结构迁移

| 属性 | 值 |
|------|-----|
| 新增文件 | 见下方 |
| 变更内容 | 基线从 `docs/current/spec.md` 单文件 → `docs/specs/<capability>/spec.md` 多文件；sdd-init 模板同时更新 |
| AC 覆盖 | AC12-AC17（与 delta 共享） |
| 验证方式 | 初始化新项目，确认 `docs/specs/` 结构正确 |

### 模块 5：telemetry 子系统（新增）

| 属性 | 值 |
|------|-----|
| 新增文件 | `references/telemetry.md` |
| 数据位置 | `~/.hermes/telemetry/` |
| AC 覆盖 | AC18-AC23 |
| 验证方式 | 启用 telemetry → 执行一次 SDD 流程 → 检查日志文件 |

---

## 4. 关键决策记录

| 决策 | 选项 | 选择 | 理由 |
|------|------|------|------|
| 探索模式实现方式 | Skill / 编排器修改 / 提示词 | Skill | 独立、可复用、低耦合 |
| Spec 格式 | hermes-native / openspec-when-then | openspec-when-then | 单一格式，与 OpenSpec 社区对齐；AC 编号嵌入 `#### Scenario AC{n}:` |
| Baseline spec 结构 | 单文件 / 按 capability 分目录 | 按 capability 分目录 | 与 OpenSpec 对齐，支持 delta 语义 |
| Delta 操作方式 | ## 操作头 / git diff / YAML | ## 操作头 | 与 OpenSpec 完全一致，语义清晰 |
| Telemetry 存储 | JSON 文件 / SQLite / 中央 Hub | JSON 文件 | 最简单、零依赖 |
| Telemetry 默认状态 | 开启 / 关闭 | 关闭 | 隐私优先 |
