# Tasks: Hermes Harness 项目上手体验

> 版本：V1.0
> 日期：2026-05-25
> 前置 Design：`design.md`
> 估时：64 分钟

---

## 执行约定

1. **工作目录**：`/root/workspace/hermes-harness`
2. **每 Task 完成后**：commit，格式 `feat(onboarding): T{N} {描述}`
3. **验证方式**：文件存在性检查 + 内容关键词检查 + sdd-init 回归

---

## Task 执行顺序

```
T1 ─┐
T2 ─┤  并行
T3 ─┘
     ↓
    T4（模板文件就绪）
     ↓
    T5（sdd-init 引用 T4）
     ↓
    T6（验证 + 回归）
     ↓
    T7（最终检查 + commit）
```

---

## T1: README.md — 项目门面

**估时**：10min
**依赖**：无
**AC 覆盖**：AC1, AC2, AC13
**产出**：`README.md`

### Step 1: 创建 README.md

写入以下内容到 `/root/workspace/hermes-harness/README.md`：

```markdown
# Hermes Harness

> 通用 SDD（Spec-Driven Development）开发框架 — 让 AI Agent 按工程规范协作

## 解决什么问题

AI Agent 写代码很快，但**写完就忘、质量不稳、流程不透明**。SDD 把人类的软件工程规范（需求→规格→设计→任务→实现→评审→测试→验收）编码为 Agent 可执行的 Skill 流程，让 Agent 像工程团队一样工作。

## SDD 流程

```mermaid
graph LR
    PO[PO: 需求定义] --> BA[BA: Spec+AC]
    BA --> AR[Architect: 设计+Task]
    AR --> CO[Coder: TDD实现]
    CO --> RE[Reviewer: 三阶段评审]
    RE --> QA[QA: 测试验证]
    QA --> UA[用户验收]
    UA --> ARV[归档]
```

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/NEU-JING/hermes-harness.git
cd hermes-harness

# 2. 安装 Skills 到本地 Hermes Agent
./install.sh

# 3. 在你的项目中初始化 SDD
cd /path/to/your-project
# 对 Hermes Agent 说："初始化 SDD"
```

## 文档

| 文档 | 说明 |
|------|------|
| [安装指南](INSTALL.md) | 详细安装步骤、卸载、升级 |
| [项目模板](templates/) | 接入 SDD 的项目需要的模板文件 |
| [SDD 规则](skills/sdd/shared/sdd-rules.md) | 10 条通用规则定义 |

## 要求

- Hermes Agent >= v2.0
```

### Step 2: 验证

```bash
# 文件存在
test -f README.md && echo "✓" || echo "✗"

# 首屏关键词
head -20 README.md | grep -q "Hermes Harness" && echo "✓" || echo "✗"
head -20 README.md | grep -q "mermaid" && echo "✓" || echo "✗"
head -20 README.md | grep -q "快速开始" && echo "✓" || echo "✗"

# 链接存在
grep -q "INSTALL.md" README.md && echo "✓" || echo "✗"
grep -q "templates/" README.md && echo "✓" || echo "✗"
```

### Step 3: Commit

```bash
git add README.md
git commit -m "feat(onboarding): T1 README — 项目门面，含 SDD 流程图和快速开始"
```

---

## T2: INSTALL.md — 安装指南

**估时**：8min
**依赖**：无
**AC 覆盖**：AC3, AC4
**产出**：`INSTALL.md`

### Step 1: 创建 INSTALL.md

写入到 `/root/workspace/hermes-harness/INSTALL.md`：

```markdown
# 安装指南

## 前置条件

- **Hermes Agent >= v2.0**：确认方法：终端输入 `hermes --version`

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/NEU-JING/hermes-harness.git
cd hermes-harness
```

### 2. 运行安装脚本

```bash
./install.sh
```

脚本会将 `skills/sdd/` 目录复制到 `~/.hermes/skills/sdd/`。

### 3. 验证安装

```bash
ls ~/.hermes/skills/sdd/
```

预期输出：

```
architect-agent  ba-agent  coder-agent  po-agent  qa-agent
reviewer-agent   sdd-init  sdd-orchestrator  sdd-structure-lint  shared
```

### 4. 初始化你的项目

```bash
cd /path/to/your-project
# 对 Hermes Agent 说："初始化 SDD"
```

## 卸载

```bash
rm -rf ~/.hermes/skills/sdd/
```

## 升级

```bash
cd hermes-harness
git pull
./install.sh
```

> install.sh 幂等：已有安装时会提示跳过，不会自动覆盖。如需强制重装请先卸载。

## 常见问题

**Q: 安装后 Hermes Agent 不识别 Skill？**
A: 检查 `~/.hermes/config.yaml` 中 `skills_dir` 是否指向 `~/.hermes/skills`。新会话重启生效。

**Q: install.sh 提示"已有安装"？**
A: 你之前装过。如需重装：`rm -rf ~/.hermes/skills/sdd/ && ./install.sh`
```

### Step 2: 验证

```bash
test -f INSTALL.md && echo "✓" || echo "✗"
grep -q "Hermes Agent >= v2.0" INSTALL.md && echo "✓" || echo "✗"
grep -q "./install.sh" INSTALL.md && echo "✓" || echo "✗"
grep -q "卸载" INSTALL.md && echo "✓" || echo "✗"
```

### Step 3: Commit

```bash
git add INSTALL.md
git commit -m "feat(onboarding): T2 INSTALL — 安装指南含前置条件/步骤/卸载/FAQ"
```

---

## T3: install.sh — 一键安装脚本

**估时**：8min
**依赖**：无
**AC 覆盖**：AC4, AC5
**产出**：`install.sh`

### Step 1: 创建 install.sh

写入到 `/root/workspace/hermes-harness/install.sh`：

```bash
#!/bin/bash
set -euo pipefail

TARGET="$HOME/.hermes/skills/sdd"
SOURCE="$(dirname "$(readlink -f "$0")")/skills/sdd"

echo "==> Hermes Harness SDD Skills 安装"

# 检测已有安装
if [ -d "$TARGET" ]; then
    echo "⚠️  检测到已有安装: $TARGET"
    echo ""
    echo "   当前已安装的 Skills:"
    ls "$TARGET/"*/SKILL.md 2>/dev/null | sed 's|.*/||;s|/.*||' | sort | while read skill; do
        echo "     - $skill"
    done
    echo ""
    echo "   如需覆盖安装，请先卸载: rm -rf $TARGET"
    echo "   然后重新运行: ./install.sh"
    exit 0
fi

# 创建目标目录
mkdir -p "$(dirname "$TARGET")"

# 安装 Skills
cp -r "$SOURCE" "$TARGET"

# 验证
echo ""
echo "✅ 安装完成。已安装的 Skills:"
ls "$TARGET/"*/SKILL.md 2>/dev/null | sed 's|.*/skills/sdd/||;s|/SKILL.md||' | sort | while read skill; do
    echo "   - $skill"
done

echo ""
echo "下一步: cd /path/to/your-project && 对 Hermes Agent 说 '初始化 SDD'"
```

### Step 2: 添加执行权限 + 验证

```bash
chmod +x install.sh

# 语法检查
bash -n install.sh && echo "✓ syntax" || echo "✗ syntax"

# 幂等测试：执行两次
./install.sh
./install.sh 2>&1 | grep -q "已有安装" && echo "✓ idempotent" || echo "✗ not idempotent"

# 清理测试安装（保留用于后续验证）
# rm -rf ~/.hermes/skills/sdd/
```

### Step 3: Commit

```bash
git add install.sh
git commit -m "feat(onboarding): T3 install.sh — 一键安装脚本，幂等设计"
```

---

## T4: templates/ 目录 — 6 个模板文件

**估时**：15min
**依赖**：无（T1-T3 并行完成后执行）
**AC 覆盖**：AC6, AC7, AC8
**产出**：`templates/` 目录下 6 个文件

### Step 1: 创建目录

```bash
mkdir -p /root/workspace/hermes-harness/templates
```

### Step 2: 创建 templates/AGENTS.md

内容同旧 `skills/sdd/sdd-init/templates/agnets-template.md`，但：
- 文件名修正为 `AGENTS.md`
- 顶部添加模板说明注释

写入 `/root/workspace/hermes-harness/templates/AGENTS.md`：

```markdown
# 模板: AGENTS.md
# 用途: 将此文件复制到项目根目录，替换 {...} 占位符后作为项目 SDD 配置
# 占位符: {project_name} = 项目名称, {一句话描述} = 项目简介
#         {Python/FastAPI / Go / ...} = 后端技术栈（选一个）
#         {React/TypeScript / Vue / 无} = 前端技术栈
#         {PostgreSQL / SQLite / ...} = 数据库

# AGENTS.md — {project_name}

## 项目信息
- name: "{project_name}"
- description: "{一句话描述}"
- repo: "TBD"

## 技术栈
- backend: "{Python/FastAPI / Go / Java}"
- frontend: "{React/TypeScript / Vue / 无}"
- database: "{PostgreSQL / SQLite / MongoDB}"

## 路径约定
- changes_dir: "docs/changes/"
- current_dir: "docs/current/"
- archive_dir: "docs/archive/"
- backend_dir: "backend/"
- frontend_dir: "frontend/"  (如无前端，删除此行)

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

### Step 3: 创建 templates/CONSTITUTION.md

内容同旧 `skills/sdd/sdd-init/templates/constitution-template.md`，加模板注释和项目特有约束示例。

写入 `/root/workspace/hermes-harness/templates/CONSTITUTION.md`：

```markdown
# 模板: CONSTITUTION.md
# 用途: 定义项目不可违背的核心原则。占位符 {project_name} 替换为实际项目名。

# CONSTITUTION.md — {project_name}

> 项目宪法：定义不可违背的核心原则。SDD 编排器在每个阶段检查合规性。

---

## 代码原则

1. **TDD 强制**：所有功能代码必须先写测试（R3，不可禁用）
2. **测试自包含**：测试不依赖预置数据或外部状态（R6，不可禁用）
3. **Pre-commit 强制**：push 前必须通过 format + lint（R8，不可禁用）

---

## 架构原则

1. **简洁优先**：能用简单方案解决的不引入复杂方案（YAGNI）
2. **模块化**：每模块职责单一，接口清晰
3. **可测试性**：所有模块设计时考虑可测试性

---

## 协作原则

1. **文档驱动**：先写 Spec，再写代码（R1）
2. **评审必做**：代码合并前必须经过 Review（R4）
3. **增量提交**：小步提交，每 commit 可独立 review

---

## 项目特有约束

<!-- 在此添加项目专属的不可违背约束。示例： -->
<!-- - 禁止使用 ORM 的 raw SQL -->
<!-- - API 响应必须使用统一格式 { "code": 0, "data": ... } -->
<!-- - 数据库迁移必须有 rollback -->
<!-- - Phase 3-6 数据使用 create_only 行为，不可被种子数据覆盖 -->
```

### Step 4: 创建 templates/QUIRKS.md

从 `skills/sdd/sdd-init/templates/quirks-template.md` 复制并加模板注释。

写入 `/root/workspace/hermes-harness/templates/QUIRKS.md`：

```markdown
# 模板: QUIRKS.md
# 用途: 记录项目开发过程中的陷阱和怪癖，随开发过程持续更新。
# 占位符: {project_name} = 项目名称, {陷阱名称} = 具体陷阱名

# QUIRKS.md — {project_name}

> 项目陷阱与怪癖记录。随着开发过程持续更新，避免踩同样的坑。

---

## 已知陷阱

### {陷阱名称}

**现象**：

**原因**：

**修复方式**：

**预防措施**：

---

## 环境怪癖

| 怪癖 | 影响 | 处理方式 |
|------|------|---------|
| | | |

---

## 工具链注意事项

| 工具 | 版本 | 注意事项 |
|------|------|---------|
| | | |

---

## 更新规则

- 每发现一个新陷阱 → 添加到本文档
- 每修复一个陷阱 → 更新状态（✓ 已修复）
- post-commit hook 自动检测本次 commit 是否修复了陷阱 → 提示更新 QUIRKS.md
```

### Step 5: 创建 templates/.pre-commit-config.yaml

从 sdd-init SKILL.md L69-100 提取 YAML 内容。

写入 `/root/workspace/hermes-harness/templates/.pre-commit-config.yaml`：

```yaml
# 模板: .pre-commit-config.yaml
# 用途: 项目 pre-commit 检查配置。Python 项目直接使用；
#       Go/前端项目替换 hooks 为对应工具。

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

### Step 6: 创建 templates/pytest.ini

从 sdd-init SKILL.md L118-122 提取。

写入 `/root/workspace/hermes-harness/templates/pytest.ini`：

```ini
# 模板: pytest.ini
# 用途: 注册 ci_only marker，配合 conftest.py 自动跳过 CI-only 测试。

[pytest]
markers =
    ci_only: 仅在 CI 环境中运行的测试（需要 Docker/GPU/大内存等资源）
```

### Step 7: 创建 templates/conftest.py

从 sdd-init SKILL.md L125-143 提取。

写入 `/root/workspace/hermes-harness/templates/conftest.py`：

```python
# 模板: conftest.py
# 用途: 自动跳过 CI-only 测试（本地开发时），CI 环境正常运行。
# 依赖: pytest.ini 中已注册 ci_only marker。

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

### Step 8: 删除旧文件（拼写修正）

```bash
# 删除拼写错误的旧模板
rm /root/workspace/hermes-harness/skills/sdd/sdd-init/templates/agnets-template.md
```

### Step 9: 验证

```bash
# 6 个文件存在
expected="AGENTS.md CONSTITUTION.md QUIRKS.md .pre-commit-config.yaml pytest.ini conftest.py"
for f in $expected; do
    test -f "templates/$f" && echo "✓ $f" || echo "✗ $f"
done

# 旧拼写错误文件已删除
test ! -f skills/sdd/sdd-init/templates/agnets-template.md && echo "✓ agnets removed" || echo "✗ agnets still exists"

# 模板文件含注释
grep -q "模板:" templates/AGENTS.md && echo "✓ AGENTS.md has template comment" || echo "✗"
grep -q "模板:" templates/.pre-commit-config.yaml && echo "✓ pre-commit has template comment" || echo "✗"
```

### Step 10: Commit

```bash
git add templates/
git rm skills/sdd/sdd-init/templates/agnets-template.md 2>/dev/null || true
git commit -m "feat(onboarding): T4 templates/ — 6个模板文件 + 拼写修正 agnets→agents"
```

---

## T5: sdd-init SKILL.md 引用更新

**估时**：10min
**依赖**：T4（templates/ 文件就绪）
**AC 覆盖**：AC9, AC10, AC12
**产出**：修改 `skills/sdd/sdd-init/SKILL.md`

### Step 1: 修改 Step A2.1 — AGENTS.md 读取方式

将 SKILL.md L57 的：
```
使用 `skill_view(name='sdd-init', file_path='templates/agnets-template.md')` 加载模板
```
改为：
```
使用 `read_file(path='../../templates/AGENTS.md')` 读取模板文件，
替换占位符 {project_name} 等，写入项目根目录。
```

### Step 2: 修改 Step A2.2 — CONSTITUTION.md

L61：
```
使用 `skill_view(name='sdd-init', file_path='templates/constitution-template.md')` 加载模板
```
改为：
```
使用 `read_file(path='../../templates/CONSTITUTION.md')` 读取模板文件，写入项目根目录。
```

### Step 3: 修改 Step A2.3 — QUIRKS.md

L65：
```
使用 `skill_view(name='sdd-init', file_path='templates/quirks-template.md')` 加载模板
```
改为：
```
使用 `read_file(path='../../templates/QUIRKS.md')` 读取模板文件，写入项目根目录。
```

### Step 4: 修改 Step A2.4 — .pre-commit-config.yaml

将 L67-107（整个 YAML 代码块 + 自适应逻辑）替换为：
```markdown
#### Step A2.4: 生成 .pre-commit-config.yaml

使用 `read_file(path='../../templates/.pre-commit-config.yaml')` 读取模板，写入项目根目录。

**自适应逻辑**：
- Python 项目 → 直接使用模板
- Go 项目 → golangci-lint + gofmt（手动替换 hooks）
- 前端项目 → eslint + prettier（手动替换 hooks）
- 混合项目 → 合并

**冲突处理**：`.pre-commit-config.yaml` 已存在 → 不覆盖，输出提示
```

### Step 5: 修改 Step A2.4a — pytest.ini + conftest.py

将 L115-143（pytest.ini 和 conftest.py 内嵌代码块）替换为：
```markdown
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
```

### Step 6: 验证

```bash
# 确认内嵌 YAML 块已移除
! grep -A5 "repos:" skills/sdd/sdd-init/SKILL.md | grep -q "psf/black" && echo "✓ YAML block removed" || echo "✗ YAML block still present"

# 确认内嵌 Python 块已移除
! grep -q "def pytest_configure" skills/sdd/sdd-init/SKILL.md && echo "✓ Python block removed" || echo "✗ Python block still present"

# 确认引用路径存在
grep -q "../../templates/" skills/sdd/sdd-init/SKILL.md && echo "✓ template refs present" || echo "✗ no template refs"

# sdd-init 语法完整（有 frontmatter）
head -1 skills/sdd/sdd-init/SKILL.md | grep -q "^---$" && echo "✓ frontmatter OK" || echo "✗ frontmatter missing"
```

### Step 7: Commit

```bash
git add skills/sdd/sdd-init/SKILL.md
git commit -m "feat(onboarding): T5 sdd-init 改为引用 templates/ 目录模板文件"
```

---

## T6: 验证 + sdd-init 回归测试

**估时**：8min
**依赖**：T4, T5
**AC 覆盖**：AC10, AC11
**产出**：验证报告

### Step 1: 模拟新项目 sdd-init

```bash
# 创建临时测试项目
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"
git init

# 模拟 sdd-init 读取模板（验证模板文件可读取）
for tmpl in AGENTS.md CONSTITUTION.md QUIRKS.md; do
    if [ -f "/root/workspace/hermes-harness/templates/$tmpl" ]; then
        echo "✓ templates/$tmpl readable"
    else
        echo "✗ templates/$tmpl MISSING"
    fi
done

# 清理
cd /root/workspace/hermes-harness
rm -rf "$TEST_DIR"
```

### Step 2: install.sh 幂等验证

```bash
# 首次安装
./install.sh 2>&1 | grep -q "安装完成" && echo "✓ first install" || echo "✗ first install"

# 重复安装（幂等）
./install.sh 2>&1 | grep -q "已有安装" && echo "✓ idempotent" || echo "✗ not idempotent"
```

### Step 3: 文件完整性检查

```bash
echo "=== 新增文件 ==="
for f in README.md INSTALL.md install.sh; do
    test -f "$f" && echo "✓ $f" || echo "✗ $f"
done

echo "=== 模板文件 ==="
for f in AGENTS.md CONSTITUTION.md QUIRKS.md .pre-commit-config.yaml pytest.ini conftest.py; do
    test -f "templates/$f" && echo "✓ templates/$f" || echo "✗ templates/$f"
done

echo "=== 旧文件清理 ==="
test ! -f skills/sdd/sdd-init/templates/agnets-template.md && echo "✓ agnets removed" || echo "✗ agnets still exists"

echo "=== sdd-init 更新 ==="
grep -q "../../templates/" skills/sdd/sdd-init/SKILL.md && echo "✓ sdd-init references templates/" || echo "✗"
! grep -q "def pytest_configure" skills/sdd/sdd-init/SKILL.md && echo "✓ inline code removed" || echo "✗ inline code still present"
```

### Step 4: Commit

```bash
git add -A
git diff --cached --stat
git commit -m "feat(onboarding): T6 验证报告 — 文件完整性 + 安装幂等 + 模板可读"
```

---

## T7: 最终检查 + 全部 commit 推送

**估时**：5min
**依赖**：T6
**AC 覆盖**：AC13
**产出**：推送所有 commit 到 GitHub

### Step 1: 最终检查清单

```bash
echo "=== SDD Structure Check ==="
test -f README.md && echo "✓ README.md"
test -f INSTALL.md && echo "✓ INSTALL.md"
test -f install.sh && echo "✓ install.sh"
test -d templates/ && echo "✓ templates/"
test -f templates/AGENTS.md && echo "✓ templates/AGENTS.md"
test -f templates/CONSTITUTION.md && echo "✓ templates/CONSTITUTION.md"
test -f templates/QUIRKS.md && echo "✓ templates/QUIRKS.md"
test -f templates/.pre-commit-config.yaml && echo "✓ templates/.pre-commit-config.yaml"
test -f templates/pytest.ini && echo "✓ templates/pytest.ini"
test -f templates/conftest.py && echo "✓ templates/conftest.py"

echo "=== Links Check ==="
grep -q "INSTALL.md" README.md && echo "✓ README → INSTALL" || echo "✗"
grep -q "templates/" README.md && echo "✓ README → templates/" || echo "✗"
grep -q "./install.sh" INSTALL.md && echo "✓ INSTALL → install.sh" || echo "✗"
```

### Step 2: 查看所有 commits

```bash
git log --oneline main..HEAD
# 预期 7 个 commit: T1-T7
```

### Step 3: Push

```bash
git push origin main
```

---

## 汇总

| # | Task | 估时 | 产出文件 | AC 覆盖 |
|---|------|:---:|------|:---:|
| T1 | README.md | 10min | 1 | AC1, AC2, AC13 |
| T2 | INSTALL.md | 8min | 1 | AC3, AC4 |
| T3 | install.sh | 8min | 1 | AC4, AC5 |
| T4 | templates/ 目录 | 15min | 7 (+1 删除) | AC6, AC7, AC8 |
| T5 | sdd-init 引用更新 | 10min | 1 (修改) | AC9, AC10, AC12 |
| T6 | 验证 + 回归 | 8min | 验证报告 | AC10, AC11 |
| T7 | 最终检查 + push | 5min | 推送 | AC13 |
| **总计** | | **64min** | **11 文件** | **13 AC 全覆盖** |
