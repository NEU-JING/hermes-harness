# SDD 通用开发机制 — 补充方案

> 解决两个缺失：**产物目录结构约束** + **项目启动/升级机制**

---

## 一、产物目录结构约束机制

### 1.1 问题

当前方案仅在 AGENTS.md 声明了 `changes_dir: "docs/changes/"`，实际执行时 Agent 可能：
- 将 prd.md 写到 `docs/` 而非 `docs/changes/001-xxx/`
- 使用不一致的 change-id 格式
- 忘记创建 `current/` 和 `archive/` 层级

### 1.2 方案：结构化约定 + Lint 验证

**目录骨架（强制执行）**：

```
{project}/
├── AGENTS.md                     # 项目配置（声明 changes_dir 等）
├── CONSTITUTION.md               # 项目宪法
├── QUIRKS.md                     # 已知陷阱
│
├── docs/
│   ├── changes/                  # 进行中的变更（SDD 工作区）
│   │   └── NNN-short-name/       # 每个变更一个目录
│   │       ├── prd.md
│   │       ├── spec.md
│   │       ├── design.md
│   │       ├── tasks.md
│   │       ├── qa-report.md
│   │       └── ac-coverage.md
│   │
│   ├── current/                  # 当前生产版（merge 后更新）
│   │   ├── prd.md
│   │   ├── spec.md
│   │   ├── design.md
│   │   └── architecture.md       # 全局架构文档
│   │
│   └── archive/                  # 历史变更归档
│       └── NNN-short-name/       # merge 后从 changes/ 移入
│           └── ...（prd/spec/design/tasks/qa）
```

**约束规则（写入 `sdd-orchestrator` 和每个角色 skill 的退出条件）**：

| 规则编号 | 约束 | 违反后果 |
|---------|------|---------|
| C1 | 每个变更必须在 `{changes_dir}/NNN-short-name/` 下 | 编排器拒绝启动下一阶段 |
| C2 | change-id 必须是 `NNN-short-name` 格式（3 位数字 + 短横线 + 英文短名） | 编排器报错并提示正确格式 |
| C3 | 每个阶段产物必须写入约定文件名（prd.md / spec.md / design.md / tasks.md / qa-report.md） | 角色 skill 退出前自检，不满足不交接 |
| C4 | 归档条件：CI 全绿 + E2E CI 全绿 + 用户验收通过 | 编排器检查 CI 状态，不满足不归档 |
| C5 | merge 到 main 后，变更目录必须从 `changes/` 移至 `archive/`，同时更新 `current/` | CI post-merge hook 自动执行 |

### 1.3 实现：`sdd-structure-lint` Skill

```markdown
---
name: sdd-structure-lint
description: >
  验证项目 SDD 目录结构是否符合约定。
  在编排器启动时和每个阶段交接前自动运行。
category: sdd
---

# SDD Structure Lint

## 触发条件
- 编排器启动时（验证项目骨架完整）
- 每个角色交接前（验证当前变更目录符合约定）

## 检查项

### 项目级
- [ ] `{project}/AGENTS.md` 存在且含 `changes_dir` 声明
- [ ] `{project}/CONSTITUTION.md` 存在
- [ ] `{changes_dir}/` 目录存在
- [ ] `{changes_dir}/current/` 目录存在
- [ ] `{changes_dir}/archive/` 目录存在

### 变更级（当前活跃变更）
- [ ] change-id 符合 `NNN-short-name` 格式
- [ ] 目录 `{changes_dir}/{change-id}/` 存在
- [ ] 前置阶段的产物文件已存在（如 Spec 阶段检查 prd.md 存在）

### 交接前（角色退出时）
- [ ] 当前阶段产物文件已写入
- [ ] 文件大小 > 0（非空壳）
- [ ] 对于 prd.md/spec.md：含必要的章节标题（目标/AC 等）

## 被禁用行为
- ❌ lint 失败时不能继续（必须修复后重试）
```

### 1.4 编排器中的调用点

```
sdd-orchestrator 启动
  → skill_view('sdd/sdd-structure-lint')  # 验证项目骨架
  → 判定流程级别
  → 进入阶段 1（PRD）

PO Agent 启动
  → skill_view('sdd/sdd-structure-lint')  # 验证 change-id + 目录
  → 查找 changes_dir 下最大 NNN → 自动递增
  → 创建 {changes_dir}/{new-id}/ 目录
  → 产出 prd.md → 写入
  → 退出前：skill_view('sdd/sdd-structure-lint')  # 自检

PO → 交接 → BA
  → skill_view('sdd/sdd-structure-lint')  # 验证 prd.md 存在
  → 产出 spec.md → 写入
  → 退出前自检

...（后续阶段同理）
```

---

## 二、项目启动/升级机制

### 2.1 问题

- **新项目**：如何确保开发者一开始就接入 SDD 框架（而非"先写代码，后补流程"）？
- **存量项目**：已有代码和文档，如何无痛升级到 SDD 框架？
- **持续遵守**：如何防止开发者绕过 SDD 直接写代码？

### 2.2 方案：`sdd-init` Skill

新增一个 **项目初始化 Skill**，类似 `npm init` 或 `git init`，在项目根目录运行后自动搭建骨架。

**新项目模式**：

```
用户：我要开始一个新项目

编排器：
  1. 检测当前目录无 AGENTS.md → 触发 sdd-init
  2. sdd-init 交互式询问：
     - 项目名称？
     - 技术栈？（FastAPI / Go / Next.js / ...）
     - 数据库？（SQLite / PostgreSQL / MongoDB）
     - 流程级别偏好？（Quick / Standard / Enhanced）
  3. 自动生成：
     - AGENTS.md（根据回答填充配置）
     - CONSTITUTION.md（根据技术栈选默认模板）
     - QUIRKS.md（空模板）
     - docs/changes/（空目录）
     - docs/current/（空目录）
     - docs/archive/（空目录）
     - .pre-commit-config.yaml（black + isort + ruff）
  4. 输出：SDD 项目骨架已就绪，你可以开始第一个变更了
```

**存量项目模式**：

```
用户：我想把现有项目接入 SDD

编排器：
  1. 检测到 AGENTS.md 已存在但结构不完整 → 触发 sdd-upgrade
  2. sdd-upgrade 分析现有项目：
     - 扫描现有文档（PRD/Design 等）
     - 检测现有 CI 配置
     - 检测现有测试框架
  3. 生成升级计划（列出：哪些文件移动、哪些新建、哪些保留）
  4. 用户确认后执行：
     - 将散落文档按约定移动到对应位置
     - 补充缺失的 CONSTITUTION.md / QUIRKS.md
     - 生成 AGENTS.md（保留现有内容，补充缺失字段）
     - 如果检测到现有流程（如 AGENTS.md 中的旧流程描述），保留并标记为"legacy"
  5. 输出：升级完成，现有文件未丢失，SDD 框架已就绪
```

### 2.3 `sdd-init` Skill 详细设计

```markdown
---
name: sdd-init
description: >
  初始化或升级项目的 SDD 开发框架。
  新项目：交互式搭建骨架。存量项目：分析→计划→确认→迁移。
category: sdd
---

# SDD Init

## 触发条件
- 编排器检测到项目缺少 AGENTS.md 或 AGENTS.md 中无 `flow_engine` 字段
- 用户说"接入 SDD 流程"或"初始化 SDD"

## 模式一：新项目初始化

### Step 1: 检测项目状态
```
if 不存在 AGENTS.md:
    → 新项目模式
else if AGENTS.md 中无 flow_engine 字段:
    → 升级模式
```

### Step 2: 交互式询问
```
clarify([
  "项目名称？",
  "一句话描述？",
  "后端技术栈：A) FastAPI  B) Go  C) Spring Boot  D) 其他",
  "前端技术栈：A) React  B) Vue  C) 无前端",
  "数据库：A) SQLite(dev)/PostgreSQL(prod)  B) PostgreSQL only  C) MongoDB",
  "默认流程级别：A) Quick  B) Standard  C) Enhanced",
])
```

### Step 3: 生成骨架
```
生成文件：
  AGENTS.md              ← 根据回答填充
  CONSTITUTION.md        ← 根据技术栈选默认模板
  QUIRKS.md              ← 空模板（含常见陷阱占位）
  docs/changes/.gitkeep  ← 空占位
  docs/current/.gitkeep  ← 空占位
  docs/archive/.gitkeep  ← 空占位
  .pre-commit-config.yaml ← black + isort + ruff

AGENTS.md 模板（新项目）：
  flow_engine: "sdd/sdd-orchestrator"
  changes_dir: "docs/changes/"
  current_dir: "docs/current/"
  archive_dir: "docs/archive/"
  constitution: "CONSTITUTION.md"
  quirks: "QUIRKS.md"
  tech_stack: {按回答填充}
```

### Step 4: 验证
```
skill_view('sdd/sdd-structure-lint')  # 验证骨架完整
```

## 模式二：存量项目升级

### Step 1: 分析现有状态
```
扫描：
  - 现有 AGENTS.md 内容 → 提取可保留的配置
  - 现有文档文件 → 列出路径，建议迁移目标
  - 现有 CI 配置 → 检查是否冲突
  - 现有 pre-commit 配置 → 检查是否冲突
```

### Step 2: 生成升级计划
```
输出升级计划（markdown），列出：
  📁 新建文件：
    - CONSTITUTION.md（模板）
    - QUIRKS.md（模板）
    - docs/changes/（目录）
    - docs/current/（目录）
    - docs/archive/（目录）

  📦 移动文件：
    - docs/some-prd.md → docs/current/prd.md
    - old-specs/ → docs/archive/001-legacy/

  ✏️ 修改文件：
    - AGENTS.md（增加 flow_engine 等字段）
    - .gitignore（增加 docs/current/ 排除规则）

  ⚠️ 冲突项：
    - CI 配置中有重复的 lint 步骤（建议保留 SDD 版本）
```

### Step 3: 用户确认
```
clarify("以上升级计划是否确认执行？", choices=["确认执行", "仅生成计划文件"])
```

### Step 4: 执行迁移
```
按计划执行 → 所有移动操作用 git mv（保留历史）
```

## 被禁用行为
- ❌ 不能删除任何现有文件（只移动或新增）
- ❌ 不能覆盖用户修改过的文件（检测 git status 中的 modified 文件）
- ❌ 存量升级未确认前不能执行任何写操作
```

---

## 三、与其他机制的衔接

| 机制 | 衔接点 |
|------|--------|
| **pre-commit hooks** | `sdd-init` 自动生成 `.pre-commit-config.yaml` |
| **CI 配置** | `sdd-init` 检测现有 CI，不冲突时补充 E2E workflow |
| **sdd-structure-lint** | 编排器每次启动和阶段交接前调用 |
| **角色 skills** | 每个角色的退出条件中包含 `skill_view('sdd/sdd-structure-lint')` |
| **QUIRKS.md** | 每次修复一个陷阱后，更新 QUIRKS.md（通过 post-commit hook） |

---

## 四、修订后的 Phase 计划

在原 4 个 Phase 基础上，补充：

| Phase | 内容 | 估时 | 新增理由 |
|-------|------|------|---------|
| **Phase 0** 🆕 | `sdd-init` + `sdd-structure-lint` 两个 skill | 2h | 解决启动机制和目录约束 |
| Phase 1 | po-agent 模板验证 | 1h | 不变 |
| Phase 2 | 批量生成 6 个角色 skill | 3h | 不变 |
| Phase 3 | AILP 适配（AGENTS.md 精简） | 1h | 现在包含了 sdd-init 的存量升级测试 |
| Phase 4 | 通用化验证 | 1.5h | 在新项目上跑 sdd-init |
| **Phase 5** 🆕 | AILP 存量升级实战（用 `sdd-upgrade` 模式迁移 AILP 项目） | 1h | 验证存量升级路径 |

**总估时：6.5h → 9.5h**
