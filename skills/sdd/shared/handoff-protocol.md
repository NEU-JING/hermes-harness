# SDD 角色交接协议

> 定义 7 个 SDD 角色之间的输入/输出契约，确保阶段切换时信息完整传递。

---

## 角色链

```
PO → BA → Architect → Coder → Reviewer → QA → Orchestrator
```

## 各角色交接契约

### PO → BA

**PO 产出**：PRD（`docs/changes/{id}/prd.md`）

**PRD 必须包含**：
- 背景与目标
- 用户场景（≥2 个）
- 功能范围（In Scope / Out of Scope）
- 非功能需求（NFR）
- 验收标准（高层级）
- 风险与假设

**BA 接收条件**：
- PRD 经用户确认（PO 阶段门禁通过）
- PRD 六章节齐全

**交接失败处理**：PRD 章节缺失 → 打回 PO 补充

---

### BA → Architect

**BA 产出**：Spec（`docs/changes/{id}/spec.md`）

**Spec 必须包含**：
- 功能概述
- 详细需求（≥3 条）
- Acceptance Criteria（每条 AC 编号为 `AC{n}`，可测试、可量化）
- 数据模型（如涉及）
- API 契约（如涉及）
- 非功能需求细化

**Architect 接收条件**：
- Spec 经用户确认（BA 阶段门禁通过）
- AC 编号连续、格式规范
- 每条 AC 可独立验证

**交接失败处理**：
- AC 编号不连续 → 打回 BA 修正
- AC 不可测试 → 打回 BA 细化

---

### Architect → Coder

**Architect 产出**：
1. Design（`docs/changes/{id}/design.md`）
2. Tasks（`docs/changes/{id}/tasks.md`）

**Design 必须包含**：
- 技术方案对比（≥2 方案，Standard/Enhanced 流程）
- 选型理由
- 架构图/数据流
- 详细实现设计（Coder Agent 照做即可）
- 产出物清单

**Tasks 必须包含**：
- 每 Task：估时、依赖、AC 覆盖、产出文件路径
- 执行顺序（依赖图）
- 验证命令

**Coder 接收条件**：
- Design 经用户确认（Architect 阶段门禁通过）
- 每 Task 有 exact 文件路径
- 每 Task 有验证步骤

**交接失败处理**：
- Task 粒度过大（单 Task > 15min）→ 打回 Architect 拆分
- 文件路径模糊（如 "创建配置文件"）→ 打回 Architect 精确化

---

### Coder → Reviewer

**Coder 产出**：
1. 代码变更（Git diff）
2. 测试（含 TDD 过程：RED → GREEN → REFACTOR）
3. Task 完成报告（每 Task 一个）

**Task 完成报告必须包含**：
- 修改的文件列表
- 通过的测试数
- 未覆盖的 AC（如有，需说明原因）

**Reviewer 接收条件**：
- 所有 Task 完成且 commit
- 测试全部通过
- 无未解决的 TODO/FIXME（除非标注为已知限制）

**交接失败处理**：
- 测试未全量通过 → 打回 Coder
- Task 报告缺失 → 打回 Coder 补报告

---

### Reviewer → QA

**Reviewer 产出**：评审报告（`docs/changes/{id}/review-report.md`）

**评审报告必须包含**：
- 评审结论（通过 / 有条件通过 / 不通过）
- 三阶段评审结果（Spec 合规 / 代码质量 / 架构一致性）
- 发现的问题清单（含严重级别：CRITICAL / MAJOR / MINOR / INFO）
- 修复建议

**QA 接收条件**：
- 评审结论为 "通过" 或 "有条件通过"
- 所有 CRITICAL 问题已修复
- MAJOR 问题有明确的修复计划

**交接失败处理**：
- 评审结论 "不通过" → 打回 Coder 修复 → 重新 Review
- CRITICAL 未修复 → 阻断，不允许进入 QA

---

### QA → Orchestrator（用户验收前）

**QA 产出**：QA 报告（`docs/changes/{id}/qa-report.md`）

**QA 报告必须包含**：
- AC 覆盖矩阵（每 AC → E2E 用例映射）
- 测试结果（通过/失败/跳过，含环境信息）
- 环境差异标记（CI-only 测试的标记验证）
- 修复循环记录（如有）
- 熔断状态（是否触发熔断）

**用户验收条件**：
- QA 报告结论为 "通过"
- AC 全覆盖（无缺失）
- 修复循环 ≤ 2 轮（超限触发熔断）

**交接失败处理**：
- AC 未全覆盖 → 打回 Coder（标记缺失 AC 编号）
- 修复循环 > 2 轮 → 触发熔断，人工介入

---

### Orchestrator → 归档（用户验收后）

**Orchestrator 产出**：归档完成状态

**归档条件**：
- 用户验收通过
- `docs/changes/{id}/` 目录结构完整
- sdd-structure-lint 全量通过
- 变更目录已移至 `docs/archive/{id}/`
- `docs/current/` 已更新

**归档失败处理**：
- 目录结构不完整 → 补全文件后重试归档
- lint 不通过 → 修复后重试归档

---

## 修复循环规则

| 打回原因 | 最大自动修复轮次 | 超限行为 |
|---------|:---:|---------|
| 需求不清晰（PO/BA 阶段） | 2 | 人工澄清 |
| 设计缺陷（Architect 阶段） | 2 | 人工决策 |
| 代码缺陷（Coder 阶段） | 2 | 熔断，人工 review |
| 测试不足（QA 阶段） | 2 | 熔断，人工验收 |

**总自动循环上限**：6 轮（全流程累计）。超限后不做自动决策，标记为 "需人工介入"。

---

## 中断恢复

编排器中断后，从以下状态恢复：

1. 读取 `docs/changes/{id}/.sdd-state.json`
2. 确定当前阶段
3. 检查当前阶段产物是否存在
4. 如产物完整 → 从该阶段继续
5. 如产物不完整 → 回退到上一阶段
