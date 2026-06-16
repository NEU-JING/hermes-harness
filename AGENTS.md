# AGENTS.md — Hermes SDD 项目配置

## 项目信息
- name: "Hermes SDD"
- description: "通用 SDD（Spec-Driven Development）开发框架——可复用的 Agentic 开发流程引擎"
- repo: "https://github.com/NEU-JING/hermes-harness"
- version: "2.6.0"

## 技术栈
- runtime: "Hermes Agent Skills 系统"
- format: "Markdown（SKILL.md + references/*.md）"
- testing: "手动验证（通过 mock 项目走完整 SDD 流程）"

## 路径约定
- changes_dir: "docs/changes/"
- current_dir: "docs/current/"
- archive_dir: "docs/archive/"
- skills_dir: "skills/sdd/"

## SDD 配置
- flow_engine: "sdd/sdd-orchestrator"
- default_flow_level: "Standard"

## 项目约束
- constitution: "CONSTITUTION.md"
- quirks: "QUIRKS.md"

## SDD Profile 映射
sdd_config:
  role_to_profile:
    po: "sdd-po"
    ba: "sdd-ba"
    architect: "sdd-architect"
    coder: "sdd-coder"
    reviewer: "sdd-reviewer"
    qa: "sdd-qa"
  profile_enabled: true
