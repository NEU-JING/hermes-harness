# Design: SDD 通用开发机制

> 版本：V2.1
> 日期：2026-05-25
> 作者：Architect Agent
> 前置 Spec：docs/changes/001-sdd-init/spec.md
>
> 本文档面向 Coder Agent，定义实现所需的全部技术细节。Agent 按此文档逐节实现即可。

---

## 一、产出物清单

本变更产出以下文件。Coder Agent 按此清单逐文件创建。

### 1.1 Skills（写入 `~/.hermes/skills/sdd/`）

```
sdd/
├── sdd-init/
│   └── SKILL.md                              # 项目初始化与升级
│
├── sdd-structure-lint/
│   └── SKILL.md                              # 三级合规验证
│
├── sdd-orchestrator/
│   └── SKILL.md                              # 编排器：流程判定 + 调度 + 门禁 + 归档
│
├── po-agent/
│   ├── SKILL.md                              # PO Agent 核心指令
│   └── references/
│       └── prd-template.md                   # PRD 模板
│
├── ba-agent/
│   ├── SKILL.md                              # BA Agent 核心指令
│   └── references/
│       ├── spec-template.md                  # Spec 模板
│       └── ac-writing-guide.md               # AC 编写指南
│
├── architect-agent/
│   ├── SKILL.md                              # Architect Agent 核心指令
│   └── references/
│       ├── design-template.md                # Design 模板
│       ├── tasks-template.md                 # Tasks 模板
│       └── brainstorming-guide.md            # Brainstorming 指南
│
├── coder-agent/
│   ├── SKILL.md                              # Coder Agent 核心指令
│   └── references/
│       ├── tdd-workflow.md                   # TDD 工作流
│       ├── nfr-checklist.md                  # 非功能需求检查清单
│       └── task-completion-report-template.md
│
├── reviewer-agent/
│   ├── SKILL.md                              # Reviewer Agent 核心指令
│   └── references/
│       ├── review-checklist.md               # 评审检查清单
│       └── severity-guide.md                 # 严重程度分级指南
│
├── qa-agent/
│   ├── SKILL.md                              # QA Agent 核心指令
│   └── references/
│       ├── qa-report-template.md             # QA 报告模板
│       ├── e2e-ac-mapping-template.md        # E2E-AC 覆盖矩阵模板
│       └── circuit-breaker.md                # 熔断机制规则
│
└── shared/
    ├── handoff-protocol.md                   # 角色交接协议
    ├── flow-level-rules.md                   # 流程级别判定规则
    ├── convention-overrides.md               # 可覆盖约定清单
    └── sdd-rules.md                          # SDD 通用规则定义（R1-R10）
```

### 1.2 模板文件（由 sdd-init 生成到项目目录）

```
{project}/
├── .pre-commit-config.yaml                   # pre-commit + pre-push hooks（Python 项目模板）
├── pytest.ini                                # pytest 配置（含 ci_only marker，Python 项目）
├── .git/hooks/post-commit                    # post-commit hook（陷阱修复提示）
│
└── docs/templates/                           # 文档模板（可选，供项目自定义）
    ├── agnets-template.md                    # 新项目 AGENTS.md 模板
    └── constitution-template.md              # 新项目 CONSTITUTION.md 模板
```

**总计**：16 个 SKILL.md + 15 个 references + 2 个 docs 模板 + 3 个 hooks/配置文件 = **36 个文件**。

---

## 二、每个 Skill 的详细设计

### 2.1 sdd-orchestrator（编排器）

**文件**：`sdd/orchestrator/SKILL.md`

**Frontmatter**：
```yaml
name: sdd-orchestrator
description: >
  SDD 编排器 — 流程级别判定、角色调度、门禁管理、合规验证、归档。
  读取 AGENTS.md 获取项目配置，按 SDD 阶段顺序调度角色 Agent。
category: sdd
version: 1.0.0
```

**核心指令结构**（详细到 Agent 可逐行执行）：

```markdown
# SDD Orchestrator

## 触发条件
- 用户说"开始一个新变更"或"开始一个功能"
- 用户说"继续 SDD 流程"（从上次中断恢复）

## 前置依赖
- [ ] 项目 AGENTS.md 存在且含 flow_engine 字段
- [ ] sdd-structure-lint 项目级检查通过
- [ ] 当前目录可写入

## 执行流程

### Step 1: 项目级合规检查
调用 `skill_view('sdd/sdd-structure-lint')` 执行项目级检查。
失败 → 输出缺失项列表并终止，提示"请运行项目初始化"。

### Step 2: 变更目录准备
1. 用 `search_files(target='files', path='{changes_dir}', pattern='*')` 列出变更目录
2. 从目录名中提取最大 NNN，自动递增（如 001 → 002）
3. 新 change-id = `{NNN}-{short-name}`，short-name 从用户输入提取（或用 clarify 询问）
4. 用 `terminal(mkdir -p {changes_dir}/{change-id})` 创建目录
5. 写入 `.sdd-phase` 文件，内容为 `init`

### Step 3: 流程级别判定
读取 `skill_view('sdd/shared', file_path='flow-level-rules.md')`
执行判定：
  - 任务是否为 bug 修复？预计 ≤ 2h？无 DB 变更？→ Quick
  - 涉及 DB schema 变更或跨模块重构？→ Enhanced
  - 其他 → Standard

判定结果写入变更目录下的 `.sdd-flow-level` 文件。

### Step 4: 阶段调度循环
按阶段列表顺序执行。每个阶段：
  1. 更新 `.sdd-phase` 为当前阶段名
  2. 根据阶段名调度对应角色 Skill（用 skill_view）
  3. 角色执行完毕后，调用 sdd-structure-lint（交接级）
  4. lint 通过 → 进入下一阶段
  5. lint 失败 → 阻断，输出缺失项

阶段列表（Quick 跳过中间阶段，Enhanced 增加额外步骤）：

| 顺序 | 阶段 | 角色 Skill | Quick? | Enhanced 差异 |
|:---:|------|-----------|:---:|------|
| 1 | prd | po-agent | ✓ | — |
| 2 | spec | ba-agent | 跳过 | 强制 run spec-linter |
| 3 | design | architect-agent | 跳过 | 强制 Brainstorming ≥ 3 方案 |
| 4 | tasks | architect-agent | 跳过 | 每个 Task ≤ 4h |
| 5 | implement | coder-agent | ✓ | 每个 Task 完成后输出 Report |
| 6 | review | reviewer-agent | 跳过 | Phase 2 增加人工审查 |
| 7 | qa | qa-agent | ✓ | — |
| 8 | accept | clarify（用户确认） | ✓ | — |
| 9 | archive | 编排器自身 | ✓ | — |

### Step 5: 门禁处理

#### PRD 确认（prd 阶段后）
1. 读取 prd.md 内容
2. `clarify("PRD 是否确认？", choices=["确认，进入 Spec", "需要修改"])`
3. 用户拒绝 → 输出拒绝原因 → 返回 po-agent 修改

#### Spec 确认（spec 阶段后）
1. 读取 spec.md 内容
2. `clarify("Spec 是否确认？", choices=["确认，进入 Design", "需要修改"])`
3. 用户拒绝 → 输出拒绝原因 → 返回 ba-agent 修改

#### QA 熔断
1. qa-agent 返回"失败"时，记录失败轮次
2. 轮次 ≤ 4 → 返回 coder-agent（仅失败对应的 Task）
3. 轮次 = 5 → 触发熔断：
   - 汇总 5 轮失败摘要（每轮的失败用例列表）
   - `clarify("QA 已连续 5 轮失败，流程熔断。", choices=["继续修复", "回退到 Design", "放弃变更"])`
4. 用户选择"继续修复" → 重置轮次计数，返回 coder-agent
5. 用户选择其他 → 按选项目执行

#### 人工验收
1. 输出变更摘要（AC 覆盖、测试通过数、E2E 结果）
2. `clarify("人工验收：场景实现是否正确？", choices=["通过，归档", "需求偏差→回退PRD", "设计缺陷→回退Design", "代码Bug→回退Implement"])`
3. 打回时：
    - 需求偏差：删除 spec.md + design.md + tasks.md + 代码变更，`.sdd-phase` 写入 `prd`，返回 po-agent
    - 设计缺陷：删除 design.md + tasks.md + 代码变更，`.sdd-phase` 写入 `design`，返回 architect-agent
    - 代码 Bug：删除对应 Task 的代码变更，`.sdd-phase` 写入 `implement`，返回 coder-agent（仅该 Task）

#### 归档
1. 检查 CI 状态（如果项目有 CI，查询最后一次 workflow run）
2. CI 不绿 → 输出失败项，拒绝归档
3. CI 全绿 → 执行：
   - `terminal(mv {changes_dir}/{change-id} {archive_dir}/{change-id})`
   - 复制 prd.md、spec.md、design.md 到 `{current_dir}/`
   - 删除 `.sdd-phase` 和 `.sdd-flow-level`
   - 输出："归档完成。{change-id} 已移至 archive/，current/ 已更新。"

### Step 6: 中断恢复
编排器启动时检测 `{changes_dir}/` 下是否有 `.sdd-phase` 文件：
  - 存在 → 读取当前阶段，从中断处继续
  - 不存在但目录下有产物文件 → 通过文件存在性推导阶段：
    - 有 prd.md 无 spec.md → prd 阶段待交接
    - 有 spec.md 无 design.md → spec 阶段待交接
    - ...
  - 无产物文件 → 询问用户是否开始新变更

## 产出物
编排器自身不产出业务文档，管理以下文件：
- {changes_dir}/{change-id}/.sdd-phase
- {changes_dir}/{change-id}/.sdd-flow-level

## 被禁用行为
- ❌ 不能跳过用户确认门禁（PRD 和 Spec）
- ❌ 不能在没有合规检查的情况下进入下一阶段
- ❌ 不能在 CI 不绿时归档
- ❌ 不能修改角色 Agent 的产出物

## 退出条件
- 变更已归档（archive/ 下有该 change-id，current/ 已更新）
- 或用户主动放弃变更
```

---

### 2.2 sdd-init（项目初始化与升级）

**文件**：`sdd/sdd-init/SKILL.md`

**Frontmatter**：
```yaml
name: sdd-init
description: >
  初始化或升级项目的 SDD 框架。新项目交互式搭建骨架。
  存量项目分析→计划→确认→迁移。
category: sdd
version: 1.0.0
```

**核心指令**：

```markdown
# SDD Init

## 触发条件
- 用户说"初始化 SDD" 或 "接入 SDD" 或 "sdd init"
- sdd-orchestrator 检测到项目缺少 AGENTS.md 或 flow_engine 字段

## 前置依赖
- [ ] 当前工作目录可写入
- [ ] （可选）项目已有 git 仓库

## 执行流程

### 模式判定
1. 用 `read_file('AGENTS.md')` 尝试读取
2. 文件不存在 → **新项目模式**（跳至"A"）
3. 文件存在但内容不包含 `flow_engine` → **升级模式**（跳至"B"）
4. 文件存在且含 `flow_engine` → 已就绪，输出"项目已处于 SDD 就绪状态"，终止

### A. 新项目模式

#### Step A1: 交互询问
使用 `clarify()` 逐一询问：

1. 项目名称？
   ```
   clarify("项目名称？", choices=[])
   ```
   用户自由输入。赋值给 `project_name`。

2. 一句话描述？
   ```
   clarify("一句话描述项目？")
   ```
   用户自由输入。赋值给 `description`。

3. 后端技术栈？
   ```
   clarify("后端技术栈？", choices=["FastAPI (Python)", "Go", "Spring Boot (Java)", "无后端"])
   ```
   赋值给 `backend`。

4. 前端技术栈？
   ```
   clarify("前端技术栈？", choices=["React", "Vue", "无前端"])
   ```
   赋值给 `frontend`。

5. 数据库？
   ```
   clarify("数据库？", choices=["SQLite(dev)/PostgreSQL(prod)", "PostgreSQL only", "MongoDB"])
   ```
   赋值给 `database`。

6. 默认流程级别？
   ```
   clarify("默认流程级别？", choices=["Quick（快速迭代，跳过文档）", "Standard（标准流程，适合多数场景）", "Enhanced（严格流程，适合核心功能）"])
   ```
   赋值给 `flow_level`。

#### Step A2: 生成文件

用 `write_file()` 依次生成。路径为当前工作目录的相对路径。

**文件 1: AGENTS.md**

模板：
```markdown
# AGENTS.md — {project_name}

## 项目信息
- name: "{project_name}"
- description: "{description}"

## 技术栈
- backend: {backend}
- frontend: {frontend}
- database: {database}

## 路径约定
- changes_dir: "docs/changes/"
- current_dir: "docs/current/"
- archive_dir: "docs/archive/"

## SDD 配置
- flow_engine: "sdd/sdd-orchestrator"
- default_flow_level: "{flow_level}"

## 项目约束
- constitution: "CONSTITUTION.md"
- quirks: "QUIRKS.md"
```

**文件 2: CONSTITUTION.md**

模板（通用版，项目可后续自定义）：
```markdown
# CONSTITUTION.md — {project_name}

## 1. 代码规范
- 使用 {backend} 标准代码风格
- 所有公开函数必须有文档注释

## 2. 测试要求
- 新功能必须包含测试
- 测试应在 CI 中自动运行

## 3. 安全性
- 不在代码中硬编码密钥
- 用户输入必须校验

## 4. SDD 流程
- 新功能按 SDD 流程开发
- PRD 和 Spec 产出后必须经负责人确认

## 5. 版本管理
- 使用 Git 进行版本控制
- Commit message 遵循约定式提交格式
```

**文件 3: QUIRKS.md**

模板（空骨架，项目在实践中填充）：
```markdown
# QUIRKS.md — {project_name} 已知陷阱

## 占位
项目初始阶段，陷阱将在实践中逐步积累。

### 添加陷阱的格式
\`\`\`
## YYYY-MM-DD: 简短描述
- **现象**：发生了什么
- **根因**：为什么发生
- **修复**：如何解决
- **预防**：如何避免再犯
\`\`\`
```

#### Step A3: 创建目录
```bash
mkdir -p docs/changes
mkdir -p docs/current
mkdir -p docs/archive
```

#### Step A4: 合规验证
调用 `skill_view('sdd/sdd-structure-lint')` 执行项目级检查。
通过 → 输出"✅ SDD 就绪。你可以开始第一个变更了。"
失败 → 输出缺失项（理论上不应失败，刚生成的文件）

### B. 升级模式

#### Step B1: 分析现有状态

1. 读取现有 AGENTS.md → 提取已声明的字段，保存到 `existing_config`
2. 用 `search_files(target='files', pattern='*.md', path='.')` 扫描项目中的 Markdown 文件
3. 识别文档类型（PRD / Spec / Design）→ 通过文件名和内容关键词判断
4. 用 `terminal('git status --porcelain')` 获取本地修改的文件列表
5. 用 `search_files(target='files', pattern='.github/workflows/*.yml', path='.')` 检查 CI 配置
6. 用 `search_files(target='files', pattern='.pre-commit-config.yaml', path='.')` 检查 pre-commit 配置

#### Step B2: 生成升级计划

输出一个 Markdown 格式的升级计划，包含：

```markdown
# SDD 升级计划 — {project_name}

## 📁 新建文件
- CONSTITUTION.md（从模板生成）
- QUIRKS.md（空模板）
- docs/changes/（目录）
- docs/current/（目录）
- docs/archive/（目录）

## 📦 移动文件
- {散落文档路径} → {约定路径}

## ✏️ 修改文件
- AGENTS.md：增加 flow_engine、changes_dir 等字段

## ⚠️ 冲突项（需人工决策）
- {冲突文件列表及原因}

## 不变文件
- {不受影响的文件列表}
```

判定逻辑：
- 如果文档文件名包含"PRD"或内容包含"背景"+"目标"章节 → 建议移动到 `docs/current/prd.md`
- 如果文档文件名包含"Spec"或内容包含 Given-When-Then → 建议移动到 `docs/current/spec.md`
- 如果文档文件名包含"Design"或"设计" → 建议移动到 `docs/current/design.md`
- 如果文档在 git modified 列表中 → 标记为冲突项

#### Step B3: 用户确认
`clarify("以上升级计划是否确认执行？", choices=["确认执行", "仅生成计划文件（不执行）", "取消升级"])`

用户选"仅生成计划" → 将计划写入 `docs/sdd-upgrade-plan.md`，终止
用户选"取消" → 终止

#### Step B4: 执行迁移

按计划逐项执行：

1. **新建文件**：用 `write_file()` 创建 CONSTITUTION.md、QUIRKS.md
2. **移动文件**：对非冲突的文档，用 `terminal('git mv {源路径} {目标路径}')`
3. **修改 AGENTS.md**：在文件末尾追加 SDD 配置字段（不覆盖现有内容）
4. **创建目录**：`terminal('mkdir -p docs/changes docs/current docs/archive')`

#### Step B5: 合规验证
调用 `skill_view('sdd/sdd-structure-lint')` 执行项目级检查。
输出结果。

## 被禁用行为
- ❌ 不能删除任何现有文件
- ❌ 不能覆盖 git modified 的文件
- ❌ 存量升级必须在用户确认后才执行
- ❌ 不能修改 AGENTS.md 中已存在的用户自定义字段

## 退出条件
- sdd-structure-lint 项目级检查通过
- 或在升级模式中用户取消操作
```

---

### 2.3 sdd-structure-lint（合规验证）

**文件**：`sdd/sdd-structure-lint/SKILL.md`

**Frontmatter**：
```yaml
name: sdd-structure-lint
description: >
  验证 SDD 目录结构和产物完整性。
  三级检查：项目级 / 变更级 / 交接级。
category: sdd
version: 1.0.0
```

**核心指令**：

```markdown
# SDD Structure Lint

## 触发条件
- 编排器启动时（项目级检查）
- 每次阶段交接前（变更级 + 交接级检查）
- sdd-init 完成后（项目级检查）

## 前置依赖
- [ ] AGENTS.md 存在且可解析
- [ ] 可从 AGENTS.md 提取 changes_dir、current_dir、archive_dir

## 配置读取
从 AGENTS.md 解析以下字段（解析规则见 §三）：
  - changes_dir
  - current_dir
  - archive_dir
  - constitution（可选，默认 "CONSTITUTION.md"）
  - quirks（可选，默认 "QUIRKS.md"）

## 执行流程

### Level 1: 项目级检查

检查清单：

| # | 检查项 | 验证方式 | 失败输出 |
|---|--------|---------|---------|
| 1 | AGENTS.md 存在 | `read_file('AGENTS.md')` 不报错 | "缺失文件：AGENTS.md" |
| 2 | AGENTS.md 含 flow_engine | 文件内容包含 "flow_engine" | "AGENTS.md 中未声明 flow_engine 字段" |
| 3 | constitution 文件存在 | `read_file('{constitution}')` | "缺失文件：{constitution}" |
| 4 | {changes_dir} 目录存在 | `search_files(target='files', path='{changes_dir}')` | "缺失目录：{changes_dir}" |
| 5 | {current_dir} 目录存在 | `search_files(target='files', path='{current_dir}')` | "缺失目录：{current_dir}" |
| 6 | {archive_dir} 目录存在 | `search_files(target='files', path='{archive_dir}')` | "缺失目录：{archive_dir}" |

执行方式：
```
errors = []
for each check:
    try execute → catch error → append to errors
if errors:
    print "项目级检查失败："
    print each error on separate line
    return FAIL
else:
    print "项目级检查通过"
    return PASS
```

### Level 2: 变更级检查

检查当前活跃变更目录（{changes_dir}/{change-id}/）的合规性。

判定当前 change-id：
1. 读取 `.sdd-phase` 文件 → 获取当前阶段
2. 无 `.sdd-phase` → 列出 `{changes_dir}/` 下所有目录，选最近修改的
3. 无变更目录 → 跳过（项目刚初始化，尚无变更）

检查清单：

| # | 检查项 | 验证方式 | 失败输出 |
|---|--------|---------|---------|
| 1 | change-id 格式符合 NNN-short-name | 正则：`^\d{3}-[a-z][a-z0-9-]*$` | "change-id 格式错误：{id}。正确格式：NNN-short-name（如 001-add-login）" |
| 2 | 目录存在 | 目录路径可访问 | "变更目录不存在：{path}" |

### Level 3: 交接级检查

检查当前阶段的前置产物是否完整。根据 `.sdd-phase` 的内容判断：

| 当前阶段 | 必须存在的产物文件 |
|---------|-------------------|
| spec | prd.md |
| design | prd.md, spec.md |
| tasks | prd.md, spec.md, design.md |
| implement | prd.md, spec.md, design.md, tasks.md |
| review | prd.md, spec.md, design.md, tasks.md + 代码 diff 存在 |
| qa | prd.md, spec.md, design.md, tasks.md + 代码 diff 存在 + 评审报告存在 |
| accept | prd.md, spec.md, design.md, tasks.md + 代码 diff + 评审报告 + qa-report.md |
| archive | 全部产物 + CI 绿色 |

额外检查：每个必须存在的产物文件大小 > 0（非空壳）

执行方式：
```
for each required file:
    if not exists:
        errors.append("前置产物缺失：{filename}")
    elif file_size == 0:
        errors.append("产物为空：{filename}")
if errors:
    print "交接级检查失败："
    print each error
    return FAIL
else:
    print "交接级检查通过"
    return PASS
```

## 被禁用行为
- ❌ 不能修改任何文件（只读检查）
- ❌ 不能在检查失败时继续推进流程

## 退出条件
- 所有适用级别的检查均已执行并输出结果
```

---

### 2.4 po-agent（PO Agent）

**文件**：`sdd/po-agent/SKILL.md`

**Frontmatter**：
```yaml
name: po-agent
description: >
  PO Agent — 产出 PRD。Why + What + 用户故事 + 成功指标。
  不包含任何技术方案。
category: sdd
version: 1.0.0
load_before: []
```

**核心指令**：

```markdown
# PO Agent

## 触发条件
- 编排器在 prd 阶段调用 `skill_view('sdd/po-agent')`

## 前置依赖
编排器应在调用前确保：
- [ ] 项目 AGENTS.md 和 CONSTITUTION.md 已读取（编排器传入上下文）
- [ ] change-id 已确定，目录已创建
- [ ] .sdd-phase 为 "prd"

## 执行流程

### Step 1: 读取上下文
始终加载：编排器传入的用户需求描述和项目上下文
按需加载：`skill_view('sdd/po-agent', file_path='references/prd-template.md')`

### Step 2: 理解需求
1. 分析用户需求中的核心问题或机会
2. 识别目标用户角色
3. 如果有不明确的地方，使用 `clarify()` 向用户确认（不超过 3 个问题）

### Step 3: 撰写 PRD
按 prd-template.md 的结构填充内容：
1. **背景**：用 2-3 句话描述现状和问题。**禁止**写"方案已设计"或任何已完成状态的断言——PRD 是需求的起点。
2. **目标**：1-3 条可量化的目标
3. **目标用户**：表格列出所有用户角色及其核心诉求
4. **核心功能点**：F1、F2... 每个功能点 1-2 句话描述做什么，加 2-3 个要点
5. **不做的事**：明确排除的内容，防止范围蔓延
6. **成功指标**：表格，每行含指标名、目标值、衡量方式

### Step 4: 写入文件
路径：`{changes_dir}/{change-id}/prd.md`
格式：Markdown，含 YAML 头部（版本、日期、作者、流程级别）

### Step 5: 自检
写入后立即读取文件，确认：
- [ ] 所有章节标题都存在
- [ ] 核心功能点 ≥ 1 个
- [ ] 成功指标 ≥ 2 项
- [ ] 不含"已完成""已设计""方案已定"等完成时态断言
- [ ] 不含技术实现词汇（API、数据库、Redis、Pydantic 等）

## 产出物
| 文件 | 路径 | 说明 |
|------|------|------|
| prd.md | {changes_dir}/{change-id}/prd.md | PRD 文档（Why + What） |

## 被禁用行为
- ❌ 不能写任何技术方案、API 路径、数据库表设计
- ❌ 不能写"已完成""已确定"等完成时态断言（PRD 是需求起点）
- ❌ 不能跳过 clarify（如果需求不明确）

## 退出条件
- prd.md 已写入并通过自检
```

**references/prd-template.md**：

从 AILP 项目的 `docs/templates/prd-template.md` 复制，章节结构：
1. 背景
2. 目标
3. 目标用户（表格）
4. 核心功能点（F1/F2...）
5. 不做的事
6. 成功指标（表格）

---

### 2.5 ba-agent（BA Agent）

**文件**：`sdd/ba-agent/SKILL.md`

**Frontmatter**：
```yaml
name: ba-agent
description: >
  BA Agent — 产出 Spec。Given-When-Then AC + 业务规则 + 错误文案。
  纯行为契约，不包含任何技术实现。
category: sdd
version: 1.0.0
load_before: ["sdd/po-agent"]
```

**核心指令**：

```markdown
# BA Agent

## 触发条件
- 编排器在 spec 阶段调用 `skill_view('sdd/ba-agent')`

## 前置依赖
编排器应在调用前确保：
- [ ] prd.md 已存在且经用户确认
- [ ] .sdd-phase 为 "spec"

## 执行流程

### Step 1: 读取上下文
始终加载：prd.md（编排器传入路径）
按需加载：`skill_view('sdd/ba-agent', file_path='references/spec-template.md')`
按需加载：`skill_view('sdd/ba-agent', file_path='references/ac-writing-guide.md')`

### Step 2: 分析 PRD
1. 提取核心功能点（F1-Fn）
2. 提取目标用户
3. 提取成功指标
4. 为每个功能点设计验收场景

### Step 3: 撰写验收场景（AC）
按 spec-template.md 结构，每个 AC 包含：
```markdown
### AC{N}: {场景名称}
- **Given** {前置条件：用户/数据/系统状态}
- **When** {触发操作，精确到动作}
- **Then** {预期行为，精确到系统输出}
```

覆盖原则：
- 每个功能点至少 1 条正常路径 AC
- 每个功能点至少 1 条异常路径 AC（错误输入、边界条件、权限不足）
- 每个功能点至少 1 条边界条件 AC（如空数据、最大值、重复操作）
- 合计 AC 数 ≥ 功能点数 × 2

### Step 4: 撰写业务规则（BR）
从 AC 中提取可复用的规则，格式：
```markdown
| BR{N} | {规则描述} | AC{x}, AC{y} |
```
规则必须是可验证的、无歧义的。

### Step 5: 撰写边界条件
列出所有系统需要处理的边界情况：
```markdown
| 边界 | 条件 | 预期行为 | 涉及场景 |
```

### Step 6: 撰写错误场景与用户提示文案
为每个异常 AC 设计用户可见的提示文字：
```markdown
| 错误场景 | 触发条件 | 用户看到的提示文案 |
```

### Step 7: 撰写非功能需求
从 PRD 的成功指标推导非功能需求：
```markdown
| 需求类型 | 要求 | 衡量方式 |
```

### Step 8: 写入文件
路径：`{changes_dir}/{change-id}/spec.md`
在文件顶部添加醒目的警告：
```
> ⚠️ 本文档只描述系统行为，不包含任何技术方案、API 路径、数据库表设计。
```

### Step 9: 自检
写入后立即读取文件，确认：
- [ ] AC 数量 ≥ PRD 功能点数 × 2
- [ ] 每条 AC 含 Given / When / Then
- [ ] 业务规则表非空
- [ ] 错误文案表非空
- [ ] 不含技术实现词汇（API、数据库、表名、框架名、Pydantic 等）
- [ ] 顶部警告存在

## 产出物
| 文件 | 路径 | 说明 |
|------|------|------|
| spec.md | {changes_dir}/{change-id}/spec.md | 行为契约 |

## 被禁用行为
- ❌ 不能写任何技术方案、API 路径、数据库表名
- ❌ 不能修改 PRD 中定义的功能范围
- ❌ 不能使用技术框架术语（FastAPI、React、SQLite 等）

## 退出条件
- spec.md 已写入并通过自检
```

**references/spec-template.md**：从 AILP 项目模板复制。
**references/ac-writing-guide.md**：AC 编写最佳实践：

```markdown
# AC 编写指南

## 格式
每条 AC 必须使用 Given-When-Then 格式。
Given = 前置条件（只描述状态，不描述过程）
When  = 触发动作（精确到具体操作）
Then  = 预期结果（精确到系统输出、提示文案、数据变化）

## 质量检查
- Given 中不出现"用户点击了"（那是 When）
- Then 中不出现"系统应该"（去掉模糊词）
- 每条 AC 覆盖一个独立场景
- AC 编号连续，AC1 为最核心场景
```

---

### 2.6 architect-agent（Architect Agent）

**文件**：`sdd/architect-agent/SKILL.md`

**Frontmatter**：
```yaml
name: architect-agent
description: >
  Architect Agent — 产出 Design + Tasks。
  Brainstorming 对比 ≥ 2 方案 → 推荐方案 → 技术设计 → 按业务场景拆分 Task。
category: sdd
version: 1.0.0
load_before: ["sdd/ba-agent"]
```

**核心指令**：

```markdown
# Architect Agent

## 触发条件
- 编排器在 design 阶段或 tasks 阶段调用 `skill_view('sdd/architect-agent')`

## 前置依赖
编排器应在调用前确保：
- [ ] spec.md 已存在且经用户确认
- [ ] 项目代码结构可访问（对于 Design 阶段）
- [ ] .sdd-phase 为 "design" 或 "tasks"

## 执行流程

### Phase 1: Design（当 .sdd-phase 为 "design"）

#### Step 1: 读取上下文
始终加载：spec.md + 项目 CONSTITUTION.md
按需加载：`skill_view('sdd/architect-agent', file_path='references/design-template.md')`
按需加载：`skill_view('sdd/architect-agent', file_path='references/brainstorming-guide.md')`

#### Step 2: Brainstorming
对每个关键决策点，探索 ≥ 2 种方案：
1. 从 spec.md 提取需要技术决策的点（如"数据存储方式""状态管理方式""Skill 组织方式"）
2. 对每个决策点，设计 ≥ 2 个方案
3. 每个方案描述：怎么做（1-3 句）、优点（≥ 2 条）、缺点/风险（≥ 1 条）
4. 标注每个方案是否与 CONSTITUTION.md 冲突

Enhanced 流程强制 ≥ 3 个方案。

#### Step 3: 推荐方案
明确推荐哪个方案，关键 trade-off 是什么。

#### Step 4: 系统架构
ASCII 图描述系统架构（Skills、工具、数据流）

#### Step 5: 详细设计
分节描述（具体内容取决于项目类型）：
- Skill 项目：每个 Skill 的详细结构（见 §二 的模板）
- Web 项目：接口定义、数据模型、技术选型、关键流程
- 通用：文件清单、目录结构、配置规范、错误处理

**详细程度原则**：Agent 只需参照 Design 文档即可实现，不需要额外询问。

#### Step 6: 写入 design.md
路径：`{changes_dir}/{change-id}/design.md`

### Phase 2: Tasks（当 .sdd-phase 为 "tasks"）

#### Step 7: Task 拆分
读取 design.md，按业务场景拆分 Task。

拆分原则（从 convention_overrides 读取，默认"按业务场景拆分"）：
- 每个 Task 对应一个可独立上线的业务场景
- **禁止按技术层次拆分**（如"数据库层→API层→前端层"）
- 每个 Task 包含：编号、名称、描述、估时、依赖关系、验收标准（引用 AC 编号）
- Task 按依赖排序

#### Step 8: 写入 tasks.md
路径：`{changes_dir}/{change-id}/tasks.md`

格式：
```markdown
# Tasks: {change-id}

| # | Task | 估时 | 依赖 | AC 覆盖 |
|---|------|:---:|------|:---:|
| T1 | {名称} | {h} | 无 | AC1, AC2 |
| T2 | {名称} | {h} | T1 | AC3, AC4 |

## T1: {名称}
- **描述**：...
- **验收标准**：...
- **产出文件**：...
```

## 产出物
| 文件 | 路径 | 触发条件 |
|------|------|---------|
| design.md | {changes_dir}/{change-id}/design.md | .sdd-phase = "design" |
| tasks.md | {changes_dir}/{change-id}/tasks.md | .sdd-phase = "tasks" |

## 被禁用行为
- ❌ 不能修改 spec.md 中的 AC 或业务规则
- ❌ 不能按技术层次拆分 Task
- ❌ 不能跳过 Brainstorming（至少 2 个方案）
- ❌ Design 不能模糊到 Agent 需要追问的程度

## 退出条件
- .sdd-phase = "design" 时：design.md 已写入
- .sdd-phase = "tasks" 时：tasks.md 已写入
```

**references/brainstorming-guide.md**：
```markdown
# Brainstorming 指南

## 何时需要 Brainstorming
- 涉及数据存储方式选择
- 涉及系统架构决策
- 涉及第三方库/框架选择
- 涉及并发、性能、扩展性决策

## 方案探索要求
- Standard 流程：≥ 2 个方案
- Enhanced 流程：≥ 3 个方案
- 每个方案必须有：优点 + 缺点/风险 + Constitution 合规检查
- 推荐方案必须给出明确理由

## 常见陷阱
- 不要只列一个方案（那不是 Brainstorming）
- 不要回避方案的缺点
- 不要忽略 Constitution 冲突
```

---

### 2.7 coder-agent（Coder Agent）

**文件**：`sdd/coder-agent/SKILL.md`

**Frontmatter**：
```yaml
name: coder-agent
description: >
  Coder Agent — TDD 实现。逐 Task 执行 RED→GREEN→REFACTOR。
  每个 Task 完成后输出 Task Completion Report。
category: sdd
version: 1.0.0
load_before: ["sdd/architect-agent"]
```

**核心指令**：

```markdown
# Coder Agent

## 触发条件
- 编排器在 implement 阶段调用 `skill_view('sdd/coder-agent')`
- QA 熔断后编排器调度修复（仅失败的 Task）

## 前置依赖
编排器应在调用前确保：
- [ ] tasks.md 已存在
- [ ] design.md 已存在
- [ ] spec.md 已存在
- [ ] .sdd-phase 为 "implement"
- [ ] 编排器传入当前 Task 编号（如 T1、T2）

## 执行流程

### Step 0: 读取上下文
始终加载：tasks.md（读取当前 Task 描述）
始终加载：design.md（读取技术方案）
始终加载：spec.md（读取对应的 AC）
按需加载：`skill_view('sdd/coder-agent', file_path='references/tdd-workflow.md')`
按需加载：`skill_view('sdd/coder-agent', file_path='references/nfr-checklist.md')`

### Step 1: 写测试（RED）
1. 根据当前 Task 的验收标准（引用 AC 编号），找到 spec.md 中对应的 AC
2. 编写测试用例，覆盖：
   - 正常路径（Happy Path）
   - 异常路径（错误输入、边界条件）
   - 当前 Task 不覆盖的 AC 除外
3. 运行测试 → 预期失败（RED）

### Step 2: 写实现（GREEN）
1. 按照 design.md 的技术方案实现功能
2. 运行测试 → 预期通过（GREEN）

### Step 3: 重构（REFACTOR）
1. 检查代码是否符合项目代码规范
2. 检查是否有重复代码、过长函数、不清晰的命名
3. 重构后重新运行测试 → 必须仍然通过

### Step 4: 回归测试
运行全量测试（不只是当前 Task 的测试）：
```bash
cd {backend_dir} && pytest tests/ -x -q
```
确保没有回归。

### Step 5: Task Completion Report
输出结构化报告：
```markdown
## Task {id}: {name} — 完成报告

- **状态**：完成
- **测试**：{passed}/{total} 通过
- **AC 覆盖**：AC{覆盖的 AC 编号列表}
- **NFR 检查**：
  - [x] 错误处理（有明确的错误提示）
  - [x] 输入校验（非法输入有校验）
  - [ ] 性能 / 埋点 / 审计（如 Task 不涉及则勾选 N/A）
- **新增/修改文件**：
  - {文件路径列表}
- **已知限制**：
  - {如果有，如实记录}
```

报告写入 `{changes_dir}/{change-id}/task-{id}-report.md`

### Step 6: 循环
编排器传入下一个 Task → 重复 Step 1-5
全部 Task 完成后 → 通知编排器

## 被禁用行为
- ❌ 不能跳过测试直接写实现
- ❌ 不能修改 spec.md 中的 AC 或业务规则
- ❌ 不能跨 Task 范围修改无关文件
- ❌ 不能 push 代码（编排器管理提交和 push）

## 退出条件
- 当前 Task 的 Completion Report 已生成
- 全量测试通过
```

---

### 2.8 reviewer-agent（Reviewer Agent）

**文件**：`sdd/reviewer-agent/SKILL.md`

**Frontmatter**：
```yaml
name: reviewer-agent
description: >
  Reviewer Agent — 三阶段评审。
  Phase 1 自动化 → Phase 2 独立审查 → Phase 3 回归验证。
category: sdd
version: 1.0.0
load_before: ["sdd/coder-agent"]
```

**核心指令**：从 AILP 的 `post-coding-review` skill 迁移，增加 format 检查。

```markdown
# Reviewer Agent

## 触发条件
- 编排器在 review 阶段调用 `skill_view('sdd/reviewer-agent')`

## 前置依赖
- [ ] 代码 diff 可获取（通过 git diff）
- [ ] spec.md + design.md + tasks.md 存在
- [ ] 所有 Task Completion Report 存在
- [ ] .sdd-phase 为 "review"

## 执行流程

### Phase 1: 自动化检查
1. **Format 检查**：
   - `terminal('black --check {backend_dir}/')`
   - `terminal('isort --check-only {backend_dir}/')`
   - `terminal('ruff check {backend_dir}/ --select=E,W,F')`
2. **测试检查**：运行全量测试
3. **git diff 审查**：检查变更范围是否与 tasks.md 一致（不应有多余文件）

Phase 1 失败项 → 标记为 WARNING，不阻断（修复由 Coder 在 Implement 阶段完成）

### Phase 2: 独立审查
对照以下文件逐项审查：
1. **对照 design.md**：实现是否符合技术方案？接口定义是否一致？
2. **对照 spec.md**：AC 是否全部覆盖？业务规则是否正确实现？
3. **对照 CONSTITUTION.md**：是否违反分层、测试、安全等规则？
4. **NFR 检查**：埋点、审计日志、性能是否按 design.md 要求实现？

按严重程度分级输出：

| 级别 | 定义 | 示例 |
|------|------|------|
| BLOCKER | 违反 Constitution 红线 | 没有测试、Schema 不是真相源 |
| CRITICAL | 缺失关键功能 | AC 未覆盖、design 要求的 NFR 缺失 |
| WARNING | 代码质量问题 | 缺少错误处理、边界条件未覆盖 |
| INFO | 改进建议 | 命名可优化、注释可补充 |

### Phase 3: 回归验证
1. 重新运行全量测试
2. 如果项目有 E2E，运行 E2E smoke
3. 确认 Phase 2 中发现的修复项已被处理

## 产出物
写入 `{changes_dir}/{change-id}/review-report.md`：
```markdown
# Review Report: {change-id}

## Phase 1: 自动化检查
- Format: {通过/失败项}
- 测试: {passed}/{total}
- Diff 范围: {一致/不一致}

## Phase 2: 独立审查
### BLOCKER
- {如果有}

### CRITICAL
- {如果有}

### WARNING
- {如果有}

### INFO
- {如果有}

## Phase 3: 回归验证
- {结果}

## 结论
- {通过 / 有条件通过 / 不通过}
```

## 被禁用行为
- ❌ 不能只检查代码风格，必须对照 Design 和 NFR
- ❌ 不能跳过 Phase 2（独立审查）
- ❌ 不能在发现 BLOCKER 时标记为"通过"

## 退出条件
- 评审报告已写入
```

---

### 2.9 qa-agent（QA Agent）

**文件**：`sdd/qa-agent/SKILL.md`

**Frontmatter**：
```yaml
name: qa-agent
description: >
  QA Agent — 触发 CI 执行测试 + AC 覆盖矩阵验证 + 环境差异标记。
category: sdd
version: 1.0.0
load_before: ["sdd/reviewer-agent"]
```

**核心指令**：

```markdown
# QA Agent

## 触发条件
- 编排器在 qa 阶段调用 `skill_view('sdd/qa-agent')`

## 前置依赖
- [ ] 代码已提交（git commit）
- [ ] spec.md 存在（用于 AC 覆盖验证）
- [ ] 评审报告存在（review-report.md）
- [ ] .sdd-phase 为 "qa"

## 执行流程

### Step 1: 触发 CI
1. 检查项目是否有 CI 配置（`.github/workflows/` 下是否有 yml 文件）
2. 有 CI：`terminal('git push origin {current-branch}')` 触发 CI
3. 无 CI：本地运行全量测试
   - `terminal('cd {backend_dir} && pytest tests/ -v')`
   - `terminal('npx playwright test')`（如有 E2E）

### Step 2: 等待 CI 结果（如有 CI）
轮询 CI 状态（参考 `cronjob` 或 GitHub API），直到 completed。
获取测试通过/失败/跳过计数。

### Step 3: AC 覆盖验证
1. 读取 spec.md，提取所有 AC 编号（AC1 ~ AC{N}）
2. 读取所有测试文件（单元测试 + 集成测试 + E2E），搜索每个 AC 编号的引用
3. 生成覆盖矩阵：

```markdown
| AC | 单元测试 | 集成测试 | E2E | 状态 |
|:--:|---------|---------|-----|:---:|
| AC1 | test_xxx.py::test_yyy | test_zzz.py::test_www | spec.js L45 | ✅ |
| AC2 | — | test_zzz.py::test_vvv | spec.js L78 | ✅ |
| AC3 | — | — | — | ❌ 缺失 |
```

4. 未覆盖的 AC → 标记为失败

### Step 4: 环境差异标记
检查是否有仅在特定环境下才能运行的测试：
1. 搜索测试文件中的 `skipif`、`skip`、`xfail` 标记
2. 记录每个跳过测试的原因（如 SQLite 限制、Docker 不可用）
3. 汇总到报告中

### Step 5: 生成 QA 报告
写入 `{changes_dir}/{change-id}/qa-report.md`：

```markdown
# QA Report: {change-id}

## 测试结果
- 单元测试：{passed}/{total}
- 集成测试：{passed}/{total}
- E2E 测试：{passed}/{total}（{skipped} skipped）

## AC 覆盖矩阵
{Step 3 的表格}

## 环境差异
| 测试 | 跳过原因 | 建议 |
|------|---------|------|

## 失败详情
{如果有失败，列出每个失败的测试名和错误摘要}

## 结论
- {通过 / 有条件通过 / 不通过}
```

## 被禁用行为
- ❌ 不能只检查单元测试，必须包含集成测试和 E2E
- ❌ 不能在没有 AC 覆盖验证的情况下输出"通过"
- ❌ 不能忽略环境差异（必须标记）

## 退出条件
- qa-report.md 已写入
- 返回结果给编排器：pass / fail（含失败详情）
```

**references/circuit-breaker.md**：

```markdown
# QA 熔断机制

## 规则
- QA 失败时，编排器自动返回 Coder Agent 修复
- 单轮修复范围：仅失败的 Task，不重跑全部
- 第 1-4 轮：自动修复循环
- 第 5 轮：触发熔断

## 熔断时输出
编排器应向用户展示：

\`\`\`
QA 已连续 5 轮失败，流程熔断。

失败摘要：
  第 1 轮：AC3 测试失败 — "expected 201, got 400"
  第 2 轮：AC3 测试失败 — "expected 201, got 500"
  第 3 轮：AC3、AC7 测试失败 — ...
  ...

请决定：
  A) 继续修复（重置计数）
  B) 回退到 Design 阶段
  C) 放弃此变更
\`\`\`
```

---

### 2.10 shared/ 共享文件

#### shared/handoff-protocol.md

```markdown
# SDD 角色交接协议

## 交棒方职责
1. 确保产出物已写入约定路径
2. 执行自检（如角色 Skill 中定义的检查清单）
3. 通知编排器当前阶段完成

## 接棒方职责
1. 读取上游产物（按角色 Skill 中定义的前置依赖）
2. 执行合规检查（编排器自动调用 sdd-structure-lint）

## 交接数据包
交接时编排器向接棒方传入：
- change-id
- 上游产物文件路径列表
- 项目 AGENTS.md 配置（路径约定等）
- 当前 Task 编号（仅 Implement 阶段）
```

#### shared/flow-level-rules.md

```markdown
# 流程级别判定规则

## Quick
条件（全部满足）：
- 预计工作量 ≤ 2 小时
- 不涉及数据库 schema 变更
- 不涉及新增 API 端点
- 不涉及跨模块重构
- 属于 bug 修复或小功能增强

跳过阶段：Spec、Design、Review

## Standard（默认）
条件（以下任一）：
- 预计工作量 2-20 小时
- 涉及新增 API 端点
- 涉及新增页面或组件

执行全部阶段，无额外要求

## Enhanced
条件（以下任一）：
- 涉及数据库 schema 变更
- 涉及跨模块重构
- 涉及安全相关功能
- 涉及性能关键路径
- 涉及第三方服务集成

额外要求：
- Design 阶段 Brainstorming ≥ 3 方案
- Review 阶段 Phase 2 增加人工审查
- 每个 Task ≤ 4 小时
```

#### shared/convention-overrides.md

```markdown
# 可覆盖约定清单

以下约定可由项目 AGENTS.md 的 convention_overrides 覆盖。

| 键 | 默认值 | 说明 | 影响范围 |
|----|--------|------|---------|
| tasks_split_rule | "按业务场景拆分" | Task 拆分策略 | architect-agent |
| change_id_format | "NNN-short-name" | 变更目录命名格式 | 编排器 + sdd-structure-lint |
| require_spec_lint | true | Spec 产出后是否强制 linter | ba-agent |
| auto_archive | false | 验收通过后自动归档 | 编排器 |
| skip_phases_for_quick | ["spec", "design", "review"] | Quick 跳过的阶段 | 编排器 |

## 覆盖示例
在 AGENTS.md 中：
\`\`\`markdown
## 自定义覆盖
- convention_overrides:
    tasks_split_rule: "按模块拆分"
    auto_archive: true
\`\`\`
```

---

## 三、Rules 设计

### 3.1 规则存储

全部规则存储在 `sdd/shared/sdd-rules.md`，每个项目通过 AGENTS.md 的 `constitution` 引用项目级规则（CONSTITUTION.md），通用 SDD 规则从此文件加载。

**文件**：`sdd/shared/sdd-rules.md`

### 3.2 规则定义

每条规则包含：编号、名称、描述、触发时机、执行者、违反处理。

#### R1: 没有 Spec 不写代码

```
编号: R1
描述: 新功能必须先产出 Spec（Quick 流程除外），无 Spec 不可进入 Implement 阶段
触发时机: 编排器在 implement 阶段启动前
执行者: sdd-orchestrator
检查方式: sdd-structure-lint 交接级检查 — spec.md 是否存在
违反处理: 阻断流程，输出 "无法进入 Implement：spec.md 不存在。请先完成 Spec 阶段。"
Quick 豁免: ✓（Quick 跳过 Spec 阶段）
```

#### R2: 编码前 Brainstorming

```
编号: R2
描述: Standard/Enhanced 流程的 Design 阶段必须执行 Brainstorming（≥2 方案对比）
触发时机: architect-agent 在 design 阶段启动时
执行者: architect-agent
检查方式: 自检 — design.md 中是否包含方案 A、方案 B 两个章节
违反处理: architect-agent 自动返回 Step 2 补充方案对比
Quick 豁免: ✓（Quick 跳过 Design 阶段）
```

#### R3: TDD 强制

```
编号: R3
描述: 代码实现必须先写测试（RED），后写实现（GREEN），最后重构（REFACTOR）
触发时机: coder-agent 每个 Task 执行时
执行者: coder-agent
检查方式: 自检 — 运行测试必须先是 RED（失败），然后 GREEN（通过）
违反处理: coder-agent 退回 Step 1，不允许跳过测试
Quick 豁免: ✗（Quick 也必须 TDD）
```

#### R4: 编码后必须评审

```
编号: R4
描述: Implement 完成后必须经 Reviewer Agent 三阶段评审
触发时机: 编排器在 implement 阶段后
执行者: sdd-orchestrator → reviewer-agent
检查方式: review-report.md 是否存在且结论为"通过"或"有条件通过"
违反处理: 阻断流程，输出 "无法进入 QA：评审未完成。"
Quick 豁免: ✓（Quick 跳过 Review 阶段）
```

#### R5: 前后端契约同步

```
编号: R5
描述: 后端 Schema 字段名必须与前端消费字段名一致；修改 Schema 需同步更新前端引用
触发时机: reviewer-agent Phase 2 审查
执行者: reviewer-agent
检查方式: 检查 diff 中 Schema 变更是否伴随前端对应字段更新
违反处理: 标记为 CRITICAL，返回 coder-agent 修复
项目豁免: 无前端的项目在 AGENTS.md 的 convention_overrides 中声明
    - convention_overrides:
        disable_rules: ["R5"]
```

#### R6: 测试自包含原则

```
编号: R6
描述: 所有测试必须在全新环境中独立运行（在各自声明的目标环境中），不依赖预置数据
触发时机: QA Agent AC 覆盖验证时
执行者: qa-agent
检查方式: 检查测试是否能在 CI 新环境中通过。CI-only 标记的测试仅需在 CI 中通过；本地可运行的测试需在本地也通过（见 R9）
违反处理: 标记为环境依赖，在 qa-report.md 的环境差异中记录
```

#### R7: E2E-AC 一一对应

```
编号: R7
描述: 每个 E2E 用例必须标注对应的 AC 编号；QA 阶段验证完整覆盖
触发时机: QA Agent AC 覆盖验证
执行者: qa-agent
检查方式: 提取 spec.md 所有 AC 编号，在 E2E 文件中搜索引用，生成覆盖矩阵
违反处理: 缺失覆盖的 AC 标记为失败，QA 报告结论为"不通过"
```

#### R8: Push 前必过 Pre-commit

```
编号: R8
描述: 代码 push 到远程前必须通过本地 pre-commit 检查（format + lint）
触发时机: git push 时（由 pre-commit hook 自动触发）
执行者: pre-commit hook
检查方式: black --check + isort --check-only + ruff check（仅变更文件）
违反处理: push 被阻断，输出具体失败项
配置: 由 sdd-init 生成 .pre-commit-config.yaml
```

#### R9: 目标环境通过原则

```
编号: R9
描述: 测试必须在声明的目标环境中通过，不强制所有测试本地+CI 双通。
      - 本地可运行的测试：需在本地和 CI 双环境通过
      - 需要 CI 资源（Docker/GPU/大内存/长超时）的复杂测试：标记为 CI-only，仅需 CI 通过
触发时机: QA Agent 环境差异标记
执行者: qa-agent
检查方式: (1) 搜索测试文件中的 CI-only 标记（pytest skipif/skip 或自定义 marker），记录跳过原因；
          (2) 非 CI-only 的测试在本地也需执行并通过
违反处理: (1) CI-only 测试未标记 → 标记为 REQ，要求补充标记及原因注释；
          (2) 非 CI-only 测试本地未通过 → 标记为 FAIL
配置: sdd-init 生成 pytest.ini 时自动注册 ci_only marker，本地默认 skip
```

#### R10: PR 不直接 push main

```
编号: R10
描述: 涉及 .github/workflows/ 或新增功能的变更，必须走 PR 流程
触发时机: 编排器归档前
执行者: sdd-orchestrator
检查方式: 检查变更是否包含 .github/workflows/ 文件变更
违反处理: 输出 "此变更涉及 CI 配置，请通过 PR 提交。"
```

### 3.3 规则加载流程

```
编排器启动
  → 读取 AGENTS.md → 提取 convention_overrides.disable_rules（如有）
  → 加载 sdd/shared/sdd-rules.md → 过滤掉 disable_rules 中的规则
  → 在每个阶段检查对应规则
```

### 3.4 规则覆盖机制

项目可在 AGENTS.md 中声明：

```markdown
## 自定义覆盖
- convention_overrides:
    disable_rules: ["R5"]          # 无前端项目禁用前后端契约检查
    custom_rules:                  # 项目特有规则
      - id: "R11"
        name: "禁止使用 any 类型"
        trigger: "reviewer-agent Phase 2"
        check: "grep -r ': any' {backend_dir}/"
```

自定义规则的 enforce 方式与内置规则相同，编排器在对应时机检查。

---

## 四、Hooks 设计

### 4.1 Hooks 清单

| Hook | 触发时机 | 执行内容 | 失败行为 | 生成方式 |
|------|---------|---------|---------|---------|
| **pre-commit** | `git commit` | black --check + isort --check-only + ruff check（仅变更文件） | 阻断 commit | sdd-init 生成 `.pre-commit-config.yaml` |
| **pre-push** | `git push` | 全量 pytest（快速模式：-x -q，CI-only 测试自动跳过） | 阻断 push | sdd-init 生成 `.pre-commit-config.yaml` 中的 pre-push stage；配合 `pytest.ini` + `conftest.py` 的 ci_only marker |
| **post-commit** | commit 成功后 | 检测本次是否修复了 QUIRKS.md 中的一个陷阱 → 提示更新 QUIRKS.md | 不阻断（仅提示） | sdd-init 生成 `.git/hooks/post-commit` 脚本 |
| **CI post-merge** | merge 到 main 后 | 自动将 changes/{id} 移至 archive/{id}，更新 current/ | CI 步骤失败但 merge 不回滚 | CI workflow 模板，后续变更实现 |

### 4.2 pre-commit Hook 详细设计

**文件**：`.pre-commit-config.yaml`（项目根目录）

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
        args: [--check]
        stages: [commit]

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--check-only]
        stages: [commit]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.1
    hooks:
      - id: ruff
        args: [--select, E, W, F]
        stages: [commit]

  - repo: local
    hooks:
      - id: pytest-fast
        name: pytest (fast)
        entry: bash -c 'cd backend && pytest tests/ -x -q'
        language: system
        pass_filenames: false
        stages: [push]
```

**sdd-init 生成逻辑**：

```
Step A2 中增加 Step A2.4: 生成 .pre-commit-config.yaml

1. 检查项目技术栈：
   - 如果是 Python 项目 → 生成如上配置
   - 如果是 Go 项目 → 生成 golangci-lint + gofmt 配置
   - 如果是前端项目 → 生成 eslint + prettier 配置
   - 如果是混合项目 → 合并各技术栈配置

2. 检查 pytest 目录：
   - backend/ 存在 → pre-push hook 路径为 'cd backend && pytest tests/ -x -q'
   - 无 backend/ → pre-push hook 路径为 'pytest tests/ -x -q'
   - 无 tests/ → 跳过 pre-push hook

3. 检查是否有 .pre-commit-config.yaml 已存在：
   - 存在 → 不覆盖，输出 "检测到现有 pre-commit 配置，已跳过"
```

### 4.2.1 pytest.ini 生成（CI-only marker 基础设施）

R9（目标环境通过原则）要求 CI-only 测试必须显式标记。sdd-init 自动生成 `pytest.ini` 注册 `ci_only` marker，本地默认 skip。

**文件**：`pytest.ini`（项目根目录，Python 项目）

```ini
[pytest]
markers =
    ci_only: 仅在 CI 环境中运行的测试（需要 Docker/GPU/大内存等资源）
```

**conftest.py 片段**（由 sdd-init 插入项目已有 conftest.py，或创建新文件）：

```python
# SDD: CI-only marker support — auto-skip locally, run only in CI
import os
import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "ci_only: tests that require CI environment resources"
    )


def pytest_collection_modifyitems(config, items):
    if os.environ.get("CI", "").lower() not in ("true", "1"):
        skip_ci_only = pytest.mark.skip(reason="CI-only test, skipped locally")
        for item in items:
            if "ci_only" in item.keywords:
                item.add_marker(skip_ci_only)
```

**sdd-init 生成逻辑**：

```
Step A2.4a: 生成 pytest.ini + conftest CI-only 支持

1. 检查项目类型：
   - Python 项目（有 setup.py/pyproject.toml/tests/）→ 继续
   - 非 Python 项目 → 跳过

2. 生成/更新 pytest.ini：
   - 已存在 → 检查是否已有 [markers] 段和 ci_only marker
     - 已有 ci_only → 跳过
     - 无 ci_only → 在 [markers] 段追加 "ci_only: ..."
     - 无 [markers] 段 → 追加 [pytest] 和 markers 配置
   - 不存在 → 创建完整文件

3. 生成/更新 conftest.py：
   - 已存在 → 在文件末尾追加 SDD CI-only 块（用 `# SDD: CI-only` 标记）
     - 如果标记块已存在 → 跳过
   - 不存在 → 创建新文件，内容为上述 conftest.py 片段
```

### 4.3 post-commit Hook 详细设计

**文件**：`.git/hooks/post-commit`（由 sdd-init 生成）

```bash
#!/bin/bash
# SDD post-commit hook — 检测陷阱修复并提示更新 QUIRKS.md

COMMIT_MSG=$(git log -1 --pretty=%B)
QUIRKS_FILE="QUIRKS.md"

# 检测 commit message 中是否包含 fix/修复 关键词
if echo "$COMMIT_MSG" | grep -qiE "fix|修复|bug"; then
    if [ -f "$QUIRKS_FILE" ]; then
        echo ""
        echo "⚠️  SDD: 检测到修复类 commit，请考虑是否需要在 QUIRKS.md 中记录："
        echo "   现象 → 根因 → 修复 → 预防"
        echo ""
    fi
fi
```

**sdd-init 生成逻辑**：

```
Step A2 中增加 Step A2.5: 生成 post-commit hook

1. 用 write_file('.git/hooks/post-commit', content) 写入上述脚本
2. terminal('chmod +x .git/hooks/post-commit')
3. 如果项目不在 git 仓库中（无 .git/），跳过此步骤
```

### 4.4 Hooks 集成到 sdd-init 流程

在 sdd-init 的 Step A2（生成文件）中，完整步骤调整为：

```
Step A2.1: 生成 AGENTS.md
Step A2.2: 生成 CONSTITUTION.md
Step A2.3: 生成 QUIRKS.md
Step A2.4: 生成 .pre-commit-config.yaml（含 pre-commit + pre-push hooks）
Step A2.4a: 生成 pytest.ini + conftest CI-only 支持（Python 项目）
Step A2.5: 生成 .git/hooks/post-commit（仅当 .git/ 存在）
Step A2.6: 创建目录（docs/changes/ docs/current/ docs/archive/）
```

### 4.5 存量项目升级时的 Hooks 处理

sdd-init 升级模式（Step B1）中增加检测：

```
Step B1 增加检测项：
  7. 检查 .pre-commit-config.yaml 是否已存在：
     - 存在 → 在升级计划中标记为 "不变文件"
     - 不存在 → 在升级计划中标记为 "📁 新建文件"
  8. 检查 .git/hooks/post-commit 是否已存在：
     - 存在且来源非 SDD → 在升级计划中标记为 "⚠️ 冲突项"
     - 不存在 → 在升级计划中标记为 "📁 新建文件"
  9. 检查 pytest.ini 是否已存在（Python 项目）：
     - 存在且已有 ci_only marker → 在升级计划中标记为 "不变文件"
     - 存在但无 ci_only → 在升级计划中标记为 "📝 需更新文件"
     - 不存在 → 在升级计划中标记为 "📁 新建文件"
 10. 检查 conftest.py 是否已有 SDD CI-only 块：
     - 已有 → 在升级计划中标记为 "不变文件"
     - 无 → 在升级计划中标记为 "📝 需更新文件"
```

---

## 五、AGENTS.md 字段解析规范

编排器和 sdd-structure-lint 需要解析 AGENTS.md。以下是精确的解析算法。

### 3.1 解析步骤

```
1. 读取整个 AGENTS.md 文件内容
2. 从"## 项目信息"到下一个"##"之间提取：
   - 匹配 "- name: ..." → name
   - 匹配 "- description: ..." → description
3. 从"## 技术栈"到下一个"##"之间提取：
   - 匹配 "- backend: ..." → backend
   - 匹配 "- frontend: ..." → frontend
   - 匹配 "- database: ..." → database
4. 从"## 路径约定"到下一个"##"之间提取：
   - 匹配 "- changes_dir: ..." → changes_dir
   - 匹配 "- current_dir: ..." → current_dir
   - 匹配 "- archive_dir: ..." → archive_dir
5. 从"## SDD 配置"到下一个"##"之间提取：
   - 匹配 "- flow_engine: ..." → flow_engine
   - 匹配 "- default_flow_level: ..." → default_flow_level
6. 从"## 项目约束"到下一个"##"之间提取：
   - 匹配 "- constitution: ..." → constitution
   - 匹配 "- quirks: ..." → quirks
7. 从"## 自定义覆盖"到文件末尾或下一个"##"之间提取：
   - convention_overrides 后的缩进块为覆盖项
```

### 3.2 值提取规则

```
模式: "- {key}: {value}" 或 "- {key}: \"{value}\""

提取：
  去除前导空格和 "- "
  按 ": " 分割为 key 和 value
  value 去除首尾引号（如有）
  如果 value 以 "{" 开头（如 convention_overrides），读取整个缩进块
```

### 3.3 默认值

未显式声明的字段使用以下默认值：
- `changes_dir` → "docs/changes/"
- `current_dir` → "docs/current/"
- `archive_dir` → "docs/archive/"
- `constitution` → "CONSTITUTION.md"
- `quirks` → "QUIRKS.md"
- `default_flow_level` → "Standard"
- `convention_overrides` → {}（空）
```

---

## 六、Tasks 拆分

按以下 Task 拆分，Coder Agent 逐 Task 实现。

| # | Task | 估时 | 依赖 | AC 覆盖 | 说明 |
|---|------|:---:|------|:---:|------|
| T1 | shared 共享文件 | 45min | 无 | — | handoff-protocol.md, flow-level-rules.md, convention-overrides.md, sdd-rules.md |
| T2 | sdd-structure-lint | 45min | T1 | AC24-27 | 三级合规验证 Skill |
| T3 | sdd-init | 1.5h | T2 | AC1-5 | 项目初始化与升级 Skill + AGENTS.md/CONSTITUTION.md 模板 + .pre-commit-config.yaml + post-commit hook |
| T4 | po-agent + references | 45min | T1 | AC10, AC18 | PO Agent SKILL.md + prd-template.md |
| T5 | ba-agent + references | 45min | T1 | AC11, AC19 | BA Agent SKILL.md + spec-template.md + ac-writing-guide.md |
| T6 | architect-agent + references | 1h | T1 | AC20 | Architect Agent SKILL.md + design-template.md + tasks-template.md + brainstorming-guide.md |
| T7 | coder-agent + references | 45min | T1 | AC21 | Coder Agent SKILL.md + tdd-workflow.md + nfr-checklist.md + task-completion-report-template.md |
| T8 | reviewer-agent + references | 45min | T1 | AC22 | Reviewer Agent SKILL.md + review-checklist.md + severity-guide.md |
| T9 | qa-agent + references | 45min | T1 | AC23 | QA Agent SKILL.md + qa-report-template.md + e2e-ac-mapping-template.md + circuit-breaker.md |
| T10 | sdd-orchestrator | 2h | T2-T9 | AC6-17, AC28-29 | 编排器：流程判定 + 调度 + 门禁 + 归档 + 中断恢复 |
| T11 | AILP 适配验证 | 1h | T10 | 全部 | 将 AILP 的 AGENTS.md 精简为新格式，走一次完整流程验证 |

**总估时：10.75h**

---

## 七、实现顺序

Coder Agent 按以下顺序执行 Task：

```
T1 (shared) → T2 (lint) → T3 (init)
                          → T4-T9 (6 个角色，可部分并行)
                          → T10 (编排器，依赖所有角色)
                          → T11 (验证)
```

T4-T9 虽然无相互依赖，但建议逐 Task 执行（每个完成后便于审查），不强制并行。
