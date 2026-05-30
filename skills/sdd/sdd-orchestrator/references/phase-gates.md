# Phase Gate Specification

> **版本**: 2.0  
> **日期**: 2026-05-30

---

## 门禁概述

Phase Gate 是状态转换的**强制检查点**。任何状态转换必须通过对应Level的lint检查，否则阻断。

**核心原则**：宁可过度检查，也不让有问题的产物进入下一阶段。

---

## Lint Level 定义

### Level 0: 初始化检查

**触发时机**: `IDLE → PO_ENTRY`

**检查内容**:
```yaml
checks:
  - name: "目录结构"
    command: |
      mkdir -p docs/changes/{change_id}
      test -d docs/changes/{change_id}
  
  - name: "状态文件初始化"
    verify: |
      .sdd-state.json 已创建
      包含: change_id, flow_level, current_state=IDLE
```

**失败处理**: 无法创建目录 → 输出权限错误，状态保持IDLE

---

### Level 1: 基础产物检查

**触发时机**: `PO_ENTRY → PO_CHECK`, `BA_ENTRY → BA_CHECK`

**检查内容**:
```yaml
checks:
  - name: "文件存在性"
    files:
      - "docs/changes/{change_id}/prd.md"  # PO阶段
      - "docs/changes/{change_id}/spec.md"  # BA阶段
  
  - name: "文件非空"
    verify: "文件大小 > 0 bytes"
  
  - name: "Markdown格式"
    verify:
      - "有标题 (#)"
      - "无语法错误"
  
  - name: "必填章节"
    prd_required:
      - "背景与目标"
      - "功能范围"
    spec_required:
      - "需求清单"
      - "AC列表"
```

**通过标准**: 所有检查项通过

**失败处理**: 
```
❌ Level 1 检查失败
缺失: prd.md
位置: docs/changes/{change_id}/
建议: 返回PO阶段重新生成
```

---

### Level 2: 设计产物检查

**触发时机**: `ARCHITECT_ENTRY → ARCHITECT_CHECK`, `CODER_ENTRY → CODER_CHECK`

**检查内容**:
```yaml
checks:
  - name: "Design文档"
    files:
      - "docs/changes/{change_id}/design.md"
      - "docs/changes/{change_id}/tasks.md"
  
  - name: "Design章节完整性"
    design_required:
      - "架构决策"
      - "数据流/时序图"
      - "接口定义"
  
  - name: "Tasks拆分合理性"
    tasks_required:
      - "Task列表非空"
      - "每个Task有编号(T1, T2...)"
      - "每个Task有明确产出"
      - "Task间依赖关系明确"
  
  - name: "增量模式标记"
    conditional: "如果incremental_mode=true"
    verify:
      - "Tasks中有Phase标记"
      - "每个Phase有交付标准"
      - "Phase间依赖关系明确"
```

**通过标准**: 所有检查项通过

**失败处理**: 返回Architect阶段修复

---

### Level 2.5: 代码产物检查

**触发时机**: `CODER_ENTRY → CODER_CHECK` 完成后

**检查内容**:
```yaml
checks:
  - name: "Git状态"
    command: "git status --porcelain"
    expect: "空（所有修改已提交）"
  
  - name: "分支检查"
    command: "git branch --show-current"
    expect: "feat/{change_id} 或 feature/{change_id}"
  
  - name: "Commits存在"
    command: "git log --oneline"
    expect: "至少1个commit"
  
  - name: "Task完成报告"
    files:
      - "docs/changes/{change_id}/completion-report.md"
  
  - name: "报告完整性"
    report_required:
      - "每个Task有完成状态"
      - "每个Task有测试覆盖"
      - "每个Task有commit引用"
  
  - name: "测试通过"
    command: "pytest 或对应测试命令"
    expect: "exit code 0"
```

**通过标准**: 所有检查项通过

**失败处理**: 返回Coder阶段修复

---

### Level 3: 报告质量检查

**触发时机**: `REVIEWER_ENTRY → REVIEWER_CHECK`, `QA_ENTRY → QA_CHECK`, `ARCHIVE_ENTRY → DONE`

**检查内容**:

#### Review报告检查
```yaml
checks:
  - name: "文件存在"
    file: "docs/changes/{change_id}/review-report.md"
  
  - name: "结论明确"
    required:
      - "评审结论: passed / conditional / failed"
  
  - name: "问题清单"
    verify:
      - "如果结论≠passed，必须有issue列表"
      - "每个issue有严重级别(CRITICAL/MAJOR/MINOR)"
      - "CRITICAL问题数 ≥ 1 → 结论必须是failed"
  
  - name: "AC覆盖检查"
    verify:
      - "列出所有AC"
      - "每个AC有覆盖状态"
```

#### QA报告检查
```yaml
checks:
  - name: "文件存在"
    file: "docs/changes/{change_id}/qa-report.md"
  
  - name: "结论明确"
    required:
      - "结论: passed / failed"
  
  - name: "AC覆盖矩阵"
    verify:
      - "表格包含: AC编号 | 测试文件 | 状态"
      - "所有AC有对应测试"
      - "覆盖率 = 100%"
  
  - name: "测试统计"
    required:
      - "总测试数"
      - "通过数"
      - "失败数"
      - "跳过数"
  
  - name: "环境差异"
    conditional: "如果有环境差异"
    required: "说明差异及影响"
```

#### 归档检查 (R10 + L3)
```yaml
checks:
  - name: "R10: PR流程合规"
    command: "git log -5 --oneline --merges"
    expect: "最近5个commit中有merge"
  
  - name: "分支检查"
    command: "git branch --show-current"
    expect: "main"
  
  - name: "归档目录结构"
    verify:
      - "docs/archive/{change_id}/ 已创建"
      - "包含: prd.md, spec.md, design.md, tasks.md"
      - "包含: review-report.md, qa-report.md"
      - "不包含: .sdd-state.json"
  
  - name: "基线更新"
    verify:
      - "docs/current/README.md 已更新"
      - "变更历史包含本change_id"
```

**通过标准**: 所有检查项通过

**失败处理**: 根据具体失败项返回对应阶段修复

---

## 门禁执行流程

```python
def execute_phase_gate(current_state, next_state, change_id):
    """
    执行阶段门禁检查
    
    Returns:
        GateResult(success: bool, errors: List[str], next_state: str)
    """
    
    # 1. 确定lint level
    lint_level = get_lint_level_for_transition(current_state, next_state)
    
    # 2. 执行检查
    errors = []
    
    if lint_level >= 1:
        errors.extend(check_level_1(change_id))
    
    if lint_level >= 2:
        errors.extend(check_level_2(change_id))
    
    if lint_level >= 2.5:
        errors.extend(check_level_2_5(change_id))
    
    if lint_level >= 3:
        errors.extend(check_level_3(change_id))
    
    # 3. 处理结果
    if errors:
        # 失败：记录到状态文件，返回阻断
        record_lint_failure(change_id, lint_level, errors)
        
        # 检查失败次数，决定是否BLOCKED
        failure_count = get_failure_count(change_id, current_state)
        if failure_count >= MAX_FAILURE_THRESHOLD:
            return GateResult(
                success=False,
                errors=errors,
                next_state="BLOCKED"
            )
        
        # 返回当前状态（重试）
        return GateResult(
            success=False,
            errors=errors,
            next_state=current_state  # 不推进，保持原状态
        )
    
    # 4. 成功：记录并推进
    record_lint_success(change_id, lint_level)
    return GateResult(success=True, errors=[], next_state=next_state)
```

---

## 失败阈值

| 状态 | 最大失败次数 | 超过阈值 |
|------|:----------:|---------|
| PO_CHECK | 3 | → BLOCKED |
| BA_CHECK | 3 | → BLOCKED |
| ARCHITECT_CHECK | 3 | → BLOCKED |
| CODER_CHECK | 3 | → BLOCKED |
| REVIEWER_CHECK | 2 | → BLOCKED（需用户决策） |
| QA_CHECK | 4 | → BLOCKED（熔断） |
| ARCHIVE_CHECK | 1 | → BLOCKED |

---

## 快速检查命令

```bash
# Level 1: 基础产物检查
./scripts/check-level1.sh {change_id}

# Level 2: 设计产物检查
./scripts/check-level2.sh {change_id}

# Level 2.5: 代码产物检查
./scripts/check-level2-5.sh {change_id}

# Level 3: 报告质量检查
./scripts/check-level3.sh {change_id}

# 全量检查
./scripts/check-all.sh {change_id}
```
