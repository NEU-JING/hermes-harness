# PR与Review流程

> **版本**: 2.0  
> **日期**: 2026-05-30  
> **对应状态机**: REVIEWER_CHECK → QA_ENTRY / CODER_ENTRY

---

## 流程概述

PR与Review是SDD流程的关键环节，连接Coder产出与QA验证。

**在状态机中的位置**:
```
CODER_CHECK ──▶ REVIEWER_ENTRY ──▶ REVIEWER_CHECK
                                           │
                    ┌──────────────────────┘
                    │ (review failed)
                    ▼
            CODER_ENTRY (修复)
                    │
                    │ (review passed)
                    ▼
            QA_ENTRY
```

---

## Reviewer阶段委托

```yaml
delegate_task:
  goal: "三阶段代码评审：Spec合规、代码质量、架构一致性"
  
  context: |
    change_id: "{change_id}"
    current_state: "REVIEWER_ENTRY"
    
    ## 输入产物
    prerequisites:
      spec:
        path: "docs/changes/{change_id}/spec.md"
        required_ac: "[AC列表]"
      design:
        path: "docs/changes/{change_id}/design.md"
      completion_report:
        path: "docs/changes/{change_id}/completion-report.md"
      code:
        branch: "feat/{change_id}"
        commits: "[自动获取]"
    
    ## 评审阶段
    review_phases:
      phase_1:
        name: "Spec合规"
        checks:
          - "所有AC有测试覆盖"
          - "功能实现与Spec一致"
          - "Out of Scope功能未实现"
      
      phase_2:
        name: "代码质量"
        checks:
          - "DRY：无重复代码"
          - "YAGNI：无过度设计"
          - "函数长度 ≤ 50行"
          - "命名清晰"
          - "错误处理完整"
      
      phase_3:
        name: "架构一致性"
        checks:
          - "模块划分与Design一致"
          - "接口定义与Design一致"
          - "数据流与Design一致"
    
    ## 严重级别
    severity:
      CRITICAL: "必须修复才能通过"
      MAJOR: "应修复，可条件通过"
      MINOR: "建议修复"
      INFO: "仅供参考"
    
    ## 输出
    deliverable:
      file: "docs/changes/{change_id}/review-report.md"
      required_conclusion: "passed/conditional/failed"
  
  toolsets: ["file", "terminal", "skills", "github"]
```

---

## Review结论处理

### 状态机转换规则

```python
def process_review_result(change_id, review_report):
    """处理Review结论"""
    
    conclusion = review_report["conclusion"]
    critical_count = review_report["critical_count"]
    
    if conclusion == "failed" or critical_count > 0:
        # Review不通过 → 返回Coder修复
        print("❌ Review不通过，返回Coder阶段修复")
        
        # 记录失败
        record_failure(change_id, "REVIEWER_CHECK", "review_failed")
        
        # 检查失败次数
        failure_count = get_failure_count(change_id, "REVIEWER_CHECK")
        if failure_count >= 2:
            # 连续2次失败 → BLOCKED
            transition(change_id, "BLOCKED")
        else:
            # 返回Coder
            transition(change_id, "CODER_ENTRY")
        
        return False
    
    elif conclusion == "conditional":
        # 有条件通过 → 进入QA，但记录MAJOR问题
        print("⚠️ Review有条件通过，进入QA但需修复MAJOR问题")
        transition(change_id, "QA_ENTRY")
        return True
    
    else:  # passed
        # 完全通过
        print("✅ Review通过，进入QA")
        transition(change_id, "QA_ENTRY")
        return True
```

### 结论映射表

| Review结论 | CRITICAL数 | 状态机动作 |
|-----------|:----------:|-----------|
| `passed` | 0 | → `QA_ENTRY` |
| `conditional` | 0 | → `QA_ENTRY`（带警告） |
| `failed` | ≥0 | → `CODER_ENTRY`（修复） |
| `passed` | ≥1 | 视为`failed` → `CODER_ENTRY` |

---

## PR工作流

### PR生命周期（Coder阶段）

```
Coder push → 创建PR(OPEN) → Review → QA → 用户验收 → Squash Merge
                 ↑                                    ↓
                 └────────── 保持OPEN直到验收通过 ────┘
```

### 状态机与PR状态的对应

| 状态机状态 | PR状态 | 动作 |
|-----------|-------|------|
| `CODER_ENTRY` | PR创建/更新 | Coder推送代码，创建PR |
| `REVIEWER_ENTRY` | PR保持OPEN | Reviewer在PR上评审 |
| `REVIEWER_CHECK` | PR保持OPEN | 结论写入review-report.md |
| `QA_ENTRY` | PR保持OPEN | QA验证代码 |
| `QA_CHECK` | PR保持OPEN | 结论写入qa-report.md |
| `USER_ACCEPT` | PR保持OPEN | 等待用户最终确认 |
| `ARCHIVE_ENTRY` | Squash Merge | 验收通过后合并 |

### R10检查（归档时）

```python
def r10_check(change_id):
    """归档前R10检查"""
    
    # 1. 检查当前分支
    current_branch = run("git branch --show-current")
    if current_branch != "main":
        return False, f"R10阻断: 当前在{current_branch}分支，请切换到main"
    
    # 2. 检查merge记录
    merges = run("git log -5 --oneline --merges")
    if not merges:
        return False, "R10阻断: 未检测到PR merge记录"
    
    # 3. 检查PR编号匹配
    # （可选）验证merge commit包含change_id
    
    return True, "R10通过"
```

---

## Review-修复循环

### 失败处理流程

```
第1轮Review:
  CODER_ENTRY → REVIEWER_ENTRY → REVIEWER_CHECK
                                        │ failed
                                        ▼
                              CODER_ENTRY (修复)
                                        │
                                        ▼
第2轮Review:
  REVIEWER_ENTRY → REVIEWER_CHECK
                                        │ failed (连续2次)
                                        ▼
                                  BLOCKED
                                        │
                                        ▼
                              用户决策（手动干预）
```

### 熔断规则

| 阶段 | 熔断阈值 | 触发后 |
|------|:-------:|--------|
| Reviewer | 2次失败 | → `BLOCKED` |
| QA | 4次失败 | → `BLOCKED` |

---

## Review报告格式

```markdown
# Review Report — {change_id}

## 评审结论

**结论**: [passed / conditional / failed]

**统计**:
- CRITICAL: {N} 个
- MAJOR: {N} 个
- MINOR: {N} 个
- INFO: {N} 个

---

## Phase 1: Spec合规检查

| AC | 测试覆盖 | 实现状态 | 备注 |
|:---|:--------:|:--------:|------|
| AC1 | ✅ | ✅ | — |
| AC2 | ✅ | ⚠️ | 边界情况未处理 |

**Phase 1结论**: [通过/不通过]

---

## Phase 2: 代码质量检查

| # | 严重级别 | 文件 | 行号 | 问题 | 修复建议 |
|---|:-------:|------|:----:|------|---------|
| 1 | CRITICAL | src/auth.py | 45 | 密码明文存储 | 使用bcrypt |
| 2 | MAJOR | src/api.py | 120 | N+1查询 | 使用joinedload |

**Phase 2结论**: [通过/不通过]

---

## Phase 3: 架构一致性检查

| 检查项 | 设计约定 | 实现 | 偏差说明 |
|--------|---------|------|---------|
| 模块划分 | 分层架构 | ✅ | — |
| 接口定义 | RESTful | ⚠️ | 部分接口不符合 |

**Phase 3结论**: [通过/不通过]

---

## 修复清单

### 必须修复（CRITICAL）

- [ ] #1: src/auth.py:45 — 使用bcrypt加密密码

### 建议修复（MAJOR）

- [ ] #2: src/api.py:120 — 优化查询

---

## AC覆盖矩阵

| AC | 测试文件 | 状态 |
|:---|---------|:----:|
| AC1 | tests/test_auth.py | ✅ |
| AC2 | tests/test_auth.py | ⚠️ |

**覆盖率**: X/Y = XX%
```

---

## 快速参考

```bash
# 手动触发Review
python orchestrator.py delegate {change_id} reviewer

# 查看Review报告
cat docs/changes/{change_id}/review-report.md

# 处理Review结论（手动）
python orchestrator.py transition {change_id} QA_ENTRY  # 通过
python orchestrator.py transition {change_id} CODER_ENTRY  # 不通过
```
