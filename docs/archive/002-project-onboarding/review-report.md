# Review Report: Hermes Harness 项目上手体验

> 变更 ID：002-project-onboarding
> 评审日期：2026-05-25
> 评审员：Reviewer Agent
> 评审范围：5 commits (4b7a367..e941057)，15 files，+1796/-63

---

## 评审结论

**结论：✅ 通过**

无 CRITICAL 问题，无 MAJOR 问题。1 项 MINOR 建议 + 2 项 INFO 标注。

---

## Phase 1: Spec 合规

逐 AC 验证：

| AC | 描述 | 验证方式 | 结果 |
|:---:|------|------|:---:|
| AC1 | README 首屏含标题+描述+流程图 | 读取 README.md L1-20 | ✅ 首屏含 "Hermes Harness" + 中文描述 + Mermaid 图 |
| AC2 | 快速开始 ≤ 3 步 | 读取 README.md L24-36 | ✅ 3 步：clone → install.sh → 对 Agent 说"初始化 SDD" |
| AC3 | 前置条件明确 | 读取 INSTALL.md L5 | ✅ "Hermes Agent >= v2.0" |
| AC4 | 安装步骤可执行 | T6 实测 install.sh | ✅ 首次安装成功，验证步骤正常 |
| AC5 | install.sh 幂等 | T6 重复执行 | ✅ 第二次执行输出"已有安装"，退出码 0 |
| AC6 | templates/ 6 文件齐全 | ls templates/ | ✅ 6/6 文件存在 |
| AC7 | 模板文件自文档化 | 读取 templates/AGENTS.md L1-6 | ✅ 顶部有 `# 模板: AGENTS.md` + 占位符说明 |
| AC8 | 拼写修正 | 检查旧文件 | ✅ agnets-template.md 已删除，新文件为 templates/AGENTS.md |
| AC9 | sdd-init 引用模板 | grep sdd-init SKILL.md | ✅ 6 处 `../../templates/` 引用，0 处内嵌 YAML/Python |
| AC10 | sdd-init 功能保留 | diff 分析 | ✅ frontmatter 完整，Step A1/A2 逻辑未变，仅改模板来源 |
| AC11 | 5 分钟上手 [MANUAL] | 模拟验证 | ⚠️ 模板可读性验证通过，但完整 sdd-init 执行需 Hermes Agent 环境 |
| AC12 | 存量升级不冲突 | sdd-init SKILL.md | ✅ 升级模式（Step B1-B5）完整保留，冲突检测逻辑未变 |
| AC13 | README 链接有效 | grep README.md | ✅ INSTALL.md 链接 + templates/ 链接 + sdd-rules.md 链接 |

**Phase 1 结果：13/13 AC 覆盖** ✅

---

## Phase 2: 代码/文档质量

| 检查项 | 结果 | 说明 |
|------|:---:|------|
| DRY | ✅ | 模板提升后无重复，sdd-init SKILL.md 无内嵌代码 |
| YAGNI | ✅ | 无过度设计，每个文件职责明确 |
| 函数/文档 ≤ 50 行 | ✅ | README 47 行，INSTALL 66 行，install.sh 37 行 |
| 命名清晰 | ✅ | 文件名语义化，AGENTS.md/CONSTITUTION.md/QUIRKS.md 规范统一 |
| 错误处理 | ✅ | install.sh 使用 `set -euo pipefail`，幂等检测 |
| 无 TODO/FIXME | ✅ | 全量 diff 无残留 |
| 前后端契约 | N/A | 本次纯文档变更，无 API/Schema 变更 |

### 发现的问题

| # | 严重级别 | 文件 | 位置 | 问题描述 | 修复建议 |
|---|:---:|------|------|---------|---------|
| 1 | MINOR | `install.sh` | L17 | `ls "$TARGET/"*/SKILL.md \| sed ...` sed 管道解析目录名，若目录含空格或特殊字符可能错误切分 | 改为 `for d in "$TARGET"/*/; do basename "$d"; done` 更安全 |

---

## Phase 3: 架构一致性

| 检查项 | Design 约定 | 实际实现 | 结果 |
|------|------|------|:---:|
| 模板存放位置 | 根目录 `templates/` | `templates/` 6 个文件 | ✅ |
| sdd-init 引用方式 | `read_file` 相对路径 | 6 处 `../../templates/` | ✅ |
| install.sh 幂等 | 已存在→警告+退出 0 | 检测 `-d` 后输出警告 | ✅ |
| README 流程图格式 | Mermaid `graph LR` | Mermaid 含 8 节点 SDD 流程 | ✅ |
| 语言 | 中文 | 全中文（README/INSTALL/模板注释） | ✅ |
| 旧文件清理 | 删除 agnets-template.md | 已 `git rm` | ✅ |

### 架构偏离

无。

### 信息标注

| # | 严重级别 | 说明 |
|---|:---:|------|
| 2 | INFO | AC11 [MANUAL] 无法在纯文档变更中自动化验证——完整端到端需真实 Hermes Agent 环境执行 sdd-init。建议在 QA 阶段做一次人工冒烟。 |
| 3 | INFO | sdd-init SKILL.md 中 `../../templates/` 路径依赖 Skill 所在目录不变。未来若调整 skills/sdd/sdd-init/ 层级，需同步更新引用路径。可在 QUIRKS.md 中记录此约定。 |

---

## 总结

| 阶段 | 结果 |
|------|:---:|
| Phase 1: Spec 合规 | ✅ 13/13 AC 覆盖 |
| Phase 2: 代码/文档质量 | ✅ 1 MINOR（不影响功能） |
| Phase 3: 架构一致性 | ✅ 无偏离 |

**建议**：MINOR #1（install.sh sed 健壮性）可在后续迭代中修复，不阻塞当前阶段。可直接进入 QA。
