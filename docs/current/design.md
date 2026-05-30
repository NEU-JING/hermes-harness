# Design — Hermes Harness（SDD 通用开发机制）

> **Technical Design Document**
> 版本：1.0 | 最后更新：2026-05-25

---

## 1. 架构概览

### 1.1 三层分离

```
                        ┌─────────────────────────────┐
                        │      用户（需求 + 审批）       │
                        └─────────────┬───────────────┘
                                      │
┌─────────────────────────────────────┼─────────────────────────────────────┐
│                     SDD Orchestrator（编排器）                              │
│  职责：判定流程级别 → 决定跳过哪些阶段 → 调度角色 → 执行门禁                 │
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

| 层 | 位置 | 内容 | 示例 |
|----|------|------|------|
| **通用层** | `~/.hermes/skills/sdd/` | 流程骨架 + 8 个角色 Skill + 共享规范 | `coder-agent/SKILL.md` |
| **项目层** | `{project}/AGENTS.md` | 项目路径、技术栈、规则覆盖 | `backend_dir: "backend/"` |
| **实例层** | `{project}/docs/changes/` | 每次变更的产物文件 | `001-public-profile/prd.md` |

---

## 2. Skills 目录结构

```
~/.hermes/skills/sdd/
├── sdd-orchestrator/
│   ├── SKILL.md                          # 编排器
│   └── references/
│       └── pr-and-review-flow.md         # PR 生命周期 + Reviewer 回退实战案例
│
├── po-agent/
│   └── SKILL.md                          # PO Agent（~60 行）
│
├── ba-agent/
│   └── SKILL.md                          # BA Agent（~70 行）
│
├── architect-agent/
│   └── SKILL.md                          # Architect Agent（~80 行）
│
├── coder-agent/
│   └── SKILL.md                          # Coder Agent（~70 行）
│
├── reviewer-agent/
│   └── SKILL.md                          # Reviewer Agent（~60 行）
│
├── qa-agent/
│   └── SKILL.md                          # QA Agent（~70 行）
│
├── sdd-init/
│   ├── SKILL.md                          # 项目初始化/升级
│   └── templates/
│       ├── constitution-template.md
│       └── quirks-template.md
│
├── sdd-structure-lint/
│   └── SKILL.md                          # 三级结构验证
│
└── shared/
    ├── sdd-rules.md                      # R1-R10 通用规则
    ├── flow-level-rules.md               # Quick/Standard/Enhanced 判定
    ├── handoff-protocol.md               # Agent 间交接协议
    ├── convention-overrides.md           # 项目级规则覆盖机制
    └── git-workflow.md                   # Git 分支/PR/合并策略
```

### 2.1 角色 Skill 粒度原则

| 部位 | 行数 | 内容 |
|------|:--:|------|
| SKILL.md | ≤100 | 触发条件、执行流程、禁止行为、退出条件 |
| references/ | 按需 | 模板、指南、清单（通过 `skill_view` 按需加载） |
| shared/ | 共享 | 所有角色引用的通用规范 |

**设计决策**：角色 SKILL.md 不内嵌模板和详细指南——这些放 references/，Agent 需要时按需加载，避免浪费 token。

---

## 3. 文件格式规范

### 3.1 Skill 文件（SKILL.md）

```yaml
---
name: coder-agent
description: TDD 实现阶段。按 Task 逐个实现，遵循 RED→GREEN→REFACTOR。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sdd, coder, implementation]
    related_skills: [architect-agent, reviewer-agent]
---

# Coder Agent

## 触发条件
...

## 前置依赖
...

## 执行流程
...

## 禁止行为
...

## 退出条件
...
```

**约束**：
- YAML frontmatter 必含 `name`、`description`
- 章节顺序：触发条件 → 前置依赖 → 执行流程 → 禁止行为 → 退出条件
- `references/` 文件无 YAML frontmatter（纯 Markdown，被 `skill_view` 按路径加载）

### 3.2 AGENTS.md（项目配置）

```markdown
# AGENTS.md — {项目名称}

## 项目信息
- name: "..."
- description: "..."
- repo: "..."

## 技术栈
- backend: "..."
- frontend: "..."

## 路径约定
- changes_dir: "docs/changes/"
- current_dir: "docs/current/"
- archive_dir: "docs/archive/"

## SDD 配置
- flow_engine: "sdd/sdd-orchestrator"
- default_flow_level: "Standard"

## 项目约束
- constitution: "CONSTITUTION.md"
- quirks: "QUIRKS.md"

## 自定义覆盖
- convention_overrides:
    disable_rules: []
    custom_rules: []
```

### 3.3 .sdd-state.json（中断恢复）

```json
{
  "change_id": "001-sdd-init",
  "flow_level": "Standard",
  "current_phase": "architect",
  "phases_completed": ["po", "ba"],
  "review_round": 0,
  "previous_review_outcome": null,
  "started_at": "2026-05-25T10:00:00Z",
  "updated_at": "2026-05-25T11:30:00Z"
}
```

**增量模式字段**（SDD 004 新增）：
```json
{
  "incremental_mode": true,
  "current_sub_phase": "phase_2_core",
  "sub_phases_completed": ["phase_1_data"],
  "phase_status": {
    "phase_1_data": {
      "status": "qa_passed",
      "ac_covered": ["AC1-AC5"],
      "completed_at": "2026-05-30T10:00:00Z"
    },
    "phase_2_core": {
      "status": "in_progress",
      "depends_on": ["phase_1_data"]
    }
  }
}
```

**增强字段**（SDD 003 新增）：
- `review_round`：Reviewer 回退轮次计数
- `previous_review_outcome`：上一轮 Review 结论

---

## 4. 项目产物结构

```
{project}/
├── AGENTS.md                     # 项目配置
├── CONSTITUTION.md               # 项目宪法
├── QUIRKS.md                     # 已知陷阱
│
├── docs/
│   ├── changes/                  # 进行中的变更（SDD 工作区）
│   │   └── NNN-short-name/
│   │       ├── .sdd-state.json   # 流程状态
│   │       ├── prd.md
│   │       ├── spec.md
│   │       ├── design.md
│   │       ├── tasks.md
│   │       ├── review-report.md
│   │       └── qa-report.md
│   │
│   ├── current/                  # 当前生产基线（融合后全貌）
│   │   ├── README.md             # 文档地图
│   │   ├── prd.md
│   │   ├── spec.md
│   │   └── design.md
│   │
│   └── archive/                  # 历史变更归档
│       └── NNN-short-name/       # merge 后从 changes/ 移入
│           └── ...（prd/spec/design/tasks/review/qa）
```

### 4.1 目录约束（C1-C5）

| 规则 | 约束 | 违反后果 |
|------|------|---------|
| C1 | 变更必须在 `{changes_dir}/NNN-short-name/` 下 | 编排器拒绝启动 |
| C2 | change-id 格式 `NNN-short-name`（3 位数字 + 英文短名） | 编排器报错 |
| C3 | 产物写入约定文件名 | 角色退出前自检，不满足不交接 |
| C4 | 归档条件：全量测试通过 + 用户验收 | 编排器检查，不满足不归档 |
| C5 | 归档后变更目录从 `changes/` 移至 `archive/` | 编排器执行 |

---

## 5. 数据流

### 5.1 Skill 加载链

```
Agent 启动
  → 加载 AGENTS.md（始终，~50 行）
  → 编排器判定当前阶段
  → 加载对应角色 SKILL.md（始终，~70 行）
  → 按需加载 references/*.md（通过 skill_view）
  → 读取项目产物文件（tasks.md、spec.md 等）
```

| 加载项 | 时机 | 大小 |
|--------|------|------|
| AGENTS.md | 始终 | ~50 行 |
| 角色 SKILL.md | 阶段开始时 | ~70 行 |
| references/*.md | 按需（通过 `skill_view`） | ~100-200 行/个 |
| 项目产物 | 按需 | 不定 |

### 5.2 阶段间数据传递

```
PO → BA:     prd.md（用户已确认）
BA → AR:     prd.md + spec.md（用户已确认）
AR → CO:     spec.md + design.md + tasks.md（用户已确认）
CO → RE:     代码 diff + Task Completion Report
RE → QA:     review-report.md（通过/有条件通过）
QA → UA:     qa-report.md（通过）
UA → ARV:    用户明确确认
```

### 5.3 归档数据流

```
用户验收通过
  → Step 8.0: R10 检查（branch + merge commit）
  → Step 8.1: 基线融合
      - prd.md → docs/current/prd.md（功能范围章节）
      - spec.md → docs/current/spec.md（新增需求）
      - design.md → docs/current/design.md（架构变更）
  → Step 8.2: sdd-structure-lint Level 3
  → Step 8.3: git mv docs/changes/{id}/ → docs/archive/{id}/
  → Step 8.4: 清理 .sdd-state.json
  → Step 8.5: 输出归档摘要
```

### 5.4 增量模式数据流（SDD 004 新增）

```
Architect 产出 tasks.md（含 Phase 标记）
  → Coder Phase 1 Coding → Phase 1 Review → Phase 1 QA → 用户确认 Phase 1
    ↓（用户选择继续）
  → Coder Phase 2 Coding → Phase 2 Review → Phase 2 QA → 用户确认 Phase 2
    ↓
  → ...
  → 全部 Phase 验收通过 → 归档（含所有 Phase Review/QA 报告）
```

**Phase 门禁检查**：
```
Phase N 开始前
  → 检查 .sdd-state.json phase_status[Phase N-1].status == "accepted"
  → 依赖满足 → 继续
  → 依赖不满足 → 阻断，提示"请先完成 Phase N-1"
```

---

## 6. 安装机制

### 6.1 install.sh

```bash
./install.sh          # 全新安装（检测到已有→提示 --force）
./install.sh --force  # 覆盖更新
```

**安装内容**：
- `cp -r skills/sdd/` → `~/.hermes/skills/sdd/`
- 含 `shared/` 和 `references/` 子目录
- 安装后列出所有 Skill + shared 文件供确认

### 6.2 与 Hermes Agent v2.0 的集成

- Skills 通过 `skill_view()` 文档地图机制加载
- `~/.hermes/skills/` 目录在 Agent 启动时自动编入索引
- shared/ 文件通过 `skill_view(name='sdd-rules')` 按名称加载

---

## 7. 关键技术决策

| 决策 | 理由 | 替代方案 |
|------|------|---------|
| **纯 Markdown + YAML frontmatter** | 零平台锁定，任何支持 system prompt 的 Agent 可用 | JSON/YAML 配置文件 → 对 Agent 不友好 |
| **角色 SKILL.md ≤100 行** | Token 效率，角色 Agent 不需要读完所有 references | 单一大文件 → token 浪费 |
| **references 按需加载** | 避免每次加载全部文档 | 始终加载 → 不适合轻量流程 |
| **AGENTS.md 纯配置** | 流程描述在 Skills 里，项目只声明"我是谁" | 流程也在 AGENTS.md → 跨项目无法复用 |
| **sdd-init 分 init/upgrade 双模式** | 覆盖新项目和存量项目两种场景 | 仅 init 模式 → 无法接入存量项目 |
| **R10 用纯 git 命令检测** | 不依赖外部文件加载，归档前直接执行 | 加载 git-workflow.md 检查 → 增加失败面 |
| **.sdd-state.json 持久化** | 支持 Agent 重启后从中断点恢复 | 内存状态 → 重启丢失进度 |
| **Phase 级交付** | 大型重构可早期验证方向，降低返工成本 | 线性瀑布 → 问题发现晚、返工成本高 |
| **Phase 状态机** | `phase_status` 字段明确追踪各 Phase 生命周期 | 无状态追踪 → 依赖关系混乱 |
| **Phase 门禁前置** | 开始前检查依赖，防止非法状态推进 | 后置检查 → 发现问题时已执行大量工作 |
