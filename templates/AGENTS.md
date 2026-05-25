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
