# AGENTS.md — Hermes SDD 项目配置

## 项目信息
- name: "Hermes SDD"
- description: "通用 SDD（Spec-Driven Development）开发框架——可复用的 Agentic 开发流程引擎"
- repo: "https://github.com/NEU-JING/hermes-harness"
- version: "2.3.0"

## 技术栈
- runtime: "Hermes Agent Skills 系统"
- format: "Markdown（SKILL.md + references/*.md）"
- testing: "手动验证（通过 mock 项目走完整 SDD 流程）"

## 路径约定
- changes_dir: "docs/changes/"
- current_dir: "docs/current/"
- archive_dir: "docs/archive/"
- skills_dir: "skills/sdd/"
- output_dir: "~/.hermes/skills/sdd/"

## SDD 配置
- flow_engine: "sdd/sdd-orchestrator"
- default_flow_level: "Standard"

## 项目约束
- constitution: "CONSTITUTION.md"
- quirks: "QUIRKS.md"

## 自定义覆盖
- convention_overrides:
    tasks_split_rule: "按角色 Skill 拆分，每个 Skill 是一个 Task"
    output_format: "SKILL.md（YAML frontmatter + Markdown body）"

---

## SDD Profile 架构概述

Hermes SDD 框架采用 **Profile + Soul 双层差异化架构**，实现真正的角色分离：

```
┌─────────────────────────────────────────────────────────────────┐
│                        Profile 层（配置层）                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ 模型配置     │  │ Provider配置  │  │ 工具集权限   │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Soul 层（思维层）                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ 角色定义     │  │ 思维模式     │  │ 输出风格     │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

**核心原理**: Kanban 调度器使用 `hermes -p <profile>` 启动 Worker，每个 Profile 独立加载自己的 `config.yaml`（模型/Provider）和 `SOUL.md`（思维特质），实现零侵入的角色差异化。

---

## Profile 能力矩阵

| 角色 | Profile 名称 | 推荐模型 | Provider | Soul 核心特质 | 对应 Skill |
|------|-------------|---------|----------|--------------|-----------|
| **PO** | sdd-po | deepseek-v4-flash | DeepSeek | 用户思维、场景化、价值导向 | po-agent |
| **BA** | sdd-ba | deepseek-v4-flash | DeepSeek | MECE、边界清晰、可测性优先 | ba-agent |
| **Architect** | sdd-architect | deepseek-v4-flash | DeepSeek | 权衡分析、分层设计、演进式思维 | architect-agent |
| **Coder** | sdd-coder | deepseek-v4-flash | DeepSeek | TDD、防御式编程、可读性优先 | coder-agent |
| **Reviewer** | sdd-reviewer | deepseek-v4-pro | DeepSeek | 批判性、三阶段评审、异质视角 | reviewer-agent |
| **QA** | sdd-qa | deepseek-v4-flash | DeepSeek | 破坏式、组合覆盖、回归意识 | qa-agent |
| **Orchestrator** | — | — | — | 状态机调度、流程编排 | sdd-orchestrator |

> **异构评审模式**: Reviewer 角色使用独立的 DeepSeek Provider 和模型，提供与开发阶段完全不同的第三方视角，避免"同一个模型审自己的代码"导致的盲区。

---

## Soul 模式配置

### 什么是 Soul 模式

Soul 模式是每个 Profile 的 `SOUL.md` 文件，定义该角色的**思维特质、决策倾向、输出风格**。与系统提示词不同，Soul 更关注"人格特质"而非"任务指令"。

### 配置位置

每个 Profile 的 SOUL.md 位于：
```
~/.hermes/profiles/<profile-name>/SOUL.md
```

### 配置示例

```markdown
# sdd-reviewer (代码评审专家)

## 核心思维模式
1. 批判性思维：假设代码有问题，直到证明它没问题
2. 开发者视角切换："如果我来维护这段代码，我会遇到什么坑？"

## 评审原则
- 对事不对人：评价代码，不评价开发者
- 给出具体建议：不只说"不好"，要说"怎么更好"
- 解释为什么：说明这样改的理由

## 禁止事项
- ❌ 不做风格自行车棚争论
- ❌ 不要求"完美"，只要求"可接受"
```

### 启用/禁用 Soul 模式

Soul 模式默认启用（只要 `SOUL.md` 文件存在）。如需禁用：
```bash
# 临时禁用
mv ~/.hermes/profiles/sdd-reviewer/SOUL.md ~/.hermes/profiles/sdd-reviewer/SOUL.md.disabled

# 重新启用
mv ~/.hermes/profiles/sdd-reviewer/SOUL.md.disabled ~/.hermes/profiles/sdd-reviewer/SOUL.md
```

---

## Workspace 配置规范

### Workspace 类型对比

| 类型 | 特性 | 适用场景 | 产物持久化 | 跨会话共享 |
|------|------|---------|-----------|-----------|
| `dir:<abs_path>` | 绑定到指定目录 | SDD 开发流程、需要持久化产物的场景 | ✅ 是 | ✅ 是 |
| `scratch` | 临时目录，任务完成后删除 | 一次性任务、数据探索、POC | ❌ 否 | ❌ 否 |

### SDD 流程的 Workspace 选择

**强制使用 `dir` 类型**，原因：
1. SDD 流程分多阶段执行，需要跨阶段共享产物
2. 产物需要提交到 Git，必须在项目目录内
3. 流程可中断、可恢复，不丢失中间状态

### 配置最佳实践

在 orchestrator 中使用绝对路径绑定：
```python
# ✅ 正确：使用脚本位置推导绝对路径
project_root = Path(__file__).resolve().parents[4]
workspace_path = f"dir:{project_root}"

# ❌ 错误：使用相对路径，依赖 CWD
workspace_path = "dir:."
```

### 路径验证

Worker 启动时应验证 workspace 路径：
```bash
if [ ! -d "$WORKSPACE_PATH" ]; then
  echo "❌ Workspace path does not exist: $WORKSPACE_PATH"
  exit 1
fi
```

---

## SDD Profile 映射（已启用）

sdd_config:
  role_to_profile:
    po: "sdd-po"              # PO → doubao-seed-2.0-pro（多模态产品设计）
    ba: "sdd-ba"              # BA → doubao-seed-2.0-pro（需求分析）
    architect: "sdd-architect" # Architect → glm-5.1（深度推理架构设计）
    coder: "sdd-coder"        # Coder → doubao-seed-2.0-code（代码专用模型）
    reviewer: "sdd-reviewer"   # Reviewer → deepseek-v4-pro（异构评审，原生DeepSeek）
    qa: "sdd-qa"              # QA → doubao-seed-2.0-pro（多模态测试）
  profile_enabled: true        # 使用 Kanban Profile 调度机制
  soul_enabled: true           # 启用 SOUL.md 思维特质模式
  workspace_type: "dir"        # 强制使用 dir 类型 workspace
