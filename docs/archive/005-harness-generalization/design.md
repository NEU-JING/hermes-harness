# Design: Hermes Harness 通用化优化

> 变更 ID: 005-harness-generalization  
> 创建日期: 2026-05-30  
> 对应 Spec: [spec.md](./spec.md)

---

## 一、产出物清单

### 修改文件（16 个）

**7 个需通用化的文件**：
```
skills/sdd/
├── qa-agent/references/phase-qa.md
├── reviewer-agent/references/phase-review.md
├── sdd-orchestrator/references/pr-and-review-flow.md
├── sdd-orchestrator/references/incremental-mode.md
├── sdd-orchestrator/SKILL.md
├── shared/sdd-state-schema.md
└── shared/git-workflow.md
```

**9 个需添加 frontmatter references 的 SKILL.md**：
```
skills/sdd/
├── sdd-init/SKILL.md
├── sdd-orchestrator/SKILL.md
├── architect-agent/SKILL.md
├── ba-agent/SKILL.md
├── reviewer-agent/SKILL.md
├── po-agent/SKILL.md
├── sdd-structure-lint/SKILL.md
├── qa-agent/SKILL.md
└── coder-agent/SKILL.md
```

**总计**：16 个文件修改。

---

## 二、技术方案对比（Brainstorming）

### 方案 A：手动逐个文件修改

**描述**：按文件清单逐个打开文件，执行字符串替换和 frontmatter 添加。

**优点**：
- 控制精确，可逐行验证
- 适合不熟悉脚本的用户

**缺点**：
- 耗时较长（16 个文件 × 5 分钟 ≈ 80 分钟）
- 容易遗漏或格式不一致
- 可重复性差

**适用场景**：文件数量少、修改复杂度高

---

### 方案 B：脚本化批量处理 + 人工复核

**描述**：
1. 使用 Python 脚本执行字符串替换（`sed`/`re.sub`）
2. 使用 YAML 解析器修改 frontmatter
3. 人工复核修改结果

**优点**：
- 快速（脚本运行 < 1 分钟）
- 一致性好
- 可重复执行
- 易扩展（新增替换规则只需改配置）

**缺点**：
- 需要编写脚本
- 复杂替换逻辑可能遗漏边界情况

**适用场景**：文件数量多、修改模式化

---

### 方案对比总结

| 维度 | 方案 A（手动） | 方案 B（脚本化） | 推荐 |
|------|:---:|:---:|:---:|
| 复杂度 | 低 | 中 | |
| 耗时 | 高 | 低 | ✓ |
| 一致性 | 低 | 高 | ✓ |
| 可重复性 | 低 | 高 | ✓ |
| 风险 | 遗漏风险 | 脚本 bug 风险 | ✓ |

**最终选择**：方案 B（脚本化批量处理）

**理由**：
1. 本次变更涉及 16 个文件，模式化程度高（字符串替换 + frontmatter 添加）
2. 替换规则明确，适合脚本化
3. 脚本化后可作为后续类似变更的模板
4. Quick 流程允许轻量脚本辅助

---

## 三、架构设计

### 整体架构

```
┌─────────────────┐
│   变更触发      │ 用户确认 Spec，进入 Phase 3
└────────┬────────┘
         ▼
┌─────────────────┐
│  Task 1-7       │ 通用化替换（7 个文件）
│  字符串替换     │ sed / Python re.sub
└────────┬────────┘
         ▼
┌─────────────────┐
│  Task 8-16      │ Frontmatter 添加（9 个 SKILL.md）
│  YAML 修改      │ Python ruamel.yaml
└────────┬────────┘
         ▼
┌─────────────────┐
│   验证          │ grep / Python 脚本验证
└─────────────────┘
```

### 数据流

1. **输入**：Spec 中定义的替换规则映射表、frontmatter 配置
2. **处理**：Task 按顺序执行，每 Task 修改 1 个文件
3. **输出**：修改后的 16 个文件
4. **验证**：AC1-AC8 验证脚本

### 关键决策

| 决策 | 选项 | 选择 | 理由 |
|------|------|:---:|------|
| 替换工具 | sed / Python re | Python | 复杂替换（如整行替换）更灵活 |
| frontmatter 解析 | 正则 / YAML 库 | ruamel.yaml | 保持格式和注释 |
| 验证方式 | 手动 / 脚本 | 脚本 | 可复用，减少遗漏 |
| 提交粒度 | 单文件 / 批量 | 单文件 per Task | 便于回滚和 Review |

---

## 四、详细设计

### 模块 1：字符串替换（7 个文件）

**职责**：将 AILP 特定字符串替换为通用占位符

**接口**：
```python
def replace_in_file(filepath: str, rules: List[Tuple[str, str]]) -> None:
    """在文件中执行批量替换"""
    
def verify_no_patterns(filepath: str, patterns: List[str]) -> bool:
    """验证文件不包含禁用模式"""
```

**关键实现**：
- 使用 `re.sub` 进行正则替换
- 替换前备份原文件
- 替换后验证无残留

**文件与规则映射**：

| 文件 | 主要替换规则 |
|------|-------------|
| phase-qa.md | `002-ailp-v4-refactor` → `[你的变更ID]` |
| phase-review.md | `002-ailp-v4-refactor` → `[你的变更ID]` |
| pr-and-review-flow.md | `003-git-and-docs` → `[你的变更ID]`，`本次 003` → `本次 [变更ID]` |
| incremental-mode.md | `002-ailp-v4-refactor` → `[你的变更ID]`，`Phase 1-6 课程系统` → `多阶段课程系统` |
| sdd-orchestrator/SKILL.md | `002-ailp-v4-refactor` → `[你的变更ID]` |
| sdd-state-schema.md | `003-git-and-docs` → `[你的变更ID]`，`002-ailp-v4-refactor` → `[你的变更ID]` |
| git-workflow.md | `003-git-and-docs` → `[你的变更ID]`，`004-typo-in-readme` → `[你的变更ID]` |

---

### 模块 2：Frontmatter 添加（9 个 SKILL.md）

**职责**：为每个 SKILL.md 添加 `metadata.hermes.references` 列表

**接口**：
```python
def add_references_to_frontmatter(filepath: str, references: List[str]) -> None:
    """在 SKILL.md frontmatter 中添加 references 列表"""
```

**关键实现**：
- 使用 `ruamel.yaml` 解析和修改 YAML
- 保持原有 frontmatter 其他字段
- references 路径格式：`references/{filename}.md`

**SKILL.md 与 references 映射**：

| SKILL.md | 需要添加的 references |
|----------|---------------------|
| sdd-init/SKILL.md | `[]`（无 references 目录） |
| sdd-orchestrator/SKILL.md | `pr-and-review-flow.md`, `incremental-mode.md`, `sdd-workflow-activation-check.md`, `quick-flow-phase-gates.md` |
| architect-agent/SKILL.md | `brainstorming-guide.md`, `design-template.md`, `handoff-to-coder.md`, `tasks-template.md` |
| ba-agent/SKILL.md | `ac-writing-guide.md`, `spec-template.md` |
| reviewer-agent/SKILL.md | `review-checklist.md`, `severity-guide.md`, `phase-review.md` |
| po-agent/SKILL.md | `prd-template.md` |
| sdd-structure-lint/SKILL.md | `[]`（无 references 目录） |
| qa-agent/SKILL.md | `ci-only-guide.md`, `circuit-breaker.md`, `e2e-ac-mapping-template.md`, `qa-report-template.md`, `phase-qa.md` |
| coder-agent/SKILL.md | `convention-checklist.md`, `nfr-checklist.md`, `task-completion-report-template.md`, `tdd-workflow.md` |

---

### 模块 3：验证

**职责**：验证所有 AC 是否满足

**接口**：
```python
def verify_ac1() -> bool:  # AILP 字符串移除
    pass

def verify_ac2() -> bool:  # 占位符格式
    pass

def verify_ac3_ac5() -> bool:  # 孤立文件引用
    pass

def verify_ac6() -> bool:  # 全部 references 完整性
    pass

def verify_ac7() -> bool:  # 向后兼容
    pass

def verify_ac8() -> bool:  # 无文件删除
    pass
```

---

## 五、配置与约定

### 路径约定

| 路径 | 用途 |
|------|------|
| `~/.hermes/skills/sdd/` | Skills 根目录 |
| `qa-agent/references/` | qa-agent references 目录 |
| `reviewer-agent/references/` | reviewer-agent references 目录 |
| `sdd-orchestrator/references/` | orchestrator references 目录 |
| `shared/` | 共享 references 目录 |

### Commit 约定

格式：`feat(generalization): T{N} {描述}`

---

## 六、Tasks 拆分

详见 [tasks.md](./tasks.md)

| # | Task | 估时 | 产出 |
|---|------|:---:|------|
| T1 | 通用化 phase-qa.md | 3min | 修改后文件 |
| T2 | 通用化 phase-review.md | 3min | 修改后文件 |
| T3 | 通用化 pr-and-review-flow.md | 5min | 修改后文件 |
| T4 | 通用化 incremental-mode.md | 5min | 修改后文件 |
| T5 | 通用化 sdd-orchestrator/SKILL.md | 3min | 修改后文件 |
| T6 | 通用化 sdd-state-schema.md | 3min | 修改后文件 |
| T7 | 通用化 git-workflow.md | 3min | 修改后文件 |
| T8 | 添加 sdd-init frontmatter | 3min | 修改后文件 |
| T9 | 添加 sdd-orchestrator frontmatter | 5min | 修改后文件 |
| T10 | 添加 architect-agent frontmatter | 5min | 修改后文件 |
| T11 | 添加 ba-agent frontmatter | 3min | 修改后文件 |
| T12 | 添加 reviewer-agent frontmatter | 3min | 修改后文件 |
| T13 | 添加 po-agent frontmatter | 3min | 修改后文件 |
| T14 | 添加 sdd-structure-lint frontmatter | 3min | 修改后文件 |
| T15 | 添加 qa-agent frontmatter | 5min | 修改后文件 |
| T16 | 添加 coder-agent frontmatter | 5min | 修改后文件 |
| T17 | 最终验证 | 10min | 验证报告 |

**总估时**：70min

---

## 七、实现顺序

```
T1 → T2 → T3 → T4 → T5 → T6 → T7 → T8 → T9 → T10 → T11 → T12 → T13 → T14 → T15 → T16 → T17
```
