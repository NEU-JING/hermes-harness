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

探索模式是 SDD 的可选前置入口。在正式进入 `/sdd start` 之前，提供一个"思考空间"进行需求探索、代码调研和方案对比。**不创建任何产物**，帮助用户理清思路后再决定是否进入 SDD。

**触发**：`/explore`。需求已明确时直接 `/sdd start`。

## Workflow

**Step 1**: 用户输入探索主题（自然语言），或直接开始对话。

**Step 2**: 自由对话 — 不创建文件、不污染 `docs/`、支持代码库分析/方案对比/图表。

**Step 3**: 退出 — "放弃"→ 清理状态不留痕迹；"/sdd start"→ 进入 PO_ENTRY（探索摘要可选传递）。

**Step 4**: 可选摘要传递 — 写入临时摘要文件供 PO Agent 参考：
```
探索发现:
- 目标: {需求}  代码库调研: {关键信息}
- 方案对比: {结论}  推荐: {方案}
```

**Step 5**: 中断恢复 — 重要交互后追加摘要到 `~/.hermes/explore/{change_id}/session.md`；重新进入时检查存在则读取上次摘要继续；正常退出时清理。

## Exploration Guide

加载 `skill_view(name='explore-agent', file_path='references/explore-guide.md')` 获取引导问题。

## Output

- 无持久化产物（除非进入 SDD）
- 退出方式：放弃 或 → PO_ENTRY（带摘要可选）

## Quality Standards

- [ ] 不创建任何文件或目录
- [ ] 用户随时可退出，不留痕迹
- [ ] 中断后恢复上次摘要
