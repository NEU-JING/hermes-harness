# SDD 通用开发机制 — 优化方案

> 从 AILP 试点抽象出的跨项目 Agentic SDD 框架
> 核心原则：**流程通用化、角色 Skill 化、项目配置化**

---

## 一、架构总览

```
                        ┌─────────────────────────────┐
                        │      用户（需求 + 审批）       │
                        └─────────────┬───────────────┘
                                      │
┌─────────────────────────────────────┼─────────────────────────────────────┐
│                     SDD Orchestrator（编排器）                              │
│  职责：判定流程级别 → 决定跳过哪些阶段 → 调度角色 Agent → 执行交接协议       │
└─────────────────────────────────────┼─────────────────────────────────────┘
                                      │
        ┌─────────┬─────────┬─────────┼─────────┬─────────┬─────────┐
        ▼         ▼         ▼         ▼         ▼         ▼         ▼
   ┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
   │PO Agent││BA Agent││Archi.  ││Coder   ││Reviewer││QA Agent││用户验收 │
   │        ││        ││Agent   ││Agent   ││Agent   ││        ││(人)    │
   └───┬────┘└───┬────┘└───┬────┘└───┬────┘└───┬────┘└───┬────┘└───┬────┘
       │         │         │         │         │         │         │
       ▼         ▼         ▼         ▼         ▼         ▼         ▼
    prd.md   spec.md  design.md  代码+测试  评审报告  qa报告   合并/归档
                            tasks.md
```

**三层分离**：

| 层 | 位置 | 内容 | 示例 |
|----|------|------|------|
| **通用层** | `~/.hermes/skills/sdd/` | 流程骨架 + 7 个角色 skill + 共享模板 | `coder-agent/SKILL.md` |
| **项目层** | `{project}/AGENTS.md` | 项目路径、技术栈、Constitution 引用 | `backend_dir: "backend/"` |
| **实例层** | `{project}/docs/changes/` | 每次变更的产物文件 | `001-public-profile/prd.md` |

---

## 二、通用 Skills 目录结构

```
~/.hermes/skills/sdd/
├── sdd-orchestrator/
│   └── SKILL.md                    # 编排器（流程判定 + 角色调度 + 门禁管理）
│
├── po-agent/
│   ├── SKILL.md                    # 核心指令（~60行）
│   └── references/
│       ├── prd-template.md         # PRD 模板
│       └── examples.md             # 优秀 PRD 示例
│
├── ba-agent/
│   ├── SKILL.md                    # 核心指令（~70行）
│   └── references/
│       ├── spec-template.md        # Spec 模板
│       ├── ac-writing-guide.md     # AC 编写指南
│       └── error-messages.md       # 错误文案规范
│
├── architect-agent/
│   ├── SKILL.md                    # 核心指令（~80行）
│   └── references/
│       ├── design-template.md      # Design 模板
│       ├── tasks-template.md       # Tasks 模板
│       └── brainstorming-guide.md  # Brainstorming 指南
│
├── coder-agent/
│   ├── SKILL.md                    # 核心指令（~70行）
│   └── references/
│       ├── tdd-workflow.md         # TDD 工作流
│       ├── nfr-checklist.md        # 非功能需求检查清单
│       └── task-completion-report.md # Task 完成报告模板
│
├── reviewer-agent/
│   ├── SKILL.md                    # 核心指令（~60行）
│   └── references/
│       ├── review-checklist.md     # 评审检查清单
│       └── severity-guide.md       # 严重程度分级指南
│
├── qa-agent/
│   ├── SKILL.md                    # 核心指令（~70行）
│   └── references/
│       ├── qa-report-template.md   # QA 报告模板
│       ├── e2e-ac-mapping.md       # E2E-AC 覆盖矩阵模板
│       └── circuit-breaker.md      # 熔断机制规则
│
└── shared/
    ├── handoff-protocol.md         # 角色交接协议（所有角色引用）
    ├── flow-level-rules.md         # Quick/Standard/Enhanced 判定规则
    └── convention-overrides.md     # 项目可通过 AGENTS.md 覆盖的约定
```

---

## 三、角色 Skill 设计（以 Coder Agent 为例）

```markdown
---
name: coder-agent
description: >
  Coder Agent — TDD 实现阶段。读取 tasks.md + design.md，
  按 Task 逐个实现，每个 Task 遵循 RED→GREEN→REFACTOR。
category: sdd
version: 1.0
load_before: []
---

# Coder Agent

## 触发条件
编排器（sdd-orchestrator）判定进入 Implement 阶段，或用户说"开始实现"。

## 前置依赖
- [ ] tasks.md 已产出（含 Task 编号、描述、依赖、估时）
- [ ] design.md 已产出（含推荐方案、接口定义、数据模型）
- [ ] spec.md 已产出（含 AC 编号、业务规则）
- [ ] 用户已确认 Design

## 执行流程

### Step 0: 读取上下文
```
始终加载：AGENTS.md（项目路径、技术栈）
按需加载：skill_view('sdd/coder-agent', file_path='references/tdd-workflow.md')
按需加载：skill_view('sdd/coder-agent', file_path='references/nfr-checklist.md')
```

### Step 1: 按 Task 顺序执行
从 tasks.md 中逐个取出 Task，按依赖顺序：
```
for task in tasks（按依赖排序）:
    1. 读取 task 描述 → 理解范围
    2. 写测试 → RED
    3. 写实现 → GREEN
    4. 重构 → REFACTOR
    5. 输出 Task Completion Report
```

### Step 2: Task Completion Report
每个 Task 完成后输出：
```markdown
## Task {id}: {name} — 完成报告
- 测试：{passed}/{total} 通过
- AC 覆盖：{covered}/{total}
- NFR 检查：
  - [x] 埋点事件
  - [x] 审计日志
  - [ ] 性能（低于阈值）
- 新增/修改文件：
  - backend/app/...
  - backend/tests/...
- 已知限制：
  - AC12 并发测试因 SQLite 限制 skip
```

### Step 3: 交接
所有 Task 完成后，将代码 diff + 所有 Completion Report 打包交给 Reviewer Agent。

## 被禁用行为
- ❌ 不能跳过测试直接写实现
- ❌ 不能修改 spec.md 中的 AC 或业务规则
- ❌ 不能跨 Task 范围修改无关文件
- ❌ 不能 push 代码（仅本地提交）

## 退出条件
- 所有 Task 的 Completion Report 已生成
- 全量测试通过（含新增 + 回归）
- 无遗留 TODO/FIXME
```

## 四、AGENTS.md 精简为项目配置

```markdown
# AGENTS.md — {项目名称}

## 项目信息
- name: "AILP"
- description: "AI 能力验证平台"
- repo: "https://github.com/NEU-JING/ai-learning-platform"

## 技术栈
- backend: FastAPI (Python 3.11)
- frontend: React + Vite
- database: SQLite (dev) / PostgreSQL (prod)
- testing: pytest + Playwright

## 路径约定
- backend_dir: "backend/"
- frontend_dir: "frontend/"
- changes_dir: "docs/changes/"
- current_dir: "docs/current/"
- archive_dir: "docs/archive/"

## SDD 配置
- flow_engine: "sdd/sdd-orchestrator"   # 使用通用编排器
- default_flow_level: "Standard"         # Quick | Standard | Enhanced
- skip_phases_for_quick: ["Spec", "Design", "Review"]

## 项目约束
- constitution: "CONSTITUTION.md"
- quirks: "QUIRKS.md"
- ci_config: ".github/workflows/"

## 自定义覆盖
- convention_overrides:
    tasks_split_rule: "按业务场景拆分，禁止按技术层次拆分"
    test_db: "SQLite in-memory (StaticPool)"
    e2e_seed: "tests/e2e/seed_test_users.py"
```

**所有流程描述从 AGENTS.md 中移除**——流程在 skills 里，AGENTS.md 只声明"我是谁、用哪套流程、有什么约束"。

---

## 五、角色 Skill 加载策略

文档地图按需加载，避免 token 浪费：

```
Agent 启动 → 加载 AGENTS.md（始终，~50 行）
          → 编排器判定当前阶段（如"Implement"）
          → 加载 coder-agent/SKILL.md（始终，~70 行）
          → 执行 Step 0：
              → 读取 AGENTS.md → 获取 backend_dir、constitution 路径
              → skill_view('sdd/coder-agent', file_path='references/tdd-workflow.md')
              → skill_view('sdd/shared', file_path='nfr-checklist.md')
          → 执行 Step 1：读 tasks.md（项目层）→ 逐 Task 实现
```

| 加载项 | 时机 | 大小 |
|--------|------|------|
| AGENTS.md | 始终 | ~50 行 |
| 角色 SKILL.md | 阶段开始时 | ~70 行 |
| references/*.md | 按需 | ~100-200 行/个 |
| 项目产物（tasks.md 等） | 按需 | 不定 |

---

## 六、落地计划

### Phase 1：模板验证（1h）
**目标**：设计一个角色 skill 作为模板，确认格式和粒度。

产出：
- `~/.hermes/skills/sdd/po-agent/SKILL.md`
- `~/.hermes/skills/sdd/po-agent/references/prd-template.md`
- `~/.hermes/skills/sdd/shared/handoff-protocol.md`

验收：
- PO Agent 能按 skill 产出标准 prd.md
- 用户确认 skill 的内容密度和文档地图机制

### Phase 2：批量生成（3h）
**目标**：完成全部 7 个角色 + 编排器 + 共享文件。

产出：
- `sdd-orchestrator/SKILL.md`
- `ba-agent/` `architect-agent/` `coder-agent/` `reviewer-agent/` `qa-agent/` 各目录
- `shared/` 下全部文件

验收：
- 每个角色 skill 的触发条件、执行流程、禁止行为、退出条件完整
- references 文件按需加载机制可用

### Phase 3：AILP 适配（1h）
**目标**：将 AILP 从 AGENTS.md 大文件切割为项目配置。

产出：
- 新版 `AGENTS.md`（纯配置，~50 行）
- 原有流程描述从 AGENTS.md 移除

验收：
- 用新版 AGENTS.md + 通用 skills 能完整执行一次 SDD 流程
- 不丢失原有功能

### Phase 4：通用化验证（1.5h）
**目标**：在另一个项目中验证通用性。

方案：
- 创建一个 mock 项目（Go + PostgreSQL）
- 编写该项目的 AGENTS.md
- 用同一套 sdd skills 走一遍 SDD 流程

验收：
- skills 不依赖 AILP 特有的路径/技术栈
- AGENTS.md 的覆盖配置正确生效

**总估时：6.5h**

---

## 七、与现有机制的兼容

| 现有机制 | 迁移方式 |
|---------|---------|
| `ailp-sdd-workflow` skill | → 拆分为通用 `sdd/*` skills + AILP 特有内容回写到项目的 AGENTS.md |
| `ailp-spec-linter` | → 保留为项目级 skill，不通用化（因为 lint 规则与项目 Constitution 绑定） |
| `ailp-brainstorming` | → 合并到 `architect-agent/SKILL.md` 的 Step 1 |
| `ailp-flow-level` | → 合并到 `sdd-orchestrator/SKILL.md`，判定规则从 `shared/flow-level-rules.md` 加载 |
| `post-coding-review` | → 合并到 `reviewer-agent/SKILL.md` |
| `ailp-qa-circuit-breaker` | → 合并到 `qa-agent/references/circuit-breaker.md` |
| AILP 项目的 `CONSTITUTION.md` | → 保留，通过 AGENTS.md 的 `constitution` 字段引用 |
