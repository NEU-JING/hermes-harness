---
name: explore-agent
description: Pre-SDD exploration mode — think through ideas, investigate codebase, and compare approaches before committing to a formal SDD change. Activated via /explore.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sdd, explore, brainstorming, pre-sdd]
    related_skills: [po-agent, sdd-orchestrator]
    references:
      - references/explore-guide.md
---

# Explore Agent — 探索模式

## Overview

探索模式是 SDD 流程的可选前置入口。在用户正式进入 `/sdd start` 之前，提供一个轻量"思考空间"进行需求探索、代码调研和方案对比。

**核心职责**：自由对话，不创建任何产物，帮助用户理清思路后再决定是否进入 SDD。

## When to Use

- 用户输入 `/explore` 时
- 需求模糊，需要先探索再决定
- 需要对代码库进行分析
- 需要对比多个技术方案

**不用此 Skill 的场景**：需求已明确 → 直接进入 `/sdd start`

## Workflow

### Step 1: 接收探索主题

用户输入探索主题（自然语言），或直接开始对话。

### Step 2: 自由对话

- 不创建任何文件（proposal/spec/design/tasks）
- 不污染 `docs/` 目录
- 支持：代码库分析、方案对比、可视化图表

### Step 3: 退出探索

| 用户指令 | 行为 |
|---------|------|
| "放弃" 或 "取消" | 清理对话状态，不留任何产物 |
| `/sdd start` 或 "进入开发" | 探索摘要（可选）传递给 PO Agent 作为 PRD 输入 |

### Step 4: 探索摘要传递（可选）

如果用户选择进入 SDD 流程，可将探索中的关键发现作为 PRD 的输入源：

```
探索发现:
- 目标: {用户原始需求}
- 代码库调研: {发现的关键信息}
- 方案对比: {对比结论}
- 推荐方案: {推荐}
```

## Exploration Guide

加载 `skill_view(name='explore-agent', file_path='references/explore-guide.md')` 获取探索引导问题。

## Output

- 无持久化产物（除非用户选择进入 SDD）
- 探索结束后：放弃 或 → PO_ENTRY（带探索摘要可选）

## Quality Standards

- [ ] 不创建任何文件或目录
- [ ] 探索期间可使用 web_search、文件读取等工具
- [ ] 用户随时可退出，不留痕迹
- [ ] 进入 SDD 时探索摘要可选传递
