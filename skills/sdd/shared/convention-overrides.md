# SDD 约定覆盖机制

> 项目可通过 AGENTS.md 禁用或自定义 SDD 通用规则。本文档定义可覆盖项和覆盖语法。

---

## 覆盖方式

项目在 `AGENTS.md` 的 `## 自定义覆盖` 章节中声明覆盖项：

```markdown
## 自定义覆盖
- convention_overrides:
    disable_rules: ["R5"]          # 禁用指定规则
    custom_rules:                  # 新增项目特有规则
      - id: "R11"
        name: "规则名称"
        trigger: "触发时机"
        check: "检查方式"
```

---

## 可禁用规则清单

以下内置规则可通过 `disable_rules` 禁用：

| 规则 | 编号 | 可禁用 | 典型禁用场景 |
|------|:---:|:---:|------|
| 没有 Spec 不写代码 | R1 | ✓ | 项目不需要 Spec 阶段（如纯配置仓库） |
| 编码前 Brainstorming | R2 | ✓ | 项目技术栈单一，无方案选择空间 |
| TDD 强制 | R3 | ✗ | **不可禁用**（核心原则） |
| 编码后必须评审 | R4 | ✓ | 个人项目、实验性项目 |
| 前后端契约同步 | R5 | ✓ | 无前端项目、纯后端服务 |
| 测试自包含原则 | R6 | ✗ | **不可禁用**（核心原则） |
| E2E-AC 一一对应 | R7 | ✓ | 无 E2E 测试能力的项目 |
| Push 前必过 Pre-commit | R8 | ✗ | **不可禁用**（核心原则） |
| 目标环境通过原则 | R9 | ✓ | 无 CI 环境的项目（仅本地开发） |
| PR 不直接 push main | R10 | ✓ | 个人仓库、单分支开发 |

### 不可禁用规则说明

R3、R6、R8 被标记为不可禁用的原因：

- **R3 (TDD)**：保证代码可测试性，是 SDD 质量基线的底线
- **R6 (测试自包含)**：防止测试环境依赖导致的不可复现问题
- **R8 (Pre-commit)**：保证代码格式一致性，降低评审成本

---

## 自定义规则

项目可新增项目特有规则。自定义规则与内置规则同等效力，编排器在指定触发时机执行检查。

### 自定义规则格式

```yaml
custom_rules:
  - id: "R11"
    name: "禁止使用 any 类型"
    trigger: "reviewer-agent Phase 2"
    check: "grep -r ': any' src/"
    violation: "MAJOR"
    description: "TypeScript 项目禁止使用 any 类型，必须显式声明"

  - id: "R12"
    name: "数据库迁移必须可回滚"
    trigger: "architect-agent Design 阶段"
    check: "检查 migration 文件是否包含 down 方法"
    violation: "CRITICAL"
    description: "所有数据库迁移必须提供回滚脚本"

  - id: "R13"
    name: "API 响应时间 ≤ 200ms (P95)"
    trigger: "qa-agent 性能测试阶段"
    check: "运行 benchmark 脚本，检查 P95 延迟"
    violation: "MAJOR"
    description: "核心 API 端点 P95 延迟必须 ≤ 200ms"
```

### 自定义规则字段

| 字段 | 必选 | 说明 |
|------|:---:|------|
| `id` | ✓ | 规则编号，格式 `R{n}`，n ≥ 11（避免与内置冲突） |
| `name` | ✓ | 规则名称 |
| `trigger` | ✓ | 触发时机（阶段名 + Agent 名） |
| `check` | ✓ | 检查方式（shell 命令或描述性指令） |
| `violation` | ✓ | 违反严重级别：CRITICAL / MAJOR / MINOR |
| `description` | ✗ | 规则详细说明 |

---

## 覆盖解析顺序

```
1. 加载 sdd/shared/sdd-rules.md（内置规则 R1-R10）
2. 读取项目 AGENTS.md → convention_overrides
3. 过滤 disable_rules 中的规则
4. 追加 custom_rules 中的规则
5. 合并为最终规则集（内置 - 禁用 + 自定义）
```

---

## 常见覆盖配置

### 无前端项目

```markdown
## 自定义覆盖
- convention_overrides:
    disable_rules: ["R5", "R7"]
```

### 个人实验项目

```markdown
## 自定义覆盖
- convention_overrides:
    disable_rules: ["R1", "R2", "R4", "R10"]
```

### 金融/合规项目

```markdown
## 自定义覆盖
- convention_overrides:
    custom_rules:
      - id: "R11"
        name: "敏感数据不得出现在日志中"
        trigger: "reviewer-agent Phase 2"
        check: "grep -rE '(password|token|secret).*log' src/"
        violation: "CRITICAL"
      - id: "R12"
        name: "所有外部 API 调用必须有超时设置"
        trigger: "reviewer-agent Phase 2"
        check: "grep -r 'requests\\.(get|post)' src/ | grep -v timeout"
        violation: "MAJOR"
```

### 开源项目

```markdown
## 自定义覆盖
- convention_overrides:
    custom_rules:
      - id: "R11"
        name: "LICENSE 文件必须存在"
        trigger: "sdd-structure-lint 文件级检查"
        check: "test -f LICENSE"
        violation: "CRITICAL"
      - id: "R12"
        name: "CHANGELOG.md 必须在每次变更时更新"
        trigger: "coder-agent Task 完成时"
        check: "git diff --cached --name-only | grep CHANGELOG.md"
        violation: "MAJOR"
```
