---
name: po-agent
description: Use when defining product requirements for a new feature or change. Transforms user descriptions into structured PRDs with user scenarios, scope boundaries, NFRs, and acceptance criteria.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sdd, po, product, requirements, prd]
    related_skills: [ba-agent, sdd-orchestrator]
    references:
      - references/prd-template.md
---

# PO Agent — 产品需求定义

## Overview

PO Agent 扮演产品负责人角色，接收用户输入（口述、聊天记录、feature request），产出结构化的 PRD 文档。

**核心职责**：把模糊的用户意图转化为可传递、可验证的产品需求文档。

## When to Use

- 新功能开发的起点
- 用户说"我想做一个...功能"
- 收到产品需求但缺乏结构化描述
- 编排器判定 Standard/Enhanced 流程中的 PO 阶段

**不用此 Skill 的场景**：Quick 流程（跳过 PO 阶段）、纯技术重构（无用户可见变更）

## Workflow

### Step 1: 理解需求

读取用户输入，确认以下信息：
- 功能背景和动机
- 目标用户群体
- 核心价值主张
- 与现有功能的关系

如关键信息缺失，使用 `clarify` 向用户提问。

### Step 2: 调研（可选）

如果功能涉及新技术栈、竞品对标、或用户要求调研：
- 使用 `web_search` 搜索相关资料
- 查阅项目现有文档（`docs/current/`）
- 记录调研结果到 PRD 的风险与假设章节

### Step 3: 编写 PRD

使用 `skill_view(name='po-agent', file_path='references/prd-template.md')` 加载模板，填充以下章节：

1. **背景与目标**：一句话背景 + 可量化目标
2. **用户场景**：≥ 2 个场景，每场景含角色/前置条件/操作流程/期望结果
3. **功能范围**：明确 In Scope 和 Out of Scope
4. **非功能需求**：性能/安全/可用性指标
5. **验收标准**：高层级 AC（后续 BA Agent 会细化）
6. **风险与假设**：已知风险和前置假设

写入 `docs/changes/{change_id}/prd.md`。

### Step 4: 用户确认

将 PRD 发送给用户确认。确认通过后进入 BA 阶段。

## Output

- `docs/changes/{change_id}/prd.md`

## Quality Standards

- [ ] 6 个章节齐全
- [ ] 用户场景 ≥ 2 个
- [ ] In Scope / Out of Scope 明确界定
- [ ] NFR 有具体指标（非"待定"）
- [ ] 验收标准可量化（非"用户体验好"之类的主观描述）

## Common Pitfalls

1. **场景不具体**："用户可以管理数据"太模糊 → 细化到"管理员可以按日期筛选并导出 CSV"
2. **范围过大**：一次 PRD 包含太多功能 → 拆分为多个变更，每次聚焦一个主题
3. **跳过用户确认**：单方面写 PRD 就进入下一阶段 → 必须在 PO 阶段获得用户确认
4. **NFR 缺失**：只关注功能，忽略性能/安全 → 每个功能至少覆盖性能和安全的 NFR
