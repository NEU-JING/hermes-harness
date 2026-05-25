# PRD: Hermes Harness 项目上手体验

> 版本：V1.0
> 日期：2026-05-25
> 作者：PO Agent

---

## 背景与目标

**背景**：

Hermes Harness 是一个面向开发者的开源项目——通用 SDD（Spec-Driven Development）开发框架。当前仓库已包含 8 个角色 Skill、共享规则、SDD 流程引擎等完整能力，并已在 AILP 等 3 个项目中验证可用。

但问题在于：**一个开发者打开 GitHub 仓库时完全不知道这是什么、怎么用、从哪开始。**

具体症状：
1. **根目录无 README**——开发者看到的是 AGENTS.md（面向 Agent 的配置）和 CONSTITUTION.md（项目宪法），这两份文件对"人"没有解释价值
2. **无安装指南**——Skills 藏在 `skills/sdd/` 目录下，开发者不知道该复制到哪、依赖什么
3. **项目级模板不可见**——AGENTS.md/CONSTITUTION.md/QUIRKS.md 的模板文件藏在 `skills/sdd/sdd-init/templates/` 深处，想接入 SDD 的开发者根本不知道它们存在

这是典型的"工程师产品"陷阱——功能完备但人机接口缺失。

**目标**：

让一个不了解 SDD 的开发者，从打开 GitHub 仓库到在自己的项目中跑通第一个 SDD 流程，**路径清晰、步骤可执行、无需额外问人**。

---

## 用户场景

### 场景 1：GitHub 来访者第一次看到项目

- **角色**：路过的开发者（不了解 SDD，甚至不知道 Hermes Agent）
- **前置条件**：从搜索引擎/社交媒体/友链进入 `github.com/NEU-JING/hermes-harness`
- **操作流程**：
  1. 打开仓库首页
  2. 在 README 中看到：项目是什么、解决什么问题、一张流程图
  3. 5 秒内判断"这东西跟我有没有关系"
  4. 如果有关，找到"快速开始"章节，了解最小安装步骤
- **期望结果**：5 秒内理解项目价值主张，30 秒内找到下一步行动

### 场景 2a：新项目从零接入 SDD

- **角色**：已安装 Hermes Agent 的开发者，刚创建了一个新项目
- **前置条件**：本地有 Hermes Agent 在运行，项目目录刚 `git init`
- **操作流程**：
  1. 阅读 INSTALL.md，执行安装命令
  2. 进入自己的项目目录，对 Hermes Agent 说"初始化 SDD" → sdd-init 自动生成 AGENTS.md、CONSTITUTION.md、QUIRKS.md
  3. 对 Hermes Agent 说"用 SDD 流程做 xxx" → 发起第一个变更
- **期望结果**：从空白项目到发起第一个 SDD 变更，不超过 5 分钟

### 场景 2b：存量项目升级接入 SDD

- **角色**：已安装 Hermes Agent 的开发者，有一个开发中的项目
- **前置条件**：项目已有代码、可能已有 .pre-commit-config.yaml 或 pytest 配置
- **操作流程**：
  1. 阅读 INSTALL.md，执行安装命令
  2. 进入自己的项目目录，对 Hermes Agent 说"把这个项目升级接入 SDD" → sdd-init 进入升级模式
  3. sdd-init 检测现有文件冲突（如已有 pre-commit 配置），输出升级计划
  4. 用户确认后，增量添加 SDD 文件（不覆盖已有配置）
  5. 用 `hermes skill load sdd-structure-lint` 验证结构完整性
- **期望结果**：存量项目平滑接入 SDD，不与现有配置冲突

### 场景 3：使用 SDD 的项目维护者想参考模板配置

- **角色**：已接入 SDD 的**业务项目**的维护者（如 AILP 的维护者）
- **前置条件**：项目已接入 SDD 一段时间，需要调整 AGENTS.md 自定义规则或 CONSTITUTION.md 约束
- **操作流程**：
  1. 打开 hermes-harness 仓库，在根目录看到 `templates/` 目录
  2. 参考 `templates/AGENTS.md` 了解 `convention_overrides` 的完整写法和注释
  3. 参考 `templates/CONSTITUTION.md` 的"项目特有约束"章节结构
  4. 回自己项目修改对应文件，不担心写错格式
- **期望结果**：`templates/` 作为"文档即规范"，维护者无需翻 `skills/sdd/sdd-init/` 深处的源码就能理解所有配置项

---

## 功能范围

### In Scope（本次包含）

- ✅ `README.md`：项目介绍、价值主张、架构概览图、快速开始
- ✅ `INSTALL.md`：安装指南（Helmes Agent 环境要求、安装命令、验证）
- ✅ `templates/` 目录：项目级模板文件（从 sdd-init 提升到根目录）
  - `templates/AGENTS.md`：项目配置模板
  - `templates/CONSTITUTION.md`：项目宪法模板
  - `templates/QUIRKS.md`：陷阱记录模板
  - `templates/.pre-commit-config.yaml`：pre-commit 配置模板
  - `templates/pytest.ini`：pytest CI-only marker 配置模板
  - `templates/conftest.py`：CI-only 跳过逻辑模板
- ✅ `install.sh`：一键安装脚本（cp skills 到 ~/.hermes/skills/sdd/）
- ✅ 更新 `sdd-init` 中模板路径引用（从内嵌模板改为引用 `templates/` 目录）

### Out of Scope（本次不包含）

- ❌ 修改任何 Skill 的核心逻辑
- ❌ 新增/删除 SDD 规则
- ❌ 前端 Dashboard
- ❌ Hermes Agent 本身的 CLI 改进
- ❌ CI/CD 配置（GitHub Actions 等）
- ❌ QUIRKS.md 文件创建（hermes-harness 自身的 QUIRKS.md）
- ❌ 多语言支持（README 仅中文，后续迭代加英文）

---

## 非功能需求（NFR）

| 类别 | 要求 | 指标 |
|------|------|------|
| 可用性 | 新用户 5 秒理解项目 | README 第一屏包含一句话描述 + 一张架构图 |
| 可用性 | 安装步骤 ≤ 3 步 | 克隆→安装→验证，每步一条命令 |
| 可维护性 | 模板与 Skill 解耦 | sdd-init 引用 `../../templates/` 而非内嵌内容 |
| 可维护性 | 模板文件自文档化 | 每个模板含注释说明占位符含义 |
| 兼容性 | 安装脚本幂等 | 重复执行 install.sh 不产生副作用 |
| 安全 | install.sh 不执行高危操作 | 仅 cp 和 mkdir，不 rm -rf |

---

## 验收标准（高层级）

1. **AC-1**：打开 GitHub 仓库首页，README 在首屏回答"这是什么、解决什么问题、怎么开始"
2. **AC-2**：执行 `./install.sh` 后，`~/.hermes/skills/sdd/` 下出现所有 Skill 目录且内容完整
3. **AC-3**：`templates/` 目录包含 6 个模板文件，每个文件有占位符和使用说明注释
4. **AC-4**：`sdd-init` Skill 成功引用 `templates/` 下的模板文件（通过相对路径）
5. **AC-5**：一个从未接触过 Hermes Harness 的开发者，按 INSTALL.md 步骤操作，能在 5 分钟内完成安装并在一个测试项目中成功运行 `sdd-init`
6. **AC-6**：AGENTS.md 文件名拼写错误修正（`agnets-template.md` → `agents-template.md`）

---

## 风险与假设

### 风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|:---:|------|
| install.sh 覆盖用户已有 Skill | 用户自定义 Skill 丢失 | 低 | install.sh 检测已有文件，输出警告并询问是否覆盖 |
| templates/ 与 sdd-init 内嵌内容不一致 | 两套模板内容不同步 | 中 | sdd-init 改为引用 templates/，内嵌内容删除，单向同步 |
| 用户无 Hermes Agent | install.sh 执行了但无法使用 | 高 | README 第一节写明前置条件"需要 Hermes Agent v2.x+" |

### 假设

- 用户已安装 Hermes Agent（>= v2.0）
- 用户的 `~/.hermes/skills/` 目录结构为标准布局
- 用户的操作系统为 Linux/macOS（Windows 的 Git Bash 也兼容）
- 当前仓库的 `skills/sdd/` 目录结构在本次变更中不发生变化
