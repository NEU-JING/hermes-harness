# PRD — OpenSpec 启发改进（Hermes-Harness v2.2）

> **Product Requirements Document**
> 变更 ID：003-openspec-improvements
> 版本：1.0 | 最后更新：2026-06-08

---

## 1. 背景

基于对 OpenSpec（53.5k stars, Fission-AI）的深度调研，对比分析发现 Hermes-Harness 在工程规范严谨性上具有显著优势（状态机、门禁、多 Agent 角色等），但在以下 4 个方面存在改进空间。

OpenSpec 的成功（社区规模、Agent 无关性、低门槛启动）为 Hermes-Harness 提供了明确的改进方向。

---

## 2. 目标

通过 4 个改进点，让 Hermes-Harness 在**保持工程规范优势**的前提下，降低使用门槛、提升通用性、建立生态基础。

**不改的底线：**
- 18 状态状态机架构不变
- 5 级 Lint + R10 门禁不变
- 6 角色 Agent 分工不变
- TDD / PR 合规 / 熔断机制不变

---

## 3. 改进点定义

### P3 — 探索模式（/explore Brainstorming 入口）

**问题：** 当前用户需求直接进入 PO 阶段 `PO_ENTRY`，无发散→收敛环节。用户可能还没想清楚就开始写 PRD，导致后期返工。

**目标：** 增加类似 OpenSpec `/opsx:explore` 的探索模式，在正式进入 SDD 流程前提供一个轻量"思考空间"。

**关键思路：**
- 新增 `/explore` slash command（或 agent prompt 入口）
- 不创建产物，仅对话探索
- 探索完成后可选择：放弃 / 进入 `/sdd start`
- 支持代码库分析、方案对比、可视化图表

**对比 OpenSpec：**
- OpenSpec `/opsx:explore` 支持自由对话 + 代码库搜索 + 选项对比 + 过渡到 /opsx:propose
- Hermes 已有 Architect 阶段的 Brainstorming，但时机太晚（在 PRD+Spec 之后）
- 改进方向：将 Brainstorming 提前到流程**最前端**，作为可选入口

### P4 — Spec 格式兼容（GIVEN/WHEN/THEN）

**问题：** 当前 Hermes spec.md 格式为自定义格式，非通用标准。使用者在不同项目之间切换时需要重新学习。

**目标：** 支持 OpenSpec 的 GIVEN/WHEN/THEN 场景格式，同时保持对老格式的兼容。

**关键思路：**
- spec.md 同时支持 Hermes 原生格式 和 GIVEN/WHEN/THEN 格式
- AC 检查时两种格式都支持提取验收条件
- 通过 `convention_overrides` 让项目选择偏好格式

**对比 OpenSpec：**
- OpenSpec 使用 `SHALL/MUST/SHOULD` (RFC 2119) + GIVEN/WHEN/THEN
- OpenSpec 格式已被社区广泛接受，53.5k stars 用户熟悉
- 格式兼容可降低学习曲线，吸引 OpenSpec 用户迁移

### P7 — Telemetry 匿名统计

**问题：** 无使用数据，无法了解哪些 Skills 被使用、哪些阶段用时最长、哪些门禁经常触发。

**目标：** 可选匿名使用统计，帮助团队优化流程。

**关键思路：**
- 仅收集命令名称和阶段转换，**不收集**文件内容、路径、项目名
- 默认关闭，用户通过 `telemetry: enabled: true` 启用
- 数据本地保存，定期可查看统计报告
- 参考 OpenSpec 的 `OPENSPEC_TELEMETRY=0` 和 `DO_NOT_TRACK=1` 退出机制

**对比 OpenSpec：**
- OpenSpec 收集命令名和版本号
- Hermes 可以做得更好：本地化存储 + 可视化面板

### P8 — Spec Delta 语义

**问题：** 当前变更前后 spec 的差异靠人工阅读对比，无结构化 diff。

**目标：** 引入 Delta Spec 模式，变更只记录增删改，而非全量重写 spec.md。

**关键思路：**
- 每个 Change 内的 spec 目录只存放 **delta 文件**（相对于基线 spec 的变更）
- 归档时自动合并 delta 到基线 spec
- 支持 diff 视图：归档前后基线对比
- 兼容 OpenSpec 的 `openspec/changes/<name>/specs/` 目录结构

**对比 OpenSpec：**
- OpenSpec 的 delta spec 是核心设计理念之一
- OpenSpec 在 archive 时执行 `sync` 将 delta 合并到主 specs
- Hermes 当前 `docs/current/` 作为基线，但缺少结构化 diff

---

## 4. 非功能需求

| 需求 | 说明 |
|------|------|
| **向后兼容** | 所有改进必须对现有 SDD 流程零破坏 |
| **渐进式采用** | 每项改进可单独启用，不需要一步到位 |
| **低 Token 开销** | 新增 Skill 的 SKILL.md 控制在 ~70 行 |
| **不增加门禁** | 这些改进不引入新的强制门禁（telemetry 除外，但可选） |

---

## 5. Phase 划分

| Phase | 改进点 | 复杂度 | 前置依赖 |
|:-----:|--------|:------:|:--------:|
| 1 | **P3 探索模式** — `/explore` 入口 | ⭐⭐ | 无 |
| 2 | **P4 Spec 格式兼容** — GIVEN/WHEN/THEN | ⭐⭐⭐ | P3（共享入口体验） |
| 3 | **P8 Spec Delta 语义** — 结构化 diff | ⭐⭐⭐⭐ | P2（依赖 spec 格式统一） |
| 4 | **P7 Telemetry** | ⭐⭐ | 无（可并行于 P1） |

---

## 6. 成功指标

- P3: 用户可通过 `/explore` 完成一次完整的需求收敛，再进入 `/sdd start`
- P4: 新项目可选择 GIVEN/WHEN/THEN 格式编写 spec，与 Hermes 原生格式等价
- P7: 团队可查看最近 30 天的流程统计（阶段耗时、门禁触发率、修复轮次分布）
- P8: 归档时自动生成 spec diff 报告，人工可读
