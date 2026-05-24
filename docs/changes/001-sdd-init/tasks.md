# Tasks: SDD 通用开发机制

> 版本：V1.1
> 日期：2026-05-25
> 前提：Design V2.1 已确认，所有技术细节见 Design 对应章节
> **执行者**：Coder Agent（千帆模型，单任务串行）
> **验证者**：人类审查每 Task 完成后确认

---

## 路径约定

| 类别 | 开发路径（项目内） | 部署目标路径 |
|------|-------------------|-------------|
| 通用 Skill | `skills/sdd/{skill-name}/` | `~/.hermes/skills/sdd/{skill-name}/` |
| 共享文件 | `skills/sdd/shared/` | `~/.hermes/skills/sdd/shared/` |
| 项目模板 | `skills/sdd/sdd-init/templates/` | 由 sdd-init 在目标项目中生成 |

**开发阶段所有文件写入项目内**（`skills/sdd/`），Git 管理。**部署阶段**（T12）一次性拷贝到正式路径。

---

## 执行约定

1. **工作目录**：所有操作在 `/root/.hermes/projects/hermes-sdd` 下执行
2. **每 Task 完成后**：`git add` 对应文件并 commit，格式 `feat(sdd): T{N} {简短描述}`
3. **验证方式**：开发阶段 sdd-structure-lint 尚未部署，手动按同样标准检查：
   - T2 完成后，Coder Agent 已明确三级验证标准
   - T3-T10 每 Task 完成后，Coder Agent 自检：YAML frontmatter 合法性 + 产出文件存在性 + 内容完整性
   - **T12 部署后**：正式调用 sdd-structure-lint 做全量自动化验证
4. **YAML frontmatter**：每个 SKILL.md 必须包含合法的 YAML frontmatter（name, description, version），写入后用 Python `yaml.safe_load()` 验证
5. **Content 参考**：每 Task 的内容细节已在 Design.md 对应章节定义（如 T4 内容见 Design §2.5），Tasks 文档不重复，只给出执行步骤和验证

---

## Task 执行顺序

```
T1 (shared) ──┬── T2 (sdd-structure-lint)
               │
               ├── T4 (po-agent)
               ├── T5 (ba-agent)
               ├── T6 (architect-agent)
               ├── T7 (coder-agent)
               ├── T8 (reviewer-agent)
               └── T9 (qa-agent)
                        │
               T3 (sdd-init, 依赖 T2)
                        │
               T10 (sdd-orchestrator, 依赖 T2-T9)
                        │
               T11 (AILP 适配验证, 依赖 T10)
                        │
               T12 (部署发布, 依赖 T11)
```

T4-T9 无相互依赖，但建议逐 Task 串行（每完成一个审查一个）。

---

## T1: shared 共享文件

**估时**：45min
**依赖**：无
**产出**：`skills/sdd/shared/` 下 4 个文件

### Step 1: 创建目录

```bash
mkdir -p skills/sdd/shared
```

### Step 2: 创建 `handoff-protocol.md`

文件：`skills/sdd/shared/handoff-protocol.md`

参考：Design §三（规则间的交接定义）+ §2.1 编排器中的角色调度逻辑

内容要点：
- 定义 7 个角色的输入/输出契约（PO → BA → Architect → Coder → Reviewer → QA → Orchestrator）
- 每个角色的交接物清单（如 BA 产出 Spec、AC 列表）
- 交接失败处理规则（打回机制、修复轮次上限、熔断阈值）

验证：文件存在，Markdown 格式正确

### Step 3: 创建 `flow-level-rules.md`

文件：`skills/sdd/shared/flow-level-rules.md`

参考：Design §2.1.2（流程级别判定规则）

内容要点：
- Quick / Standard / Enhanced 三级定义
- 判定逻辑：用伪代码描述 `determine_flow_level(change_description)` 的输入输出
- 每级包含的阶段清单和跳过规则

### Step 4: 创建 `convention-overrides.md`

文件：`skills/sdd/shared/convention-overrides.md`

参考：Design §3.4（规则覆盖机制）

内容要点：
- 可覆盖的约定清单（R1-R10 中哪些可通过 AGENTS.md 禁用/自定义）
- 覆盖语法：`disable_rules` 和 `custom_rules` 的 YAML 格式
- 示例：无前端项目禁用 R5、金融项目新增风控规则

### Step 5: 创建 `sdd-rules.md`

文件：`skills/sdd/shared/sdd-rules.md`

参考：Design §三.2（规则定义 R1-R10）

内容要点：
- 逐条列出 R1-R10，每条包含：编号、名称、描述、触发时机、执行者、检查方式、违反处理、Quick 豁免标记
- R9 使用 V2.1 更新版（目标环境通过原则 + CI-only 机制）
- 格式：每条规则用 `### R{n}: {名称}` 标题

验证：
```bash
grep -c "^### R" skills/sdd/shared/sdd-rules.md
# 期望输出: 10
```

### Step 6: Commit

```bash
git add skills/sdd/shared/
git commit -m "feat(sdd): T1 创建 shared 共享文件（handoff-protocol, flow-level-rules, convention-overrides, sdd-rules）"
```

---

## T2: sdd-structure-lint

**估时**：45min
**依赖**：T1
**产出**：`skills/sdd/sdd-structure-lint/SKILL.md`

### Step 1: 创建目录

```bash
mkdir -p skills/sdd/sdd-structure-lint
```

### Step 2: 创建 SKILL.md

文件：`skills/sdd/sdd-structure-lint/SKILL.md`

参考：Design §2.2（sdd-structure-lint 详细设计）

内容要点：
- YAML frontmatter：`name: sdd-structure-lint`, `description: 三级合规验证...`
- 三级验证定义：
  - **文件级**：必选文件是否存在（AGENTS.md, CONSTITUTION.md, QUIRKS.md, docs/ 目录结构）
  - **交接级**：当前阶段必选产物是否存在（spec.md, design.md, tasks.md 等）
  - **内容级**：AC 编号格式、Tasks 表格格式、review-report 字段完整性
- 每级的检查逻辑用伪代码描述
- 错误报告格式（标准化的 Markdown 报告模板）

验证：
```bash
python3 -c "
import yaml
with open('skills/sdd/sdd-structure-lint/SKILL.md') as f:
    content = f.read()
    parts = content.split('---')
    assert len(parts) >= 3, 'Missing YAML frontmatter'
    fm = yaml.safe_load(parts[1])
    assert fm['name'] == 'sdd-structure-lint'
    print('✓ YAML frontmatter valid')
"
```

### Step 3: Commit

```bash
git add skills/sdd/sdd-structure-lint/
git commit -m "feat(sdd): T2 创建 sdd-structure-lint（三级合规验证）"
```

---

## T3: sdd-init

**估时**：1.5h
**依赖**：T2
**AC 覆盖**：AC1-5
**产出**：`skills/sdd/sdd-init/SKILL.md` + 项目模板

> 说明：T3 创建的模板文件（templates/）是**项目模板**，由 sdd-init 在目标项目初始化时拷贝生成。它们不是 Skill 的 reference 文件，而是供 sdd-init 使用的脚手架文件。

### Step 1: 创建目录

```bash
mkdir -p skills/sdd/sdd-init/templates
```

### Step 2: 创建 AGENTS.md 模板

文件：`skills/sdd/sdd-init/templates/agnets-template.md`（注意文件名保留 typo，与 Design 一致）

参考：Design §2.3 Step A2.1 + §五（AGENTS.md 字段解析规范）

验证：
```bash
grep -c "^## " skills/sdd/sdd-init/templates/agnets-template.md
# 至少包含: 项目信息, 技术栈, 路径约定, SDD 配置, 项目约束, 自定义覆盖
```

### Step 3: 创建 CONSTITUTION.md 模板

文件：`skills/sdd/sdd-init/templates/constitution-template.md`

参考：Design §2.3 Step A2.2

### Step 4: 创建 QUIRKS.md 模板

文件：`skills/sdd/sdd-init/templates/quirks-template.md`

参考：Design §2.3 Step A2.3

### Step 5: 创建 sdd-init SKILL.md

文件：`skills/sdd/sdd-init/SKILL.md`

参考：Design §2.3（sdd-init 完整设计）

内容要点：
- 两种模式：初始化（Step A1-A4）和升级（Step B1-B4）
- Step A2 包含 6 个子步骤（含 A2.4a pytest.ini）
- Step B1 包含 10 个检测项
- Python 代码示例（正则解析 AGENTS.md、文件检测等）
- 模板文件引用：使用 skill_view 加载 `templates/` 下的文件

验证：
```bash
python3 -c "
import yaml
with open('skills/sdd/sdd-init/SKILL.md') as f:
    parts = f.read().split('---')
    fm = yaml.safe_load(parts[1])
    assert fm['name'] == 'sdd-init'
    print('✓ valid')
"
```

### Step 6: Commit

```bash
git add skills/sdd/sdd-init/
git commit -m "feat(sdd): T3 创建 sdd-init（项目初始化与升级 + 项目模板）"
```

---

## T4: po-agent

**估时**：45min
**依赖**：T1
**AC 覆盖**：AC10, AC18
**产出**：`skills/sdd/po-agent/SKILL.md` + `references/prd-template.md`

### Step 1: 创建目录

```bash
mkdir -p skills/sdd/po-agent/references
```

### Step 2: 创建 prd-template.md

文件：`skills/sdd/po-agent/references/prd-template.md`

参考：Design §2.5（PO Agent 设计）

验证：
```bash
grep -E "^## (背景与目标|用户场景|功能范围|非功能需求|验收标准|风险与假设)" \
  skills/sdd/po-agent/references/prd-template.md | wc -l
# 期望: 6
```

### Step 3: 创建 SKILL.md

文件：`skills/sdd/po-agent/SKILL.md`

参考：Design §2.5

验证：
```bash
grep "prd-template" skills/sdd/po-agent/SKILL.md
# 期望: 至少一处引用
```

### Step 4: Commit

```bash
git add skills/sdd/po-agent/
git commit -m "feat(sdd): T4 创建 po-agent（PO Agent + PRD 模板）"
```

---

## T5: ba-agent

**估时**：45min
**依赖**：T1
**AC 覆盖**：AC11, AC19
**产出**：`skills/sdd/ba-agent/SKILL.md` + 2 个 references

### Step 1: 创建目录

```bash
mkdir -p skills/sdd/ba-agent/references
```

### Step 2: 创建 spec-template.md

文件：`skills/sdd/ba-agent/references/spec-template.md`

参考：Design §2.6

### Step 3: 创建 ac-writing-guide.md

文件：`skills/sdd/ba-agent/references/ac-writing-guide.md`

参考：Design §2.6

验证：
```bash
grep -E "(Given|When|Then|可测试|可量化)" \
  skills/sdd/ba-agent/references/ac-writing-guide.md | wc -l
# 期望: >= 4
```

### Step 4: 创建 SKILL.md

文件：`skills/sdd/ba-agent/SKILL.md`

参考：Design §2.6

### Step 5: Commit

```bash
git add skills/sdd/ba-agent/
git commit -m "feat(sdd): T5 创建 ba-agent（BA Agent + Spec 模板 + AC 指南）"
```

---

## T6: architect-agent

**估时**：1h
**依赖**：T1
**AC 覆盖**：AC20
**产出**：`skills/sdd/architect-agent/SKILL.md` + 4 个 references

### Step 1: 创建目录

```bash
mkdir -p skills/sdd/architect-agent/references
```

### Step 2: 创建 4 个 reference 文件

按 Design §2.7，全部放在 `skills/sdd/architect-agent/references/`：
1. `design-template.md`
2. `tasks-template.md`
3. `brainstorming-guide.md`
4. `handoff-to-coder.md`

### Step 3: 创建 SKILL.md

文件：`skills/sdd/architect-agent/SKILL.md`

参考：Design §2.7

### Step 4: Commit

```bash
git add skills/sdd/architect-agent/
git commit -m "feat(sdd): T6 创建 architect-agent（架构师 + 4 references）"
```

---

## T7: coder-agent

**估时**：45min
**依赖**：T1
**AC 覆盖**：AC21
**产出**：`skills/sdd/coder-agent/SKILL.md` + 4 个 references

### Step 1: 创建目录

```bash
mkdir -p skills/sdd/coder-agent/references
```

### Step 2: 创建 4 个 reference 文件

按 Design §2.8，全部放在 `skills/sdd/coder-agent/references/`：
1. `tdd-workflow.md`
2. `nfr-checklist.md`
3. `task-completion-report-template.md`
4. `convention-checklist.md`

### Step 3: 创建 SKILL.md

文件：`skills/sdd/coder-agent/SKILL.md`

参考：Design §2.8

### Step 4: Commit

```bash
git add skills/sdd/coder-agent/
git commit -m "feat(sdd): T7 创建 coder-agent（开发者 + TDD/NFR/模板）"
```

---

## T8: reviewer-agent

**估时**：45min
**依赖**：T1
**AC 覆盖**：AC22
**产出**：`skills/sdd/reviewer-agent/SKILL.md` + 2 个 references

### Step 1: 创建目录

```bash
mkdir -p skills/sdd/reviewer-agent/references
```

### Step 2: 创建 review-checklist.md

文件：`skills/sdd/reviewer-agent/references/review-checklist.md`

参考：Design §2.9

### Step 3: 创建 severity-guide.md

文件：`skills/sdd/reviewer-agent/references/severity-guide.md`

参考：Design §2.9

### Step 4: 创建 SKILL.md

文件：`skills/sdd/reviewer-agent/SKILL.md`

参考：Design §2.9

### Step 5: Commit

```bash
git add skills/sdd/reviewer-agent/
git commit -m "feat(sdd): T8 创建 reviewer-agent（审查员 + checklist + severity）"
```

---

## T9: qa-agent

**估时**：45min
**依赖**：T1
**AC 覆盖**：AC23
**产出**：`skills/sdd/qa-agent/SKILL.md` + 4 个 references

### Step 1: 创建目录

```bash
mkdir -p skills/sdd/qa-agent/references
```

### Step 2: 创建 4 个 reference 文件

按 Design §2.10，全部放在 `skills/sdd/qa-agent/references/`：
1. `qa-report-template.md`
2. `e2e-ac-mapping-template.md`
3. `circuit-breaker.md`
4. `ci-only-guide.md`（新增：CI-only 测试标记规范）

**ci-only-guide.md 内容要点**：
- pytest marker 使用方式：`@pytest.mark.ci_only`
- 原因注释格式：`# CI_ONLY: 需要 Docker 环境运行 PostgreSQL`
- 环境变量约定：CI 环境设置 `CI=true`
- conftest.py 自动 skip 逻辑说明
- 常见 CI-only 场景：数据库集成测试、E2E 测试、GPU 测试、长时间运行测试

### Step 3: 创建 SKILL.md

文件：`skills/sdd/qa-agent/SKILL.md`

参考：Design §2.10

### Step 4: Commit

```bash
git add skills/sdd/qa-agent/
git commit -m "feat(sdd): T9 创建 qa-agent（QA 工程师 + 报告模板 + CI-only 指南）"
```

---

## T10: sdd-orchestrator

**估时**：2h
**依赖**：T2-T9
**AC 覆盖**：AC6-17, AC28-29
**产出**：`skills/sdd/sdd-orchestrator/SKILL.md`

### Step 1: 创建目录

```bash
mkdir -p skills/sdd/sdd-orchestrator
```

### Step 2: 创建 SKILL.md

文件：`skills/sdd/sdd-orchestrator/SKILL.md`

参考：Design §2.1（编排器完整设计）

必须覆盖的内容模块：
- 流程判定（引用 `shared/flow-level-rules.md`）
- 角色调度（PO → BA → Architect → Coder → Reviewer → QA）
- 门禁检查（调用 sdd-structure-lint）
- 归档流程（changes/ → archive/）
- 中断恢复（`.sdd-state.json`）

验证：
```bash
grep -cE "流程判定|角色调度|门禁检查|归档流程|中断恢复" \
  skills/sdd/sdd-orchestrator/SKILL.md
# 期望: 5
```

### Step 3: Commit

```bash
git add skills/sdd/sdd-orchestrator/
git commit -m "feat(sdd): T10 创建 sdd-orchestrator（编排器：流程判定+调度+门禁+归档）"
```

---

## T11: AILP 适配验证

**估时**：1h
**依赖**：T10
**AC 覆盖**：全部
**产出**：验证报告 + 精简后的 AILP AGENTS.md（存于 hermes-sdd 项目内作为参考）

### Step 1: 精简 AILP 的 AGENTS.md

在 AILP 项目中按模板格式创建/更新 AGENTS.md，作为部署验证：

```bash
# 生成到 AILP 项目，验证 sdd-init 模板能正常工作
```

### Step 2: 走一次 Quick 流程验证

用 sdd-orchestrator 对 AILP 发起一个 Quick 变更，验证编排器完整流程。

### Step 3: 写入验证报告

文件：`docs/changes/001-sdd-init/verification-report.md`

### Step 4: Commit

```bash
git add docs/changes/001-sdd-init/verification-report.md
git commit -m "docs(sdd): T11 AILP 适配验证报告"
```

---

## T12: 部署发布

**估时**：30min
**依赖**：T11
**产出**：所有文件从 `skills/sdd/` 拷贝到 `~/.hermes/skills/sdd/` + sdd-structure-lint 全量验证

### Step 1: 确认 Git 状态干净

```bash
git status
# 期望: nothing to commit, working tree clean
```

### Step 2: 部署到正式路径

```bash
# 确保目标目录存在
mkdir -p ~/.hermes/skills/sdd

# 拷贝所有 Skill 文件（覆盖）
cp -r skills/sdd/* ~/.hermes/skills/sdd/

# 验证部署完整性
echo "=== 部署后的文件列表 ==="
find ~/.hermes/skills/sdd -type f | sort
```

### Step 3: 验证部署后可加载

```bash
# 检查关键 Skill 文件存在
python3 -c "
import os
sd = os.path.expanduser('~/.hermes/skills/sdd')
required = [
    'shared/sdd-rules.md',
    'shared/handoff-protocol.md',
    'sdd-orchestrator/SKILL.md',
    'sdd-init/SKILL.md',
    'sdd-structure-lint/SKILL.md',
    'po-agent/SKILL.md',
    'ba-agent/SKILL.md',
    'architect-agent/SKILL.md',
    'coder-agent/SKILL.md',
    'reviewer-agent/SKILL.md',
    'qa-agent/SKILL.md',
]
for f in required:
    path = os.path.join(sd, f)
    assert os.path.exists(path), f'MISSING: {f}'
    print(f'✓ {f}')
print('文件完整性验证通过')
"
```

### Step 4: 用 sdd-structure-lint 全量自动化验证

```bash
# 此时 sdd-structure-lint 已在正式路径可用
# 加载 skill 并对 hermes-sdd 项目自身执行三级验证
echo ">>> 对 hermes-sdd 项目自身执行 sdd-structure-lint 全量验证 <<<"
# 验证要点（由 Agent 加载 sdd-structure-lint skill 后执行）：
#   (1) 文件级: AGENTS.md, CONSTITUTION.md, QUIRKS.md, docs/ 目录
#   (2) 交接级: ~/.hermes/skills/sdd/ 下所有 Skill 的 SKILL.md + references 完整性
#   (3) 内容级: YAML frontmatter 合法性、AC 编号格式
# 期望：全量通过，无错误
```

### Step 5: Tag 并推送

```bash
git tag v1.0.0 -m "SDD 通用开发机制 v1.0: 7 角色 + 编排器 + 12 规则 + hooks"
git push origin main --tags
```

---

## 汇总

| # | Task | 估时 | 产出路径 | 文件数 |
|---|------|:---:|---------|:---:|
| T1 | shared 共享文件 | 45min | `skills/sdd/shared/` | 4 |
| T2 | sdd-structure-lint | 45min | `skills/sdd/sdd-structure-lint/` | 1 |
| T3 | sdd-init + 模板 | 1.5h | `skills/sdd/sdd-init/` | 4 |
| T4 | po-agent | 45min | `skills/sdd/po-agent/` | 2 |
| T5 | ba-agent | 45min | `skills/sdd/ba-agent/` | 3 |
| T6 | architect-agent | 1h | `skills/sdd/architect-agent/` | 5 |
| T7 | coder-agent | 45min | `skills/sdd/coder-agent/` | 5 |
| T8 | reviewer-agent | 45min | `skills/sdd/reviewer-agent/` | 3 |
| T9 | qa-agent | 45min | `skills/sdd/qa-agent/` | 5 |
| T10 | sdd-orchestrator | 2h | `skills/sdd/sdd-orchestrator/` | 1 |
| T11 | AILP 适配验证 | 1h | `docs/changes/001-sdd-init/` | 2 |
| T12 | 部署发布 | 30min | 拷贝至 `~/.hermes/skills/sdd/` + lint 验证 | — |
| **总计** | | **11.75h** | | **35** |

### 路径对照

```
开发路径（项目内）                    部署目标路径
─────────────────────────────────    ─────────────────────────────────
skills/sdd/shared/                 → ~/.hermes/skills/sdd/shared/
skills/sdd/sdd-structure-lint/     → ~/.hermes/skills/sdd/sdd-structure-lint/
skills/sdd/sdd-init/               → ~/.hermes/skills/sdd/sdd-init/
  └── templates/  (项目模板)        → 不直接部署，由 sdd-init 在目标项目生成
skills/sdd/sdd-orchestrator/       → ~/.hermes/skills/sdd/sdd-orchestrator/
skills/sdd/po-agent/               → ~/.hermes/skills/sdd/po-agent/
skills/sdd/ba-agent/               → ~/.hermes/skills/sdd/ba-agent/
skills/sdd/architect-agent/        → ~/.hermes/skills/sdd/architect-agent/
skills/sdd/coder-agent/            → ~/.hermes/skills/sdd/coder-agent/
skills/sdd/reviewer-agent/         → ~/.hermes/skills/sdd/reviewer-agent/
skills/sdd/qa-agent/               → ~/.hermes/skills/sdd/qa-agent/
```
