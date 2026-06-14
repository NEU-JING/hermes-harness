# SDD Core Specification

> **基线版本**: v2.1.0
> **归档来源**: change 003-openspec-improvements
> **归档时间**: 2026-06-14T13:47:24+08:00

---

## 1. 探索模式

### Requirement: 探索模式入口

**概述**: 用户通过 `/explore` 进入自由对话模式进行需求探索，不创建任何文件。

**AC 列表**:

#### Scenario AC1: 启动 /explore 进入自由对话
- **WHEN** 用户输入 `/explore`
- **THEN** Agent 进入探索模式，不创建任何文件或目录

#### Scenario AC2: 代码库调研
- **WHEN** 用户在探索模式中要求代码库调研
- **THEN** Agent 读取文件并返回分析

#### Scenario AC3: 方案对比
- **WHEN** 用户要求方案对比
- **THEN** Agent 输出结构化对比表

#### Scenario AC4: 放弃探索
- **WHEN** 用户说"放弃"或"取消"
- **THEN** Agent 清理对话状态，不留任何产物

#### Scenario AC5: 进入 SDD
- **WHEN** 用户说"/sdd start"或"进入开发"
- **THEN** Agent 启动 PO_ENTRY，探索摘要可选传递

#### Scenario AC6: 中断恢复
- **WHEN** 探索被意外中断且用户重新进入 `/explore`
- **THEN** Agent 读取上次会话摘要并询问是否继续

---

## 2. Spec 格式统一

### Requirement: OpenSpec WHEN/THEN 格式

**概述**: BA Agent 使用 OpenSpec WHEN/THEN + AND 链格式，AC 编号嵌入 `#### Scenario AC{n}:`。

#### Scenario AC7: OpenSpec 格式识别
- **WHEN** Spec 包含 `#### Scenario AC{n}:` 格式
- **THEN** Lint 正确提取 AC 编号

#### Scenario AC8: 单格式迁移
- **WHEN** 存量项目接入新版 BA Agent
- **THEN** 存量 Hermes 表格式重写为 OpenSpec 格式

#### Scenario AC9: 迁移窗口配置
- **WHEN** 项目需要过渡期
- **AND** 通过 `convention_overrides.spec_format` 声明
- **THEN** Orchestrator 提示而非阻断

#### Scenario AC10: 默认格式
- **WHEN** 无 `convention_overrides.spec_format` 配置
- **THEN** BA Agent 使用 OpenSpec WHEN/THEN + AND 链格式

#### Scenario AC11: AC 提取正确性
- **WHEN** QA 对比 Lint 提取的 AC 列表与 Spec 声明
- **THEN** 两者完全一致

---

## 3. Spec Delta 语义

### Requirement: Delta Spec 版本管理

**概述**: 变更通过 Delta 结构记录 specs 的增量修改，归档时合并到基线。

#### Scenario AC12: Delta 目录创建
- **WHEN** 新 Change 创建
- **THEN** 在 `changes/{id}/specs/<capability>/` 创建 Delta 结构

#### Scenario AC13: 增量修改
- **WHEN** 已有 AC 被修改
- **THEN** 在 Delta 中标记为 MODIFIED，包含新旧值

#### Scenario AC14: 新增 AC
- **WHEN** 新增 AC
- **THEN** 在 Delta 中标记为 ADDED，包含完整内容

#### Scenario AC15: 删除 AC
- **WHEN** 删除 AC
- **THEN** 在 Delta 中标记为 REMOVED，包含 Reason 和 Migration 字段

#### Scenario AC16: 归档合并
- **WHEN** 归档时
- **THEN** Delta 合并到基线，生成 sync 报告

#### Scenario AC17: 向后兼容
- **WHEN** 存量 Change 无 Delta 结构
- **THEN** 不报错，跳过 Spec Sync

---

## 4. Telemetry 匿名统计

### Requirement: Telemetry 子系统

**概述**: 编排器在阶段转换时自动记录匿名统计数据，默认关闭。

#### Scenario AC18: 默认关闭
- **WHEN** sdd-init 创建新项目
- **THEN** AGENTS.md 中 telemetry 配置为注释状态（enabled: false）

#### Scenario AC19: 显式启用
- **WHEN** 用户设置 `telemetry: enabled: true`
- **THEN** 编排器在阶段转换时记录 telemetry 事件

#### Scenario AC20: 数据范围限制
- **WHEN** 记录 telemetry 事件
- **THEN** 仅记录命令名、阶段名、耗时

#### Scenario AC21: 本地存储
- **WHEN** 记录 telemetry 事件
- **THEN** 写入 `~/.hermes/telemetry/{change_id}/events.ndjson`，30天清理

#### Scenario AC22: 退出机制
- **WHEN** 设置 `HERMES_TELEMETRY_DISABLE=1`
- **THEN** 编排器立即停止记录

#### Scenario AC23: 隐私合规
- **WHEN** 设置 `DO_NOT_TRACK=1`
- **THEN** 覆盖任何配置，停止记录
