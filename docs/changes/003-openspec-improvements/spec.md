# Spec — OpenSpec 启发改进

> **功能规格说明**
> 变更 ID：003-openspec-improvements
> 版本：1.0 | 最后更新：2026-06-08
> 基于 PRD：`docs/changes/003-openspec-improvements/prd.md`

---

## 功能概述

基于 OpenSpec 的调研发现，对 Hermes-Harness 进行 4 个改进：探索模式（P3）、Spec 格式兼容（P4）、Spec Delta 语义（P8）、Telemetry 匿名统计（P7）。所有改进保持向后兼容，不改变现有 SDD 核心流程。

---

## 详细需求

### Requirement: 探索模式 — /explore 入口（P3）

**描述**：在用户进入 `/sdd start` 之前，新增一个可选探索模式 `/explore`，让用户可以自由发散讨论需求、调研代码库、对比方案，再决定是否进入正式 SDD 流程。

**输入**：用户输入探索主题或问题（自然语言）

**输出**：
- `/explore` 启动时：进入自由对话模式，不创建任何产物
- 探索结束后：可选择「放弃」或「进入 SDD 流程」
- 选择进入 SDD 时：可将探索中的关键信息（可选）传递给 PO Agent 作为 PRD 输入

**约束**：
- 不创建中间产物，不污染 changes/ 目录
- 支持代码库分析和方案对比
- 探索期间可使用工具（web_search、文件读取等）

---

### Requirement: Spec 格式迁移 — OpenSpec WHEN/THEN（P4）

**描述**：将当前 Hermes spec.md 自定义表格式迁移到 OpenSpec WHEN/THEN + AND 链标准格式。迁移后 AC 检查使用正则 `/#### Scenario AC(\d+):/` 提取验收条件。

**输入**：BA Agent 或用户编写的 spec.md

**输出**：AC 检查时正确提取 `#### Scenario AC{n}:` 场景头和 WHEN/THEN/AND 条件

**约束**：
- 不保留 Hermes 原生表格式（不做双格式兼容）
- 存量项目 spec 以 OpenSpec 格式重写
- 通过 `convention_overrides` 声明迁移窗口期
- 默认格式 = `#### Scenario AC{n}:` + WHEN/THEN + AND 链

---

### Requirement: Spec Delta 语义（P8）

**描述**：引入 Delta Spec 模式，每个 Change 内的 spec 目录只存放增量变更（相对于基线 spec 的增删改），归档时自动合并到基线。

**输入**：Change 创建时从基线 `docs/current/spec.md` 复制为 base
**输出**：归档时自动生成 diff 报告，基线更新

**约束**：
- 现有 Change（无 delta 结构）向后兼容
- Delta 文件格式支持：新增、修改、删除三种操作
- 归档时自动执行基线合并

---

### Requirement: Telemetry 匿名统计（P7）

**描述**：可选匿名使用统计，收集命令名称和阶段转换数据，帮助团队优化流程效率。

**输入**：编排器在执行过程中自动记录阶段转换事件
**输出**：本地存储的统计数据，支持查询和可视化

**约束**：
- 默认关闭，用户必须显式启用
- 仅收集：命令名称、阶段转换、耗时
- 不收集：文件内容、路径、项目名称、用户身份
- 数据本地存储（不发送外部）
- 支持 `TELEMETRY_DISABLE=1` / `DO_NOT_TRACK=1` 退出

---

## Acceptance Criteria（验收标准）

### P3 — 探索模式

| 编号 | 场景 | Given | When | Then |
|:---:|------|-------|------|------|
| AC1 | 启动探索 | 用户未开始任何 SDD 流程 | 输入 `/explore` | 进入自由对话，无产物创建 |
| AC2 | 代码库调研 | 探索中 | 询问代码库结构 | Agent 读取文件返回分析 |
| AC3 | 方案对比 | 探索多方案 | 要求对比 | 输出结构化对比表 |
| AC4 | 放弃探索 | 无明确结论 | 用户说"放弃" | 退出探索，不留痕迹 |
| AC5 | 进入 SDD | 有明确结论 | 用户说"进入开发" | 启动 `/sdd start`，探索内容可选传递 |
| AC6 | 中断恢复 | 探索被意外中断 | 重新进入 `/explore` | 读取 `~/.hermes/explore/` 会话摘要，询问是否继续 |

### P4 — Spec 格式迁移

| 编号 | 场景 | Given | When | Then |
|:---:|------|-------|------|------|
| AC7 | OpenSpec 格式识别 | spec.md 使用 `#### Scenario AC{n}:` + WHEN/THEN 格式 | BA Agent 或 Lint 检查 AC | 正则 `/#### Scenario AC(\d+):/` 正确提取所有验收条件，编号连续 |
| AC8 | 单格式迁移 | 存量项目使用 Hermes 原生表格式 | 首次接入 SDD 新版本 | BA Agent 产出 OpenSpec 格式 spec，存量 spec 通过迁移窗口重写 |
| AC9 | 迁移窗口配置 | 项目需要过渡期 | 通过 `convention_overrides` 声明 | Orchestrator 在格式检查时给予迁移提示而非阻断 |
| AC10 | 默认格式 | 存量项目无 spec_format 配置 | BA Agent 产出 spec.md | 使用 OpenSpec `#### Scenario AC{n}:` + WHEN/THEN 格式 |
| AC11 | AC 提取正确性 | spec.md 使用新格式 | QA 对比 AC 提取结果 | AC 列表与 Spec 内容完全一致，编号连续，WHEN/THEN 条件完整 |

### P8 — Spec Delta 语义

| 编号 | 场景 | Given | When | Then |
|:---:|------|-------|------|------|
| AC12 | Delta 目录创建 | Change 创建时基线 spec 存在 | `/sdd start` 或 `/opsx:new` | Change 内创建 `specs/` 目录，自动复制基线为 base |
| AC13 | 增量修改 | 用户修改 Delta spec 中某条 AC | 修改完成 | Delta 文件标记该 AC 为「modified」，记录旧值和新值 |
| AC14 | 新增 AC | 用户新增一条不存在于基线的 AC | 写入 Delta spec 文件 | Delta 文件标记该 AC 为「added」 |
| AC15 | 删除 AC | 用户删除基线中的某条 AC | 从 Delta spec 移除 | Delta 文件标记该 AC 为「deleted」 |
| AC16 | 归档合并 | 归档触发 | `/opsx:archive` 或归档流程 | Delta 自动合并到基线，生成 diff 报告（added N / modified M / deleted D） |
| AC17 | 向后兼容 | 存量 Change 无 Delta 结构 | 归档流程 | 使用传统全量 spec 合并，不报错 |

### P7 — Telemetry

| 编号 | 场景 | Given | When | Then |
|:---:|------|-------|------|------|
| AC18 | 默认关闭 | 新项目首次初始化 | Hermes-Harness 初始化完成 | Telemetry 默认 disabled，不记录任何数据 |
| AC19 | 显式启用 | 用户在 AGENTS.md 或 config 中配置 `telemetry: enabled: true` | 编排器启动 | 开始记录命令名称和阶段转换事件 |
| AC20 | 数据范围限制 | Telemetry 已启用 | 用户执行 `/sdd start` 到归档全流程 | 仅记录：命令名 + 阶段名 + 耗时，不记录文件内容/路径/项目名 |
| AC21 | 本地存储 | Telemetry 数据已记录 | 用户查询统计 | 数据保存在本地，可查询最近 30 天的阶段耗时分布和门禁触发率 |
| AC22 | 退出机制 | Telemetry 已启用 | 设置环境变量 `TELEMETRY_DISABLE=1` | 立即停止统计，已有数据保留可查询 |
| AC23 | 隐私合规 | 环境中存在 `DO_NOT_TRACK=1` | 编排器启动 | Telemetry 自动禁用，覆盖项目配置 |

---

## 非功能需求细化

| 类别 | 原始 NFR | 细化指标 | 验证方式 |
|------|---------|---------|---------|
| 向后兼容 | 所有改进对现有 SDD 零破坏 | 存量项目走完整 SDD 流程，产物和状态无异常 | 在 AILP 项目上运行全部 5 个 Phase 验证 |
| 渐进式采用 | 每项改进可单独启用 | 改进不互相依赖导致连锁启用 | 逐一启用改进验证其他保持 disabled |
| Token 开销 | 新增 SKILL.md ≤ 70 行 | 探索模式提示词 ≤ 70 行 | wc -l 检查 |
| 隐私 | Telemetry 不收集敏感信息 | 数据字段清单审计通过 | 配置中定义 allowlist，不在列表内的字段自动排除 |
