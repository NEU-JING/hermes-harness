---
name: sdd-init
description: Use when initializing a new project with SDD structure or upgrading an existing project to SDD compliance. Generates AGENTS.md, CONSTITUTION.md, QUIRKS.md, directory structure, pre-commit hooks, and pytest CI-only marker infrastructure.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sdd, init, setup, scaffolding, upgrade]
    related_skills: [sdd-structure-lint, sdd-orchestrator]
    references: []
---

# SDD Init — 项目初始化与升级

## Overview

sdd-init 负责将任意项目接入 SDD 流程。支持两种模式：
- **初始化模式（Step A）**：全新项目，从零生成
- **升级模式（Step B）**：存量项目，检测冲突后增量添加

## When to Use

- 新项目：`sdd-init` → 初始化模式
- 存量项目：`sdd-init --upgrade` → 升级模式
- 用户说 "把这个项目接入 SDD" 或 "初始化 SDD"

**不用此 Skill 的场景**：SDD 结构的日常 lint（用 sdd-structure-lint）

---

## 模式 A：初始化（Init）

### Step A1: 收集项目信息

向用户确认：
1. 项目名称
2. 一句话描述
3. 技术栈（backend / frontend / database）
4. 默认流程级别（Standard / Quick / Enhanced）
5. 是否有前端（影响 R5）

如用户未提供，从项目目录推断：
```python
# 检测后端技术栈
if exists('backend/pyproject.toml'): backend = 'Python/FastAPI'
if exists('backend/go.mod'): backend = 'Go'
# 检测前端
if exists('frontend/package.json'): frontend = 'React/TypeScript'
# 检测数据库
if 'psycopg2' in requirements: database = 'PostgreSQL'
```

### Step A2: 生成文件

#### Step A2.1: 生成 AGENTS.md

使用 `read_file(path='../../templates/AGENTS.md')` 读取模板文件，替换占位符 `{project_name}` 等，写入项目根目录。

#### Step A2.2: 生成 CONSTITUTION.md

使用 `read_file(path='../../templates/CONSTITUTION.md')` 读取模板文件，写入项目根目录。

#### Step A2.3: 生成 QUIRKS.md

使用 `read_file(path='../../templates/QUIRKS.md')` 读取模板文件，写入项目根目录。

#### Step A2.4: 生成 .pre-commit-config.yaml

使用 `read_file(path='../../templates/.pre-commit-config.yaml')` 读取模板，写入项目根目录。

**自适应逻辑**：
- Python 项目 → 直接使用模板
- Go 项目 → golangci-lint + gofmt（手动替换 hooks）
- 前端项目 → eslint + prettier（手动替换 hooks）
- 混合项目 → 合并

**pytest 目录检测**：
- `backend/` 存在 → `cd backend && pytest tests/ -x -q`
- 无 `backend/` → `pytest tests/ -x -q`
- 无 `tests/` → 跳过 pre-push hook

**冲突处理**：`.pre-commit-config.yaml` 已存在 → 不覆盖，输出提示

#### Step A2.4a: 生成 pytest.ini + conftest CI-only 支持（Python 项目）

**pytest.ini**：
使用 `read_file(path='../../templates/pytest.ini')` 读取模板，写入项目根目录。

**conftest.py**：
使用 `read_file(path='../../templates/conftest.py')` 读取模板，写入项目测试目录。

**生成逻辑**：
- Python 项目（有 setup.py/pyproject.toml/tests/）→ 生成
- 非 Python 项目 → 跳过
- pytest.ini 已存在 → 检查是否有 ci_only marker，缺失则追加
- conftest.py 已存在 → 追加 SDD CI-only 块（用 `# SDD: CI-only` 标记），已存在则跳过

#### Step A2.5: 生成 .git/hooks/post-commit

```bash
#!/bin/bash
# SDD post-commit hook — detect trap fixes and prompt QUIRKS.md update

COMMIT_MSG=$(git log -1 --pretty=%B)
QUIRKS_FILE="QUIRKS.md"

if echo "$COMMIT_MSG" | grep -qiE "fix|修复|bug"; then
    if [ -f "$QUIRKS_FILE" ]; then
        echo ""
        echo "🔧 SDD: 本次 commit 包含修复，请检查是否需要更新 QUIRKS.md"
        echo ""
    fi
fi
```

写入 `.git/hooks/post-commit` 并 `chmod +x`。
仅在 `.git/` 存在时执行。

#### Step A2.6: 创建目录结构

```bash
mkdir -p docs/changes docs/current docs/archive
```

### Step A3: 验证

调用 sdd-structure-lint Level 1（文件级检查）：
- AGENTS.md ✓
- CONSTITUTION.md ✓
- QUIRKS.md ✓
- docs/{changes,current,archive}/ ✓

### Step A4: 输出摘要

```markdown
## SDD 初始化完成 ✓

**生成文件**：
- AGENTS.md
- CONSTITUTION.md
- QUIRKS.md
- .pre-commit-config.yaml
- pytest.ini（Python 项目）
- .git/hooks/post-commit

**生成目录**：
- docs/changes/
- docs/current/
- docs/archive/

**下一步**：运行 `pre-commit install` 激活 hooks
```

---

## 模式 B：升级（Upgrade）

### Step B1: 检测现有状态

逐项检测 10 项：

```bash
# 1-6: 基础文件
test -f AGENTS.md && echo "✓" || echo "📁 新建文件"
test -f CONSTITUTION.md && echo "✓" || echo "📁 新建文件"
test -f QUIRKS.md && echo "✓" || echo "📁 新建文件"
test -d docs/changes && echo "✓" || echo "📁 新建目录"
test -d docs/current && echo "✓" || echo "📁 新建目录"
test -d docs/archive && echo "✓" || echo "📁 新建目录"

# 7: pre-commit
test -f .pre-commit-config.yaml && echo "不变文件" || echo "📁 新建文件"

# 8: post-commit hook
test -f .git/hooks/post-commit && echo "检查来源" || echo "📁 新建文件"

# 9: pytest.ini (Python 项目)
# 存在且已有 ci_only → "不变文件" | 存在但无 ci_only → "📝 需更新" | 不存在 → "📁 新建"

# 10: conftest.py SDD 块
grep -q "# SDD: CI-only" conftest.py 2>/dev/null && echo "不变文件" || echo "📝 需更新"
```

### Step B2: 生成升级计划

根据检测结果输出升级计划，标注每项的状态：

```markdown
## SDD 升级计划

| 文件 | 当前状态 | 操作 |
|------|---------|------|
| AGENTS.md | 已存在 | 不变 |
| CONSTITUTION.md | 不存在 | 📁 新建 |
| .pre-commit-config.yaml | 存在，来源非 SDD | ⚠️ 冲突 |
```

### Step B3: 用户确认

将升级计划发送给用户确认。特别关注冲突项（如已有 pre-commit 配置、自定义 post-commit hook）。

### Step B4: 执行升级

按确认后的计划执行：
- 新建文件 → 写入
- 不变文件 → 跳过
- 冲突项 → 按用户选择处理（保留/覆盖/合并）
- 需更新文件 → 追加缺失内容

### Step B5: 验证 + 摘要

同 Step A3-A4。

---

## Post-Init 操作提示

初始化完成后，提醒用户：

```bash
# 激活 git hooks
pre-commit install

# 验证 SDD 结构
# 加载 sdd-structure-lint skill 执行 Level 1 检查
```

## Common Pitfalls

1. **覆盖已有配置**：pre-commit 和 post-commit 可能与其他工具冲突 → 升级模式先检测再处理
2. **非 Python 项目生成 pytest.ini**：Go/前端项目不需要 pytest 配置 → Step A2.4a 检测项目类型
3. **CI-only 块重复追加**：conftest.py 已有 `# SDD: CI-only` 时不再追加
4. **忘记 chmod post-commit**：.git/hooks/post-commit 必须有执行权限
5. **AGENTS.md 占位符未替换**：模板中的 `{project_name}` 等必须替换为实际值
