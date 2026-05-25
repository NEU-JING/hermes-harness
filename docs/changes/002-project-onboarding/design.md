# Design: Hermes Harness 项目上手体验

> 版本：V1.0
> 日期：2026-05-25
> 作者：Architect Agent（基于 [Spec](./spec.md)）

---

## 一、产出物清单

### 新增文件（仓库根目录）

```
hermes-harness/
├── README.md                          ← 新增
├── INSTALL.md                         ← 新增
├── install.sh                         ← 新增
├── templates/                         ← 新增（目录）
│   ├── AGENTS.md
│   ├── CONSTITUTION.md
│   ├── QUIRKS.md
│   ├── .pre-commit-config.yaml
│   ├── pytest.ini
│   └── conftest.py
```

### 修改文件

```
skills/sdd/sdd-init/SKILL.md          ← Step A2.4/A2.4a 引用模板
skills/sdd/sdd-init/templates/        ← 删除 agnets-template.md（拼写修正）
```

### 无需修改

```
skills/sdd/sdd-orchestrator/          ← 不变
skills/sdd/ba-agent/                  ← 不变
skills/sdd/po-agent/                  ← 不变
skills/sdd/architect-agent/           ← 不变
skills/sdd/coder-agent/               ← 不变
skills/sdd/reviewer-agent/            ← 不变
skills/sdd/qa-agent/                  ← 不变
skills/sdd/sdd-structure-lint/        ← 不变
skills/sdd/shared/                    ← 不变
```

**总计**：9 个新文件 + 1 个修改文件 + 1 个删除文件。

---

## 二、技术方案对比（Brainstorming）

### 方案 A：模板双存 — templates/ 为参考，sdd-init 自持副本

**描述**：
- 根目录 `templates/` 存在，但仅作为人类开发者的"配置参考手册"
- sdd-init 保持现状：SKILL.md 中内嵌 .pre-commit-config.yaml / pytest.ini / conftest.py 代码块
- sdd-init/templates/ 保留 agnets-template.md 等文件供 Skill 执行时读取
- 两份模板独立维护，靠人工记忆同步

**优点**：
- 零改动 sdd-init，无回归风险
- 实现最快（只写新文件，不改旧文件）

**缺点**：
- **两份模板必然漂移**：改了一处忘记改另一处 → 内容不一致
- sdd-init 的 SKILL.md 过长（287 行），大量 YAML/INI/Python 内嵌代码块难以维护
- 违反 Spec 的 R5（"模板与 Skill 解耦"）

**适用场景**：临时方案，快速上线后重构

---

### 方案 B：模板单源 — sdd-init 引用根 templates/

**描述**：
- 根目录 `templates/` 为**唯一真相源**
- sdd-init SKILL.md 中将内嵌代码块替换为文件引用指令
- sdd-init/templates/ 旧文件删除，Skill 执行时读取 `../../templates/`（从 skills/sdd/sdd-init/ 向上两级到仓库根）
- 修改模板只需改 `templates/` 一处

**优点**：
- 单一真相源，不会漂移
- sdd-init SKILL.md 大幅精简
- 符合 Spec 的 NFR（"模板与 Skill 解耦"）
- 维护者改模板时无需理解 Skill 内部逻辑

**缺点**：
- 需要改 sdd-init SKILL.md（有回归风险）
- 路径计算：sdd-init 执行时工作目录可能是用户项目，需要 Skill 指令中明确"从 skill 所在目录的相对路径读取模板"

**适用场景**：长期维护的开源项目

---

### 方案对比

| 维度 | 方案 A（双存） | 方案 B（单源） | 权重 |
|------|:---:|:---:|:---:|
| 实现复杂度 | ★☆☆ | ★★☆ | 3 |
| 模板一致性 | ✗（漂移风险） | ✓（单源） | 3 |
| 可维护性 | ★☆☆（287 行 SKILL.md） | ★★★（精简） | 3 |
| 回归风险 | 无 | 低（仅改引用方式） | 2 |
| 团队熟悉度 | — | — | 1 |

**最终选择**：方案 B — 模板单源

**理由**：
1. hermes-harness 是**对外发布的开源项目**，模板一致性是不可妥协的质量底线
2. 方案 A 的"漂移风险"在 AILP 项目中已验证过（种子文件与 DB 不同步 = 数据契约问题）
3. 回归风险可控：sdd-init 的核心逻辑（Step A1 信息收集、Step A2 文件写入）不变，只改变"从哪读取模板内容"

---

## 三、架构设计

### 整体架构

```
┌────────────────────────────────────────────────────────────┐
│                    GitHub 仓库首页                           │
│  ┌──────────┐  点击  ┌──────────┐  点击  ┌──────────────┐  │
│  │ README.md │ ────→ │INSTALL.md│ ────→ │  install.sh   │  │
│  │ 是什么/为什么│       │ 怎么装   │       │  一键安装      │  │
│  └──────────┘       └──────────┘       └──────┬─────────┘  │
│                                                │            │
│                           cp -r skills/sdd     │            │
│                           ~/.hermes/skills/    │            │
│                                                ▼            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              templates/（唯一真相源）                   │  │
│  │  AGENTS.md  CONSTITUTION.md  QUIRKS.md               │  │
│  │  .pre-commit-config.yaml  pytest.ini  conftest.py    │  │
│  └──────────┬───────────────────────────────────────────┘  │
│             │ sdd-init 引用（相对路径）                       │
│             ▼                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          skills/sdd/sdd-init/SKILL.md                 │  │
│  │  Step A2: "读取 ../../templates/AGENTS.md 并写入"      │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### 数据流

```
开发者打开 GitHub
  → README.md（理解项目）
  → INSTALL.md（了解安装）
  → git clone && ./install.sh（安装 Skills 到 ~/.hermes/skills/sdd/）
  → cd 自己的项目
  → 对 Hermes Agent 说"初始化 SDD"
  → sdd-init Skill 被加载
  → sdd-init 读取 templates/ 模板文件
  → 替换占位符
  → 写入开发者项目根目录
```

### 关键决策

| 决策 | 选项 | 选择 | 理由 |
|------|------|:---:|------|
| 模板存放位置 | 根目录 `templates/` | ✅ | 开发者可见，单一真相源 |
| sdd-init 如何读取模板 | 内嵌代码块 vs 文件引用 | 文件引用 | 解耦，避免漂移 |
| 安装方式 | 手动 cp vs install.sh | install.sh | 降低门槛，幂等设计 |
| README 流程图格式 | Mermaid vs ASCII | Mermaid | GitHub 原生渲染，可维护 |
| 语言 | 纯中文 vs 双语 | 中文（本迭代） | 当前用户群体以中文为主 |

---

## 四、详细设计

### 模块 1：README.md

**职责**：项目门面，让开发者在 5 秒内理解项目价值。

**内容结构**：
```markdown
# Hermes Harness
> 一句话描述

## 解决什么问题
痛点 → 方案（3 句话）

## SDD 流程（Mermaid 图）
```mermaid
graph LR
  PO[PO: 需求] → BA[BA: Spec] → AR[Architect: 设计] → CO[Coder: 实现] → RE[Reviewer: 评审] → QA[QA: 验证]
```

## 快速开始
```bash
git clone https://github.com/NEU-JING/hermes-harness.git
cd hermes-harness && ./install.sh
cd your-project && # 对 Hermes Agent 说"初始化 SDD"
```

## 文档
- [安装指南](INSTALL.md)
- [项目模板](templates/)
```

**关键实现**：
- 首屏内容控制在 ~15 行（无滚动可见）
- Mermaid 流程图用 `graph LR` 横向排列，移动端也友好
- 不引用未创建的文件（如 QUIRKS.md）

---

### 模块 2：INSTALL.md

**职责**：独立的安装指南，解答"怎么装到我的 Hermes Agent 里"。

**内容结构**：
```markdown
# 安装指南

## 前置条件
- Hermes Agent >= v2.0

## 安装
### 1. 克隆仓库
### 2. 运行安装脚本
### 3. 验证安装

## 卸载
## 升级
## 常见问题
```

**关键实现**：
- 前置条件写在最前面（避免"装完了才发现缺依赖"）
- 验证步骤用 `ls ~/.hermes/skills/sdd/` 输出预期目录列表
- 卸载：`rm -rf ~/.hermes/skills/sdd/`

---

### 模块 3：templates/ 目录

**职责**：存放接入 SDD 的项目需要的模板文件。每个模板文件顶部有 `# 模板` 注释说明用途。

**文件详情**：

| 文件 | 来源 | 关键注释 |
|------|------|------|
| `templates/AGENTS.md` | 旧 `agnets-template.md` | 占位符 `{project_name}` 等带注释 |
| `templates/CONSTITUTION.md` | 旧 `constitution-template.md` | 新增"项目特有约束"示例 |
| `templates/QUIRKS.md` | 旧 `quirks-template.md` | 已有，直接提升 |
| `templates/.pre-commit-config.yaml` | sdd-init SKILL.md L69-100 | 提取 YAML 块 |
| `templates/pytest.ini` | sdd-init SKILL.md L118-122 | 提取 INI 块 |
| `templates/conftest.py` | sdd-init SKILL.md L125-143 | 提取 Python 块，保留 `# SDD: CI-only` 标记 |

**关键约束**：
- 模板文件**不替换**占位符——占位符保留 `{...}` 格式
- 替换逻辑在 sdd-init 运行时执行

---

### 模块 4：install.sh

**职责**：将 `skills/sdd/` 目录安装到用户 Hermes Agent 的 Skills 路径。

**接口**：
- 输入：无（自动检测）
- 输出：stdout 安装日志
- 退出码：0=成功，1=部分失败

**逻辑伪代码**：
```bash
#!/bin/bash
set -euo pipefail

TARGET="$HOME/.hermes/skills/sdd"

# 检测目标路径
if [ -d "$TARGET" ]; then
    echo "⚠️  检测到已有安装: $TARGET"
    echo "   如需覆盖请手动删除后重试: rm -rf $TARGET"
    exit 0
fi

# 安装
mkdir -p "$(dirname "$TARGET")"
cp -r "$(dirname "$0")/skills/sdd" "$TARGET"

# 验证
echo "✅ 安装完成。已安装的 Skills:"
ls "$TARGET"/*/SKILL.md | sed 's|.*/skills/sdd/||;s|/SKILL.md||'
```

**关键实现**：
- 使用 `$(dirname "$0")` 定位仓库根目录（不依赖 `pwd`）
- `set -euo pipefail` 确保任何错误立即退出
- 不执行 `rm -rf ~/.hermes/` 等危险操作
- 已存在 → 警告 + 退出 0（幂等），**不自动覆盖**

---

### 模块 5：sdd-init SKILL.md 更新

**职责**：将内嵌代码块替换为模板文件引用。

**变更位置**（行号基于当前文件）：

| 原位置 | 原内容 | 改为 |
|------|------|------|
| L69-100 | 内嵌 .pre-commit-config.yaml | 引用 `../../templates/.pre-commit-config.yaml` |
| L118-122 | 内嵌 pytest.ini | 引用 `../../templates/pytest.ini` |
| L125-143 | 内嵌 conftest.py | 引用 `../../templates/conftest.py` |
| L59-65 | `skill_view(name='sdd-init', file_path='templates/agnets-template.md')` | 改为 `../../templates/AGENTS.md` |
| 文件名 | `agnets-template.md` | 删除（拼写修正） |

**路径约定**：
- sdd-init SKILL.md 位于 `skills/sdd/sdd-init/SKILL.md`
- 模板位于仓库根目录 `templates/`
- 相对路径：`../../templates/`（向上两级：sdd-init → sdd → skills → 仓库根）

**引用方式**：
Skill 指令中使用 `read_file` 工具读取模板文件：
```
使用 read_file(path='skills/sdd/../../templates/AGENTS.md') 读取模板，
替换占位符后写入目标项目根目录。
```
或简化为运行时根据 Skill 所在路径计算。

---

## 五、配置与约定

### 路径约定

| 路径 | 用途 |
|------|------|
| `templates/` | 项目级模板文件（唯一真相源） |
| `skills/sdd/sdd-init/SKILL.md` | 初始化 Skill（引用 templates/） |
| `~/.hermes/skills/sdd/` | 用户本地安装目标 |
| `docs/changes/{id}/` | SDD 变更产物目录 |

### 命名约定

- 模板文件：根目录 `templates/` 下，无 `-template` 后缀（因为整个目录就是模板）
- sdd-init 内旧模板：`agnets-template.md` → 删除（修正为 `templates/AGENTS.md`）

---

## 六、Tasks 拆分

| # | Task | 估时 | 依赖 | AC 覆盖 | 说明 |
|---|------|:---:|------|:---:|------|
| T1 | README.md | 10min | — | AC1, AC2, AC13 | 项目门面 |
| T2 | INSTALL.md | 8min | — | AC3, AC4 | 安装指南 |
| T3 | install.sh | 8min | — | AC4, AC5 | 一键安装脚本 |
| T4 | templates/ 目录 + 6 个文件 | 15min | — | AC6, AC7, AC8 | 模板文件创建 + 拼写修正 |
| T5 | sdd-init SKILL.md 引用更新 | 10min | T4 | AC9, AC10, AC12 | 内嵌 → 引用 |
| T6 | 验证 + sdd-init 回归测试 | 8min | T4, T5 | AC10, AC11 | 端到端验证 |
| T7 | 最终检查 + commit | 5min | T6 | AC13 | 链接验证 + 提交 |

**总估时**：64 分钟（约 1 小时）

---

## 七、实现顺序

```
T1 ─┐
T2 ─┤  并行（无依赖）
T3 ─┘
     │
     ▼
    T4（templates/ 文件就绪后，T5 才能引用）
     │
     ▼
    T5（sdd-init 引用更新）
     │
     ▼
    T6（验证 + 回归）
     │
     ▼
    T7（最终检查 + commit）
```
