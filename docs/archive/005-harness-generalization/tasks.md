# Tasks: Hermes Harness 通用化优化

> 变更 ID: 005-harness-generalization  
> 对应 Design: [design.md](./design.md)

---

## 执行约定

1. **工作目录**：`/root/workspace/hermes-harness/skills/sdd/`
2. **每 Task 完成后**：commit，格式 `feat(generalization): T{N} {描述}`
3. **验证方式**：手动自检 + grep 验证

---

## Task 执行顺序

```
T1 → T2 → T3 → T4 → T5 → T6 → T7 → T8 → T9 → T10 → T11 → T12 → T13 → T14 → T15 → T16 → T17
```

---

## T1: 通用化 phase-qa.md

**估时**：3min  
**依赖**：无  
**AC 覆盖**：AC1（部分）  
**产出**：`qa-agent/references/phase-qa.md`

### Step 1: 替换 AILP 引用

将文件中的 `"002-ailp-v4-refactor"` 替换为 `"[你的变更ID]"`。

```bash
# 执行替换
sed -i 's/"002-ailp-v4-refactor"/"[你的变更ID]"/g' qa-agent/references/phase-qa.md
```

### Step 2: 验证替换

```bash
# 验证无残留
grep -n "ailp\|002-ailp" qa-agent/references/phase-qa.md
# 预期：无输出

# 验证占位符存在
grep -n "\[你的变更ID\]" qa-agent/references/phase-qa.md
# 预期：显示匹配行
```

### Step 3: Commit

```bash
git add qa-agent/references/phase-qa.md
git commit -m "feat(generalization): T1 通用化 phase-qa.md 中的 AILP 引用"
```

---

## T2: 通用化 phase-review.md

**估时**：3min  
**依赖**：无  
**AC 覆盖**：AC1（部分）  
**产出**：`reviewer-agent/references/phase-review.md`

### Step 1: 替换 AILP 引用

```bash
sed -i 's/"002-ailp-v4-refactor"/"[你的变更ID]"/g' reviewer-agent/references/phase-review.md
```

### Step 2: 验证

```bash
grep -n "ailp\|002-ailp" reviewer-agent/references/phase-review.md || echo "✓ 无 AILP 引用"
grep -n "\[你的变更ID\]" reviewer-agent/references/phase-review.md
```

### Step 3: Commit

```bash
git add reviewer-agent/references/phase-review.md
git commit -m "feat(generalization): T2 通用化 phase-review.md 中的 AILP 引用"
```

---

## T3: 通用化 pr-and-review-flow.md

**估时**：5min  
**依赖**：无  
**AC 覆盖**：AC1（部分）  
**产出**：`sdd-orchestrator/references/pr-and-review-flow.md`

### Step 1: 替换多个 AILP 引用

```bash
sed -i 's/003-git-and-docs/[你的变更ID]/g' sdd-orchestrator/references/pr-and-review-flow.md
sed -i 's/本次 003/本次 [变更ID]/g' sdd-orchestrator/references/pr-and-review-flow.md
sed -i 's/SDD 003/SDD [变更ID]/g' sdd-orchestrator/references/pr-and-review-flow.md
```

### Step 2: 验证

```bash
grep -n "003-git-and-docs\|本次 003\|SDD 003" sdd-orchestrator/references/pr-and-review-flow.md || echo "✓ 无特定引用"
grep -n "\[你的变更ID\]\|\[变更ID\]" sdd-orchestrator/references/pr-and-review-flow.md
```

### Step 3: Commit

```bash
git add sdd-orchestrator/references/pr-and-review-flow.md
git commit -m "feat(generalization): T3 通用化 pr-and-review-flow.md 中的 AILP 引用"
```

---

## T4: 通用化 incremental-mode.md

**估时**：5min  
**依赖**：无  
**AC 覆盖**：AC1（部分）  
**产出**：`sdd-orchestrator/references/incremental-mode.md`

### Step 1: 替换 AILP 引用和项目特定描述

```bash
sed -i 's/"002-ailp-v4-refactor"/"[你的变更ID]"/g' sdd-orchestrator/references/incremental-mode.md
sed -i 's/Phase 1-6 课程系统/多阶段课程系统/g' sdd-orchestrator/references/incremental-mode.md
# 如存在其他 AILP 特定描述，一并替换
```

### Step 2: 验证

```bash
grep -n "ailp\|002-ailp" sdd-orchestrator/references/incremental-mode.md || echo "✓ 无 AILP 引用"
grep -n "课程系统" sdd-orchestrator/references/incremental-mode.md
# 预期显示 "多阶段课程系统"
```

### Step 3: Commit

```bash
git add sdd-orchestrator/references/incremental-mode.md
git commit -m "feat(generalization): T4 通用化 incremental-mode.md 中的 AILP 引用"
```

---

## T5: 通用化 sdd-orchestrator/SKILL.md

**估时**：3min  
**依赖**：无  
**AC 覆盖**：AC1（部分）  
**产出**：`sdd-orchestrator/SKILL.md`

### Step 1: 替换状态文件示例中的 AILP 引用

```bash
sed -i 's/002-ailp-v4-refactor/[你的变更ID]/g' sdd-orchestrator/SKILL.md
```

### Step 2: 验证

```bash
grep -n "ailp\|002-ailp" sdd-orchestrator/SKILL.md || echo "✓ 无 AILP 引用"
grep -n "\[你的变更ID\]" sdd-orchestrator/SKILL.md
```

### Step 3: Commit

```bash
git add sdd-orchestrator/SKILL.md
git commit -m "feat(generalization): T5 通用化 sdd-orchestrator/SKILL.md 中的 AILP 引用"
```

---

## T6: 通用化 sdd-state-schema.md

**估时**：3min  
**依赖**：无  
**AC 覆盖**：AC1（部分）  
**产出**：`shared/sdd-state-schema.md`

### Step 1: 替换 JSON 示例中的 AILP 引用

```bash
sed -i 's/003-git-and-docs/[你的变更ID]/g' shared/sdd-state-schema.md
sed -i 's/002-ailp-v4-refactor/[你的变更ID]/g' shared/sdd-state-schema.md
```

### Step 2: 验证

```bash
grep -n "003-git-and-docs\|002-ailp" shared/sdd-state-schema.md || echo "✓ 无 AILP 引用"
grep -n "\[你的变更ID\]" shared/sdd-state-schema.md
```

### Step 3: Commit

```bash
git add shared/sdd-state-schema.md
git commit -m "feat(generalization): T6 通用化 sdd-state-schema.md 中的 AILP 引用"
```

---

## T7: 通用化 git-workflow.md

**估时**：3min  
**依赖**：无  
**AC 覆盖**：AC1（部分）  
**产出**：`shared/git-workflow.md`

### Step 1: 替换分支命名示例

```bash
sed -i 's/003-git-and-docs/[你的变更ID]/g' shared/git-workflow.md
sed -i 's/004-typo-in-readme/[你的变更ID]/g' shared/git-workflow.md
```

### Step 2: 验证

```bash
grep -n "003-git-and-docs\|004-typo-in-readme" shared/git-workflow.md || echo "✓ 无特定引用"
grep -n "\[你的变更ID\]" shared/git-workflow.md
```

### Step 3: Commit

```bash
git add shared/git-workflow.md
git commit -m "feat(generalization): T7 通用化 git-workflow.md 中的 AILP 引用"
```

---

## T8: 添加 sdd-init frontmatter references

**估时**：3min  
**依赖**：T1-T7  
**AC 覆盖**：AC6（部分）  
**产出**：`sdd-init/SKILL.md`

### Step 1: 检查 references 目录

```bash
ls sdd-init/references/ 2>/dev/null || echo "目录不存在"
# 预期：目录不存在或为空
```

### Step 2: 添加空 references 列表

在 `sdd-init/SKILL.md` 的 frontmatter 中添加：

```yaml
metadata:
  hermes:
    references: []
```

或使用 Python 脚本：

```python
import ruamel.yaml

yaml = ruamel.yaml.YAML()
yaml.preserve_quotes = True

with open('sdd-init/SKILL.md', 'r') as f:
    content = f.read()
    
# 提取 frontmatter
if content.startswith('---'):
    parts = content.split('---', 2)
    frontmatter = yaml.load(parts[1])
    
    # 添加 references
    if 'metadata' not in frontmatter:
        frontmatter['metadata'] = {}
    if 'hermes' not in frontmatter['metadata']:
        frontmatter['metadata']['hermes'] = {}
    frontmatter['metadata']['hermes']['references'] = []
    
    # 写回
    import io
    buf = io.StringIO()
    yaml.dump(frontmatter, buf)
    new_content = f"---\n{buf.getvalue()}---{parts[2]}"
    
    with open('sdd-init/SKILL.md', 'w') as f:
        f.write(new_content)
```

### Step 3: 验证

```bash
grep -A 10 "^metadata:" sdd-init/SKILL.md | grep "references:"
# 预期：显示 references: []
```

### Step 4: Commit

```bash
git add sdd-init/SKILL.md
git commit -m "feat(generalization): T8 添加 sdd-init frontmatter references"
```

---

## T9: 添加 sdd-orchestrator frontmatter references

**估时**：5min  
**依赖**：T3, T4  
**AC 覆盖**：AC3, AC6（部分）  
**产出**：`sdd-orchestrator/SKILL.md`

### Step 1: 添加 references 列表

在 frontmatter 中添加：

```yaml
metadata:
  hermes:
    references:
      - references/sdd-workflow-activation-check.md
      - references/incremental-mode.md
      - references/pr-and-review-flow.md
      - references/quick-flow-phase-gates.md
```

**注意**：T5 已修改此文件，需确保与 T5 的修改合并。

### Step 2: 验证

```bash
grep -A 15 "^metadata:" sdd-orchestrator/SKILL.md | grep "references:"
# 预期显示包含 4 个 references
```

### Step 3: Commit

```bash
git add sdd-orchestrator/SKILL.md
git commit -m "feat(generalization): T9 添加 sdd-orchestrator frontmatter references"
```

---

## T10: 添加 architect-agent frontmatter references

**估时**：5min  
**依赖**：无  
**AC 覆盖**：AC6（部分）  
**产出**：`architect-agent/SKILL.md`

### Step 1: 添加 references 列表

```yaml
metadata:
  hermes:
    references:
      - references/brainstorming-guide.md
      - references/design-template.md
      - references/handoff-to-coder.md
      - references/tasks-template.md
```

### Step 2: Commit

```bash
git add architect-agent/SKILL.md
git commit -m "feat(generalization): T10 添加 architect-agent frontmatter references"
```

---

## T11: 添加 ba-agent frontmatter references

**估时**：3min  
**依赖**：无  
**AC 覆盖**：AC6（部分）  
**产出**：`ba-agent/SKILL.md`

### Step 1: 添加 references 列表

```yaml
metadata:
  hermes:
    references:
      - references/ac-writing-guide.md
      - references/spec-template.md
```

### Step 2: Commit

```bash
git add ba-agent/SKILL.md
git commit -m "feat(generalization): T11 添加 ba-agent frontmatter references"
```

---

## T12: 添加 reviewer-agent frontmatter references

**估时**：3min  
**依赖**：T2  
**AC 覆盖**：AC5, AC6（部分）  
**产出**：`reviewer-agent/SKILL.md`

### Step 1: 添加 references 列表（包含 phase-review.md）

```yaml
metadata:
  hermes:
    references:
      - references/review-checklist.md
      - references/severity-guide.md
      - references/phase-review.md
```

### Step 2: Commit

```bash
git add reviewer-agent/SKILL.md
git commit -m "feat(generalization): T12 添加 reviewer-agent frontmatter references"
```

---

## T13: 添加 po-agent frontmatter references

**估时**：3min  
**依赖**：无  
**AC 覆盖**：AC6（部分）  
**产出**：`po-agent/SKILL.md`

### Step 1: 添加 references 列表

```yaml
metadata:
  hermes:
    references:
      - references/prd-template.md
```

### Step 2: Commit

```bash
git add po-agent/SKILL.md
git commit -m "feat(generalization): T13 添加 po-agent frontmatter references"
```

---

## T14: 添加 sdd-structure-lint frontmatter references

**估时**：3min  
**依赖**：无  
**AC 覆盖**：AC6（部分）  
**产出**：`sdd-structure-lint/SKILL.md`

### Step 1: 检查并添加空列表

```bash
# 检查 references 目录
ls sdd-structure-lint/references/ 2>/dev/null || echo "目录不存在"
```

添加空列表或实际 references：

```yaml
metadata:
  hermes:
    references: []
```

### Step 2: Commit

```bash
git add sdd-structure-lint/SKILL.md
git commit -m "feat(generalization): T14 添加 sdd-structure-lint frontmatter references"
```

---

## T15: 添加 qa-agent frontmatter references

**估时**：5min  
**依赖**：T1  
**AC 覆盖**：AC4, AC6（部分）  
**产出**：`qa-agent/SKILL.md`

### Step 1: 添加 references 列表（包含 phase-qa.md）

```yaml
metadata:
  hermes:
    references:
      - references/ci-only-guide.md
      - references/circuit-breaker.md
      - references/e2e-ac-mapping-template.md
      - references/qa-report-template.md
      - references/phase-qa.md
```

### Step 2: Commit

```bash
git add qa-agent/SKILL.md
git commit -m "feat(generalization): T15 添加 qa-agent frontmatter references"
```

---

## T16: 添加 coder-agent frontmatter references

**估时**：5min  
**依赖**：无  
**AC 覆盖**：AC6（部分）  
**产出**：`coder-agent/SKILL.md`

### Step 1: 添加 references 列表

```yaml
metadata:
  hermes:
    references:
      - references/convention-checklist.md
      - references/nfr-checklist.md
      - references/task-completion-report-template.md
      - references/tdd-workflow.md
```

### Step 2: Commit

```bash
git add coder-agent/SKILL.md
git commit -m "feat(generalization): T16 添加 coder-agent frontmatter references"
```

---

## T17: 最终验证

**估时**：10min  
**依赖**：T1-T16  
**AC 覆盖**：AC1-AC8  
**产出**：验证报告

### Step 1: AC1 - 验证无 AILP 字符串残留

```bash
echo "=== AC1: 检查 AILP 字符串 ==="
PATTERNS="ailp|002-ailp|003-git-and-docs|本次 003|SDD 003"
FILES=(
  "qa-agent/references/phase-qa.md"
  "reviewer-agent/references/phase-review.md"
  "sdd-orchestrator/references/pr-and-review-flow.md"
  "sdd-orchestrator/references/incremental-mode.md"
  "sdd-orchestrator/SKILL.md"
  "shared/sdd-state-schema.md"
  "shared/git-workflow.md"
)

for f in "${FILES[@]}"; do
  result=$(grep -n -E "$PATTERNS" "$f" 2>/dev/null || true)
  if [ -n "$result" ]; then
    echo "❌ $f 包含 AILP 引用:"
    echo "$result"
  else
    echo "✓ $f"
  fi
done
```

### Step 2: AC2 - 验证占位符格式

```bash
echo "=== AC2: 检查占位符格式 ==="
grep -r "\[你的变更ID\]" qa-agent/references/phase-qa.md reviewer-agent/references/phase-review.md
# 预期：显示匹配行
```

### Step 3: AC3-AC6 - 验证 frontmatter references

```bash
echo "=== AC3-AC6: 检查 frontmatter references ==="
SKILLS=("sdd-init" "sdd-orchestrator" "architect-agent" "ba-agent" "reviewer-agent" "po-agent" "sdd-structure-lint" "qa-agent" "coder-agent")

for skill in "${SKILLS[@]}"; do
  file="${skill}/SKILL.md"
  if grep -q "references:" "$file" 2>/dev/null; then
    count=$(grep -A 20 "^metadata:" "$file" | grep "references:" -A 20 | grep "^- " | wc -l)
    echo "✓ $file: $count references"
  else
    echo "❌ $file: 缺少 references"
  fi
done
```

### Step 4: AC7 - 向后兼容（检查核心逻辑未变）

```bash
echo "=== AC7: 向后兼容检查 ==="
# 检查 SKILL.md 的 workflow 部分是否保留
for skill in "${SKILLS[@]}"; do
  if grep -q "## Workflow" "${skill}/SKILL.md"; then
    echo "✓ ${skill}/SKILL.md: Workflow 章节保留"
  fi
done
```

### Step 5: AC8 - 文件完整性

```bash
echo "=== AC8: 文件完整性检查 ==="
REFS_COUNT=$(find . -path "*/references/*.md" -type f | wc -l)
echo "References 文件数: $REFS_COUNT (预期: 21)"
```

### Step 6: Commit 验证脚本

```bash
git add .
git commit -m "feat(generalization): T17 最终验证完成，所有 AC 通过"
```

---

## 汇总

| # | Task | 估时 | 产出文件 | AC 覆盖 |
|---|------|:---:|:--------:|:-------:|
| T1 | 通用化 phase-qa.md | 3min | 1 | AC1 |
| T2 | 通用化 phase-review.md | 3min | 1 | AC1 |
| T3 | 通用化 pr-and-review-flow.md | 5min | 1 | AC1, AC3 |
| T4 | 通用化 incremental-mode.md | 5min | 1 | AC1 |
| T5 | 通用化 sdd-orchestrator/SKILL.md | 3min | 1 | AC1 |
| T6 | 通用化 sdd-state-schema.md | 3min | 1 | AC1 |
| T7 | 通用化 git-workflow.md | 3min | 1 | AC1 |
| T8 | 添加 sdd-init frontmatter | 3min | 1 | AC6 |
| T9 | 添加 sdd-orchestrator frontmatter | 5min | 1 | AC3, AC6 |
| T10 | 添加 architect-agent frontmatter | 5min | 1 | AC6 |
| T11 | 添加 ba-agent frontmatter | 3min | 1 | AC6 |
| T12 | 添加 reviewer-agent frontmatter | 3min | 1 | AC5, AC6 |
| T13 | 添加 po-agent frontmatter | 3min | 1 | AC6 |
| T14 | 添加 sdd-structure-lint frontmatter | 3min | 1 | AC6 |
| T15 | 添加 qa-agent frontmatter | 5min | 1 | AC4, AC6 |
| T16 | 添加 coder-agent frontmatter | 5min | 1 | AC6 |
| T17 | 最终验证 | 10min | 报告 | AC1-AC8 |
| **总计** | | **70min** | **16** | **8/8** |
