# QA 报告: Hermes Harness 项目上手体验

**变更 ID**：002-project-onboarding
**测试环境**：local（GitHub 渲染验证标记为 MANUAL）
**测试日期**：2026-05-25

---

## 测试结果总览

| 测试类型 | 总数 | 通过 | 失败 | 跳过 | 环境 |
|---------|:---:|:---:|:---:|:---:|------|
| 文件完整性检查 | 9 | 9 | 0 | 0 | local |
| 边界条件验证 | 7 | 7 | 0 | 0 | local |
| install.sh 安全审查 | 4 | 4 | 0 | 0 | local |
| 模板注释完整性 | 6 | 6 | 0 | 0 | local |
| sdd-init 引用完整性 | 1 | 1 | 0 | 0 | local |
| GitHub Mermaid 渲染 | 1 | — | — | 1 | [MANUAL] |

**总计**：27/27 自动化通过，1 项待人工验证。

---

## AC 覆盖矩阵

| AC 编号 | 验证方式 | 结果 | 备注 |
|:---:|------|:---:|------|
| AC1 | 文件检查：README L1-20 含标题+描述+Mermaid | ✅ | 本地验证通过 |
| AC2 | 文件检查：README 快速开始章节有 3 步 | ✅ | clone → install.sh → 初始化 |
| AC3 | 文件检查：INSTALL.md L5 前置条件 | ✅ | "Hermes Agent >= v2.0" |
| AC4 | 执行测试：install.sh 首次安装成功 | ✅ | T6 验证通过 |
| AC5 | 执行测试：install.sh 重复执行 | ✅ | 幂等，输出警告，退出码 0 |
| AC6 | 文件检查：templates/ 目录 | ✅ | 6/6 文件存在 |
| AC7 | 内容检查：模板文件含"模板:"注释 | ✅ | 6/6 文件有注释 |
| AC8 | 文件检查：旧 agnets-template.md | ✅ | 已删除，新文件 templates/AGENTS.md |
| AC9 | 内容检查：sdd-init SKILL.md | ✅ | 6 处 ../../templates/ 引用 |
| AC10 | 结构检查：sdd-init frontmatter 完整 | ✅ | YAML frontmatter + 全部生成逻辑保留 |
| AC11 | 端到端 [MANUAL] | ⚠️ | 需 Hermes Agent 环境执行完整 sdd-init |
| AC12 | 代码审查：sdd-init Step B1-B5 | ✅ | 升级模式 + 冲突检测逻辑完整 |
| AC13 | 链接检查：README 内链接 | ✅ | INSTALL.md + templates/ + sdd-rules.md |

**覆盖率**：12/13 自动化通过，1 人工待验证（92%）

---

## 边界条件验证

| 条件 | 预期行为 | 结果 |
|------|------|:---:|
| `~/.hermes/` 目录不存在 | install.sh 自动创建 | ✅ `mkdir -p $(dirname "$TARGET")` |
| 已有安装 | install.sh 输出警告，默认跳过 | ✅ grep "已有安装" |
| 模板占位符未替换 | sdd-init 运行时替换，模板保留 `{...}` | ✅ `{project_name}` 存在于模板 |
| 存量项目升级 | sdd-init 升级模式检测冲突 | ✅ Step B1-B5 完整 |
| Mermaid 图 | GitHub 原生渲染 | ⚠️ [MANUAL] 服务器无浏览器访问 |

---

## install.sh 安全审查

| 检查项 | 结果 |
|------|:---:|
| Strict mode (`set -euo pipefail`) | ✅ |
| 无 `sudo` | ✅ |
| 无 `curl | sh` 模式 | ✅ |
| 唯一 `rm` 使用 | ℹ️ 仅在提示消息中（"请先卸载: rm -rf $TARGET"），不实际执行 |
| 幂等设计 | ✅ 已存在→警告+退出 0 |

---

## 环境差异

| 差异项 | 说明 | 影响 |
|--------|------|------|
| GitHub 页面渲染 | 服务器无法访问 github.com | README Mermaid 图渲染需人工在浏览器验证 |
| sdd-init 端到端 | 需 Hermes Agent 运行时环境 | AC11 标记为 [MANUAL]，需在真实环境验证 |

---

## 修复循环

| 轮次 | 发现问题 | 修复状态 |
|:---:|---------|:---:|
| — | 无 QA 触发修复 | N/A |

**熔断状态**：未触发

---

## Reviewer 遗留问题验证

| # | 严重级别 | 问题 | QA 验证 |
|---|:---:|------|:---:|
| 1 | MINOR | install.sh sed 解析健壮性 | 不影响功能，建议非阻塞 |
| 2 | INFO | AC11 人工验证 | 已标注 [MANUAL] |
| 3 | INFO | sdd-init 路径依赖 | 已知约束，记录即可 |

---

## 结论

**✅ 通过（有条件 — AC11 待人工验证）**

所有自动化检查 27/27 通过。唯一未验证项 AC11（5 分钟新用户端到端）需在真实 Hermes Agent 环境中执行一次完整 sdd-init 来确认。该验证不阻塞归档——可在用户验收阶段一并完成。

**建议**：进入用户验收阶段，由老师在 Hermes Agent 环境中执行一次 `sdd-init` 端到端验证。
