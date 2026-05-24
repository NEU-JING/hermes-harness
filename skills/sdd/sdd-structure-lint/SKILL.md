---
name: sdd-structure-lint
description: Use when verifying SDD project structure compliance at file-level, handoff-level, or content-level. Run before every phase gate to ensure all required artifacts exist and are well-formed.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sdd, lint, compliance, verification, structure]
    related_skills: [sdd-orchestrator, sdd-init, writing-plans]
---

# SDD Structure Lint — 三级合规验证

## Overview

SDD 项目中每个阶段切换前都必须验证产物完整性。sdd-structure-lint 提供三级合规验证，从粗到细逐层检查。

**调用方**：sdd-orchestrator 在每阶段门禁检查时调用，开发者也可手动运行。

## When to Use

- 编排器门禁检查：阶段切换前自动触发
- 开发者自检：提交代码前验证产物完整性
- CI 流水线：PR 合并前的自动化检查
- sdd-init 完成后：验证初始化结果

**不用此 Skill 的场景**：代码 lint（那是 pre-commit 的职责，见 R8）

## 三级验证

### Level 1: 文件级检查（File-Level）

验证 SDD 项目的基础结构完整性。

**检查项**：

| 检查项 | 文件/目录 | 严重级别 |
|--------|----------|:---:|
| AGENTS.md 存在 | `AGENTS.md` | CRITICAL |
| CONSTITUTION.md 存在 | `CONSTITUTION.md` | MAJOR |
| QUIRKS.md 存在 | `QUIRKS.md` | MAJOR |
| changes 目录存在 | `docs/changes/` | CRITICAL |
| current 目录存在 | `docs/current/` | MAJOR |
| archive 目录存在 | `docs/archive/` | MAJOR |

**执行方式**：

```bash
# 基础文件检查
for f in AGENTS.md CONSTITUTION.md QUIRKS.md; do
  test -f "$f" && echo "✓ $f" || echo "✗ MISSING: $f (CRITICAL)"
done

# 目录检查
for d in docs/changes docs/current docs/archive; do
  test -d "$d" && echo "✓ $d/" || echo "✗ MISSING: $d/ (CRITICAL/MAJOR)"
done
```

---

### Level 2: 交接级检查（Handoff-Level）

验证当前阶段必选产物是否存在。不同阶段要求不同产物。

**阶段-产物映射**：

| 阶段 | 必选产物 | 可选产物 |
|------|---------|---------|
| PO 完成 | `docs/changes/{id}/prd.md` | — |
| BA 完成 | `docs/changes/{id}/spec.md` | — |
| Architect 完成 | `docs/changes/{id}/design.md`, `tasks.md` | — |
| Coder 完成 | 代码变更 (git diff), 测试通过 | Task 完成报告 |
| Reviewer 完成 | `docs/changes/{id}/review-report.md` | — |
| QA 完成 | `docs/changes/{id}/qa-report.md` | E2E 测试报告 |
| 归档前 | 全部上述文件 | sdd-state.json |

**执行方式**：

```bash
change_id="001-sdd-init"  # 从上下文获取
dir="docs/changes/${change_id}"

case "$phase" in
  po)
    test -f "$dir/prd.md" || echo "MISSING: prd.md"
    ;;
  ba)
    test -f "$dir/spec.md" || echo "MISSING: spec.md"
    ;;
  architect)
    test -f "$dir/design.md" || echo "MISSING: design.md"
    test -f "$dir/tasks.md" || echo "MISSING: tasks.md"
    ;;
  coder)
    git diff --stat HEAD || echo "No code changes detected"
    ;;
  reviewer)
    test -f "$dir/review-report.md" || echo "MISSING: review-report.md"
    ;;
  qa)
    test -f "$dir/qa-report.md" || echo "MISSING: qa-report.md"
    ;;
esac
```

---

### Level 3: 内容级检查（Content-Level）

验证产物内容质量，确保 Agent 可解析。

#### 3.1 PRD 内容检查

```bash
# PRD 必须包含以下章节
grep -cE "^## (背景与目标|用户场景|功能范围|非功能需求|验收标准|风险与假设)" prd.md
# 期望: 6（可容忍 ≥ 4）
```

#### 3.2 Spec AC 编号检查

```bash
# AC 编号格式: AC{n}，需连续
grep -oP "AC\d+" spec.md | sort -t'C' -k2 -n | uniq
# 检查：无跳号（如 AC1 AC3 缺 AC2）
```

#### 3.3 Design 方案对比检查

```bash
# Standard/Enhanced 流程要求 ≥ 2 方案对比
grep -c "^### 方案" design.md
# 期望: ≥ 2
```

#### 3.4 Tasks 表格格式检查

```bash
# Tasks 文档必须包含任务表格
grep -c "| # | Task |" tasks.md
# 期望: ≥ 1
```

#### 3.5 Review Report 字段完整性

```bash
# Review report 必须包含结论和严重级别
grep -cE "(评审结论|CRITICAL|MAJOR)" review-report.md
# 期望: ≥ 3
```

#### 3.6 QA Report 覆盖矩阵

```bash
# QA Report 必须包含 AC 覆盖矩阵
grep -c "AC 覆盖矩阵" qa-report.md
# 期望: ≥ 1
```

#### 3.7 Skill YAML Frontmatter 检查

```bash
# 所有 SKILL.md 必须有合法 YAML frontmatter
python3 -c "
import yaml, os, glob
errors = []
for f in glob.glob('skills/**/SKILL.md', recursive=True):
    content = open(f).read()
    if not content.startswith('---'):
        errors.append(f'{f}: missing frontmatter')
        continue
    parts = content.split('---')
    if len(parts) < 3:
        errors.append(f'{f}: malformed frontmatter')
        continue
    try:
        fm = yaml.safe_load(parts[1])
        assert 'name' in fm, f'{f}: missing name'
        assert 'description' in fm, f'{f}: missing description'
    except Exception as e:
        errors.append(f'{f}: {e}')
if errors:
    for e in errors:
        print(f'✗ {e}')
    exit(1)
print('✓ All SKILL.md frontmatters valid')
"
```

---

## 错误报告格式

验证完成后输出标准化的 Markdown 报告：

```markdown
# SDD Structure Lint Report

**项目**：{project_name}
**变更 ID**：{change_id}
**阶段**：{current_phase}
**检查级别**：Level {1|2|3}

## 结果总览

- CRITICAL: {count}
- MAJOR: {count}
- MINOR: {count}
- INFO: {count}

## CRITICAL

| 检查项 | 问题 | 修复建议 |
|--------|------|---------|
| ... | ... | ... |

## MAJOR

...

## 结论

{通过 / 不通过}
```

---

## 编排器集成

sdd-orchestrator 在以下时机自动调用本 Skill：

1. **阶段切换前**：Level 1 + Level 2（当前阶段产物）
2. **归档前**：Level 1 + Level 2 + Level 3（全部产物）
3. **sdd-init 后**：Level 1（基础结构）

调用方式：

```
skill_view(name='sdd-structure-lint')
→ 执行对应 Level 的检查
→ 输出报告
→ 返回通过/不通过
```

## Common Pitfalls

1. **Level 2 用错阶段名**：检查阶段的产物映射必须匹配编排器当前阶段，如 `architect` 而非 `design`
2. **Level 3 正则过于严格**：AC 编号允许非连续（如删除了某个 AC），但需在报告中标注
3. **忽略 SKILL.md 检查**：项目内部创建的 Skills 也需要 frontmatter 验证，部署前尤其关键
4. **只检查存在性不检查内容**：Level 1 只证明文件存在，不证明内容正确 —— 必须配合 Level 3

## Verification Checklist

- [ ] Level 1: 基础文件齐全（AGENTS.md 等 6 项）
- [ ] Level 2: 当前阶段产物存在
- [ ] Level 3: 内容质量达标（AC 格式、方案对比、YAML frontmatter）
- [ ] 错误报告格式标准化
- [ ] 编排器集成点正确（阶段切换/归档/init 后）
