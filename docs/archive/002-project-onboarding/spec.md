# Spec: Hermes Harness 项目上手体验

> 版本：V1.0
> 日期：2026-05-25
> 作者：BA Agent（基于 [PRD](./prd.md)）

---

## 功能概述

为 hermes-harness 仓库补齐面向人类开发者的入口层：README（项目门面）、INSTALL（安装指南）、templates/（项目级模板目录）、install.sh（一键安装脚本），并修正 sdd-init 中模板引用方式。

---

## 详细需求

### 需求 1：README.md — 项目门面

**描述**：在仓库根目录创建 README.md，让开发者 5 秒理解项目、30 秒找到下一步。

**内容要求**：
- 项目名称 + 一句话描述（中文）
- 解决什么问题（痛点 → 方案）
- SDD 流程图（ASCII 或 Mermaid）
- 快速开始（3 步：克隆 → 安装 → 初始化）
- 链接到 INSTALL.md 和 templates/

**约束**：
- 第一屏（无需滚动）必须包含项目名称、一句话描述、架构/流程图
- 不引用尚未创建的文件（如 QUIRKS.md）

---

### 需求 2：INSTALL.md — 安装指南

**描述**：独立的安装指南，告诉开发者如何把 Skills 装到本地。

**内容要求**：
- 前置条件（Hermes Agent >= v2.0）
- 安装步骤（≤ 3 条命令）
- 验证方式（如何确认安装成功）
- 卸载方式

---

### 需求 3：templates/ 目录 — 项目级模板

**描述**：在仓库根目录创建 `templates/`，存放接入 SDD 的项目需要的模板文件。这些文件原本散落在 `skills/sdd/sdd-init/templates/` 和 SKILL.md 内嵌代码块中。

**文件清单**：

| 文件 | 来源 | 说明 |
|------|------|------|
| `templates/AGENTS.md` | sdd-init/templates/agnets-template.md | 修正拼写错误，添加注释 |
| `templates/CONSTITUTION.md` | sdd-init/templates/constitution-template.md | 添加"项目特有约束"示例注释 |
| `templates/QUIRKS.md` | sdd-init/templates/quirks-template.md | 已有，直接提升 |
| `templates/.pre-commit-config.yaml` | sdd-init SKILL.md 内嵌 YAML | 提取为独立文件 |
| `templates/pytest.ini` | sdd-init SKILL.md 内嵌 INI | 提取为独立文件 |
| `templates/conftest.py` | sdd-init SKILL.md 内嵌 Python | 提取为独立文件 |

**约束**：
- 每个模板文件顶部有注释说明这是模板，占位符用 `{...}` 标记
- 文件名修正：`agnets-template.md` → `AGENTS.md`

---

### 需求 4：install.sh — 一键安装脚本

**描述**：将 `skills/sdd/` 安装到 `~/.hermes/skills/sdd/`。

**逻辑**：
```bash
1. 检测 ~/.hermes/skills/sdd/ 是否已存在
2. 如已存在 → 输出警告，询问是否覆盖（非交互模式默认跳过）
3. 如不存在 → cp -r skills/sdd ~/.hermes/skills/sdd/
4. 验证安装结果（ls 列出已安装的 Skill 目录）
```

**约束**：
- 幂等：重复执行不产生副作用
- 不执行 rm -rf 等危险操作
- 兼容 Linux/macOS
- 退出码 0=成功，1=部分失败

---

### 需求 5：sdd-init 模板引用更新

**描述**：sdd-init SKILL.md 当前将 .pre-commit-config.yaml、pytest.ini、conftest.py 的内容硬编码在文档中。需要改为引用 `templates/` 目录下的文件。

**变更范围**：
- `skills/sdd/sdd-init/SKILL.md`：Step A2.4 和 A2.4a 内嵌代码块替换为模板文件引用
- `skills/sdd/sdd-init/templates/`：旧模板文件可删除（已提升到根目录 templates/），或保留为重定向

---

## Acceptance Criteria（验收标准）

| 编号 | 场景 | Given | When | Then |
|:---:|------|-------|------|------|
| AC1 | 仓库首页第一印象 | 开发者打开 GitHub 仓库首页 | 看到 README 渲染结果 | 第一屏（无需滚动）包含：项目名称、一句话描述（中文）、SDD 流程图（ASCII/Mermaid） |
| AC2 | 快速开始路径清晰 | README 已渲染 | 开发者阅读"快速开始"章节 | 看到 ≤ 3 个步骤，每步有一条可复制粘贴的命令 |
| AC3 | 安装前置条件明确 | 开发者打开 INSTALL.md | 阅读文档 | 看到明确的前置条件："需要 Hermes Agent v2.0+" |
| AC4 | 安装步骤可执行 | 开发者在仓库根目录 | 按 INSTALL.md 顺序执行命令 | 每条命令成功执行，最后验证步骤显示已安装的 Skill 列表 |
| AC5 | install.sh 幂等 | 已经执行过一次 install.sh | 再次执行 install.sh | 输出警告"已存在"，不覆盖已有文件，退出码 0 |
| AC6 | templates/ 文件齐全 | 开发者列出 `templates/` 目录 | 执行 `ls templates/` | 看到 6 个文件：AGENTS.md、CONSTITUTION.md、QUIRKS.md、.pre-commit-config.yaml、pytest.ini、conftest.py |
| AC7 | 模板文件自文档化 | 开发者打开 `templates/AGENTS.md` | 阅读文件内容 | 看到注释说明每个占位符的含义（如 `{project_name}` — 项目名称） |
| AC8 | 文件名拼写修正 | 查看旧模板目录 | 检查 `sdd-init/templates/` | `agnets-template.md` 不再存在；新模板在 `templates/AGENTS.md` |
| AC9 | sdd-init 引用模板文件 | sdd-init 执行 Step A2.4 | 读取 Skill 指令 | 指令引用 `../../templates/.pre-commit-config.yaml` 而非内嵌 YAML 代码块 |
| AC10 | sdd-init 功能不受影响 | 模板提升后 | 在一个测试项目中执行 `sdd-init` | AGENTS.md、CONSTITUTION.md、QUIRKS.md、.pre-commit-config.yaml 均正确生成 |
| AC11 | 新项目 5 分钟上手 [MANUAL] | 一个未接触过 hermes-harness 的开发者 + 新项目 | 按 README → INSTALL → sdd-init 操作 | 5 分钟内完成安装并在项目中成功运行 `sdd-init` |
| AC12 | 存量项目升级不冲突 | 项目已有 .pre-commit-config.yaml（非 SDD 来源） | 执行 `sdd-init --upgrade` | sdd-init 检测到冲突，输出升级计划，标记已有文件"⚠️ 冲突"，不自动覆盖 |
| AC13 | README 链接有效 | README 中包含链接 | 点击 README 中的 INSTALL.md 链接和 templates/ 链接 | 链接跳转到正确文件/目录 |

---

## 非功能需求细化

| 类别 | 原始 NFR | 细化指标 | 验证方式 |
|------|---------|---------|---------|
| 可用性 | 新用户 5 秒理解项目 | README 第一屏内：标题 ≤ 10 字 + 描述 ≤ 30 字 + 架构图 | 人工验证（AC1） |
| 可用性 | 安装步骤 ≤ 3 步 | 克隆 + ./install.sh + 验证 = 3 条命令 | 人工验证（AC4） |
| 可用性 | 5 分钟端到端 | 从 git clone 到 sdd-init 成功执行 ≤ 300s | 人工计时（AC11） |
| 可维护性 | 模板与 Skill 解耦 | sdd-init 中无内嵌 YAML/INI/Python 代码块 | 代码审查（AC9） |
| 可维护性 | 模板文件自文档化 | 每个模板 ≥ 3 条注释，占位符均有说明 | 代码审查（AC7） |
| 兼容性 | install.sh 幂等 | 重复执行无副作用，退出码 0 | 自动化测试（AC5） |
| 兼容性 | 存量项目升级无覆盖 | sdd-init 升级模式不自动覆盖已有文件 | 自动化测试（AC12） |
| 安全 | install.sh 无危险操作 | 脚本中不含 rm -rf / 等危险命令 | 代码审查 |

---

## 边界条件

| 条件 | 预期行为 |
|------|------|
| `~/.hermes/` 目录不存在 | install.sh 自动创建 |
| 用户手动修改过 ~/.hermes/skills/sdd/ 下的 Skill | install.sh 检测到已有文件，输出警告，默认跳过 |
| 模板文件中的占位符未替换 | sdd-init 执行时替换，模板文件本身保留占位符 |
| 非 Linux/macOS 环境（Windows Git Bash） | install.sh 兼容，README 中注明 |
| README 中的 Mermaid 图 | GitHub 原生渲染 Mermaid，无需额外插件 |
