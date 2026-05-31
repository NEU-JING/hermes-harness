# AGENTS.md — Hermes SDD 项目配置

## 项目信息
- name: "Hermes SDD"
- description: "通用 SDD（Spec-Driven Development）开发框架——可复用的 Agentic 开发流程引擎"
- repo: "https://github.com/NEU-JING/hermes-harness"

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

## SDD Profile 覆盖（可选）

# Hermes v2.1.0+ 支持基于 Profile 的多 Agent 委托。
# 不声明此段 = 使用 skills/sdd/shared/sdd-rules.md 中的默认映射。
# 声明后只覆盖指定角色，未覆盖角色继续使用默认值。
# 示例：
# sdd_config:
#   role_to_profile:
#     po: "sdd-pro"        # 将 PO 升级为 pro 模型
#     coder: "sdd-flash"   # 将 Coder 降级为 flash（不推荐）
