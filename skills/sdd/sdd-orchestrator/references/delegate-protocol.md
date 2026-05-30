# Agent Delegation Protocol

> **版本**: 2.0  
> **日期**: 2026-05-30

---

## 协议概述

编排器通过 `delegate_task` 调用各角色Agent。**编排器本身不直接执行任务，只负责调度和状态管理**。

---

## 委托规范

### 基础委托格式

```yaml
delegate_task:
  goal: "[明确的目标描述]"
  
  context: |
    ## 变更上下文
    change_id: "{change_id}"
    current_state: "{current_state}"
    flow_level: "{Quick|Standard|Enhanced}"
    incremental_mode: "{true|false}"
    
    ## 前置产物（必须提供完整路径）
    prerequisites:
      - type: "prd"
        path: "docs/changes/{change_id}/prd.md"
      - type: "spec"
        path: "docs/changes/{change_id}/spec.md"
      # ... 根据阶段提供
    
    ## 约束条件（来自AGENTS.md/CONSTITUTION）
    constraints:
      tech_stack: "{from AGENTS.md}"
      naming_conventions: "{from AGENTS.md}"
      disabled_rules: "{from AGENTS.md convention_overrides}"
    
    ## 产出要求
    deliverables:
      - file: "docs/changes/{change_id}/{output_file}"
        template: "{skill_name}/templates/{template_file}"
        required_sections:
          - "section1"
          - "section2"
  
  toolsets: ["file", "terminal", "skills"]
  
  role: "leaf"
```

---

## 各阶段委托详情

### PO阶段委托

```yaml
delegate_task:
  goal: "产出PRD文档：定义变更的背景、目标、功能范围、非目标、成功指标、用户场景"
  
  context: |
    change_id: "{change_id}"
    description: "{用户输入的变更描述}"
    
    ## 输出要求
    deliverable:
      file: "docs/changes/{change_id}/prd.md"
      template: "po-agent/templates/prd-template.md"
      
    ## PRD必须包含的章节
    required_sections:
      - "背景与目标"
      - "目标用户"
      - "功能范围（功能表格）"
      - "非目标（明确不做）"
      - "成功指标（可量化）"
      - "用户场景（User Story）"
    
    ## 约束
    constraints:
      - "每个功能必须有明确的验收标准暗示"
      - "非目标必须具体，不能模糊"
  
  toolsets: ["file", "skills"]
  
  role: "leaf"
```

**编排器后续动作**:
1. 等待delegate返回
2. 检查产出物存在 → `PO_ENTRY → PO_CHECK`

---

### BA阶段委托

```yaml
delegate_task:
  goal: "根据PRD产出Spec文档：细化需求清单，编写AC（Given-When-Then格式）"
  
  context: |
    change_id: "{change_id}"
    
    ## 输入
    prerequisites:
      - type: "prd"
        path: "docs/changes/{change_id}/prd.md"
    
    ## 输出
    deliverable:
      file: "docs/changes/{change_id}/spec.md"
      template: "ba-agent/templates/spec-template.md"
    
    ## Spec必须包含
    required_sections:
      - "需求清单（R1-RN）"
      - "每个需求的AC（Given-When-Then）"
      - "边界情况"
      - "数据契约（输入/输出格式）"
    
    ## AC格式要求
    ac_format: |
      ### R{N}: {需求标题}
      
      **AC{N}.1**: {场景描述}
      - **Given**: {前置条件}
      - **When**: {操作}
      - **Then**: {预期结果}
    
    ## 约束
    constraints:
      - "每个PRD功能点必须有对应的R需求"
      - "每个R需求至少2个AC（正常+异常）"
      - "AC必须是可测试的（有明确的Then断言）"
  
  toolsets: ["file", "skills"]
  
  role: "leaf"
```

---

### Architect阶段委托

```yaml
delegate_task:
  goal: "根据Spec产出Design文档和Tasks拆分"
  
  context: |
    change_id: "{change_id}"
    
    ## 输入
    prerequisites:
      - type: "spec"
        path: "docs/changes/{change_id}/spec.md"
    
    ## 输出
    deliverables:
      - file: "docs/changes/{change_id}/design.md"
        template: "architect-agent/templates/design-template.md"
        required_sections:
          - "技术方案（至少2种备选）"
          - "方案对比与选择"
          - "架构设计（模块/接口/数据流）"
          - "关键技术决策"
          - "产出物清单（新增/修改/删除的文件）"
      
      - file: "docs/changes/{change_id}/tasks.md"
        template: "architect-agent/templates/tasks-template.md"
        required_sections:
          - "Task列表（按业务场景拆分）"
          - "每个Task可独立部署"
          - "Task依赖关系"
    
    ## 增量模式
    incremental_mode: "{true|false}"
    phase_marking_required: "{incremental_mode}"
    
    ## 约束
    constraints:
      - "每个Task对应1个可独立测试的功能"
      - "Task粒度：1-2天工作量"
      - "Task间通过接口契约交互"
  
  toolsets: ["file", "terminal", "skills"]
  
  role: "leaf"
```

---

### Coder阶段委托

**注意**: Coder阶段是**按Task逐个委托**。

```yaml
# 为每个Task调用一次
delegate_task:
  goal: "实现Task {task_id}: {task_name} — 遵循TDD（RED-GREEN-REFACTOR）"
  
  context: |
    change_id: "{change_id}"
    task_id: "T{N}"
    task_name: "{task_name}"
    
    ## 输入
    prerequisites:
      - type: "design"
        path: "docs/changes/{change_id}/design.md"
      - type: "tasks"
        path: "docs/changes/{change_id}/tasks.md"
        section: "T{N} 部分"
      - type: "spec"
        path: "docs/changes/{change_id}/spec.md"
        relevant_ac: "[AC编号列表]"
    
    ## TDD流程
    tdd_workflow:
      - step: "RED"
        action: "写测试（先写测试，确保失败）"
      - step: "GREEN"
        action: "实现代码（最小改动使测试通过）"
      - step: "REFACTOR"
        action: "重构（保持测试通过，优化代码）"
      - step: "COMMIT"
        action: "提交commit（清晰的消息）"
    
    ## 代码约束
    constraints:
      tech_stack: "{from AGENTS.md}"
      naming: "{from AGENTS.md conventions}"
      max_function_lines: 50
      test_coverage: "必须"
    
    ## 产出
    deliverables:
      - type: "commits"
        branch: "feat/{change_id}"
      - type: "task_report"
        append_to: "docs/changes/{change_id}/completion-report.md"
  
  toolsets: ["file", "terminal", "skills"]
  
  role: "leaf"
```

**编排器控制逻辑**:
```python
# 解析tasks.md获取所有Task
 tasks = parse_tasks_md(f"docs/changes/{change_id}/tasks.md")

for task in tasks:
    # 委托单个Task
    result = delegate_task(
        goal=f"实现Task {task.id}",
        context={...task context...}
    )
    
    if result.success:
        mark_task_done(task.id)
    else:
        # Task失败处理
        record_task_failure(task.id, result.error)
        # 询问用户是否继续或阻断
```

---

### Reviewer阶段委托

```yaml
delegate_task:
  goal: "三阶段评审：Spec合规检查、代码质量检查、架构一致性检查"
  
  context: |
    change_id: "{change_id}"
    
    ## 输入
    prerequisites:
      - type: "spec"
        path: "docs/changes/{change_id}/spec.md"
      - type: "design"
        path: "docs/changes/{change_id}/design.md"
      - type: "completion_report"
        path: "docs/changes/{change_id}/completion-report.md"
      - type: "code"
        branch: "feat/{change_id}"
        commits: "[commit列表]"
    
    ## 三阶段评审
    review_phases:
      - name: "Phase 1: Spec合规"
        checks:
          - "所有AC有测试覆盖"
          - "功能实现与Spec一致"
          - "Out of Scope功能未实现"
      
      - name: "Phase 2: 代码质量"
        checks:
          - "DRY：无重复代码"
          - "YAGNI：无过度设计"
          - "函数长度 ≤ 50行"
          - "命名清晰（不缩写）"
          - "错误处理完整"
          - "日志适当"
          - "无TODO/FIXME（除非标issue）"
      
      - name: "Phase 3: 架构一致性"
        checks:
          - "模块划分与Design一致"
          - "接口定义与Design一致"
          - "数据流与Design一致"
          - "关键技术决策被遵循"
    
    ## 严重级别定义
    severity_levels:
      CRITICAL: "必须修复才能通过"
      MAJOR: "应修复，可条件通过"
      MINOR: "建议修复"
      INFO: "仅供参考"
    
    ## 输出
    deliverable:
      file: "docs/changes/{change_id}/review-report.md"
      template: "reviewer-agent/templates/review-report.md"
      required_sections:
        - "评审结论（passed/conditional/failed）"
        - "发现的问题（按严重级别排序）"
        - "修复建议"
        - "AC覆盖检查"
  
  toolsets: ["file", "terminal", "skills", "github"]
  
  role: "leaf"
```

---

### QA阶段委托

```yaml
delegate_task:
  goal: "执行测试验证：AC覆盖检查、测试执行、环境差异检查"
  
  context: |
    change_id: "{change_id}"
    
    ## 输入
    prerequisites:
      - type: "spec"
        path: "docs/changes/{change_id}/spec.md"
      - type: "review_report"
        path: "docs/changes/{change_id}/review-report.md"
    
    ## QA检查
    qa_checks:
      - name: "AC覆盖矩阵"
        action: "建立AC↔测试的映射表"
        verify: "每个AC至少1个测试"
      
      - name: "测试执行"
        types:
          - "单元测试"
          - "集成测试"
          - "E2E测试（Standard/Enhanced）"
        verify: "所有测试通过"
      
      - name: "环境差异"
        check: "检查test环境vs生产环境的差异"
        if_different: "记录差异及影响"
      
      - name: "熔断检查"
        verify: "本次变更QA失败次数 < 4"
  
    ## 输出
    deliverable:
      file: "docs/changes/{change_id}/qa-report.md"
      template: "qa-agent/templates/qa-report.md"
      required_sections:
        - "AC覆盖矩阵"
        - "测试结果统计"
        - "环境差异说明"
        - "结论（passed/failed）"
  
  toolsets: ["file", "terminal", "skills"]
  
  role: "leaf"
```

---

## 委托结果处理

### 成功处理

```python
def handle_delegate_success(result, current_state, next_state):
    """Agent委托成功后的处理"""
    
    # 1. 验证产出物
    for deliverable in result.deliverables:
        if not file_exists(deliverable.path):
            return handle_delegate_failure(
                error=f"产出物缺失: {deliverable.path}",
                current_state=current_state
            )
    
    # 2. 更新状态文件
    update_sdd_state({
        "current_state": next_state,
        "previous_state": current_state,
        "state_history": append_transition(current_state, next_state),
        "updated_at": now()
    })
    
    # 3. 触发门禁检查（如果是EXECUTING → CHECK转换）
    if is_check_state(next_state):
        return execute_phase_gate(current_state, next_state)
    
    # 4. 等待状态：提示用户
    if is_waiting_state(next_state):
        output_user_prompt(next_state)
    
    return StateTransitionResult(success=True, state=next_state)
```

### 失败处理

```python
def handle_delegate_failure(error, current_state):
    """Agent委托失败后的处理"""
    
    # 1. 记录失败
    record_failure(current_state, error)
    
    # 2. 检查失败次数
    failure_count = get_failure_count(current_state)
    
    if failure_count >= MAX_FAILURES:
        # 转为BLOCKED状态
        update_sdd_state({
            "current_state": "BLOCKED",
            "blocked_reason": error,
            "failure_history": get_failure_history()
        })
        output_blocked_message(error)
        return StateTransitionResult(success=False, state="BLOCKED")
    
    # 3. 保持在当前状态，允许重试
    output_retry_prompt(current_state, error, failure_count)
    return StateTransitionResult(success=False, state=current_state)
```

---

## 委托上下文完整性检查清单

编排器在委托前必须确认：

- [ ] change_id 已生成且有效
- [ ] 当前状态与期望状态一致
- [ ] 所有前置产物文件存在
- [ ] 产物路径格式正确
- [ ] AGENTS.md约束已加载
- [ ] 输出目录已创建

---

## 快速参考

| 阶段 | Skill | 输入产物 | 输出产物 |
|------|-------|---------|---------|
| PO | po-agent | 变更描述 | prd.md |
| BA | ba-agent | prd.md | spec.md |
| Architect | architect-agent | spec.md | design.md + tasks.md |
| Coder | coder-agent | tasks.md + design.md | commits + completion-report.md |
| Reviewer | reviewer-agent | spec + design + code | review-report.md |
| QA | qa-agent | spec + review-report | qa-report.md |
