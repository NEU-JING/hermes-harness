# Tasks: SDD Orchestrator v2.0.1 优化

## 任务列表

### T1: 精简 SKILL.md - State Machine 章节

**目标**: 将 State Machine 章节精简为摘要+链接形式

**步骤**:
1. 保留状态机概述和 ASCII 流程图
2. 保留状态转换表
3. 移除详细状态定义（每个状态的 entry/execution/exit）
4. 添加链接指向 references/state-machine.md

**产出**: SKILL.md 中 State Machine 章节精简完成

---

### T2: 精简 SKILL.md - Phase Gates 章节

**目标**: 将 Phase Gates 章节精简为摘要+链接形式

**步骤**:
1. 保留 Level 概述（L0-L3+R10）
2. 保留 Lint Level 映射表
3. 移除详细检查内容（每个 level 的检查项）
4. 添加链接指向 references/phase-gates.md

**产出**: SKILL.md 中 Phase Gates 章节精简完成

---

### T3: 精简 SKILL.md - Agent Delegation 章节

**目标**: 将 Agent Delegation 章节精简为摘要+链接形式

**步骤**:
1. 保留委托协议概述
2. 保留基础委托格式示例
3. 移除各阶段委托详情（PO/BA/Architect/Coder/Reviewer/QA）
4. 添加链接指向 references/delegate-protocol.md

**产出**: SKILL.md 中 Agent Delegation 章节精简完成

---

### T4: 更新 references/delegate-protocol.md - 增加前置检查

**目标**: 在委托协议中增加显式 skill_view() 要求

**步骤**:
1. 在"委托规范"章节后增加"前置检查"章节
2. 定义前置检查清单：必须调用 skill_view() 加载对应技能
3. 定义失败处理：加载失败时阻断流程
4. 更新各阶段委托示例，包含 skill_view() 调用

**产出**: delegate-protocol.md 增加前置检查章节

---

### T5: 验证和测试

**目标**: 验证修改后的文档有效

**步骤**:
1. 检查 SKILL.md 中所有 references/ 链接有效
2. 统计 SKILL.md 行数，确认减少 30%+
3. 验证 delegate-protocol.md 每个阶段都有 skill_view() 示例

**产出**: 验证报告
