# SDD 流程级别判定规则

> 定义 Quick / Standard / Enhanced 三级流程的判定逻辑和阶段清单。

---

## 三级定义

### Quick（轻量级）

**适用场景**：
- Bug 修复（单文件、无架构变更）
- 文档更新
- 配置变更（非 CI/CD）
- 小 UI 调整（纯前端，不涉及后端 API）

**判定条件**（满足任一即 Quick）：
1. 变更范围 ≤ 2 个文件
2. 变更类型为 `docs`、`chore`、`style`
3. 用户明确指定 `--quick` 或 "快速"、"简单"

**流程阶段**：
```
Architect（轻量：跳过 Brainstorming）
  → Coder（TDD 仍强制）
  → QA（跳过 E2E，仅单元测试）
```

**跳过阶段**：PO、BA、Review

---

### Standard（标准级，默认）

**适用场景**：
- 新功能开发
- API 变更
- 数据模型变更
- 跨模块重构
- 任何不满足 Quick 条件的变更

**判定条件**（默认，无需匹配）：
- 不满足 Quick 条件 → 自动判定为 Standard

**流程阶段**：
```
PO → BA → Architect → Coder → Reviewer → QA → 用户验收 → 归档
```

**强制执行**：Brainstorming（≥2 方案对比）、E2E 测试、前后端契约检查

---

### Enhanced（增强级）

**适用场景**：
- 安全相关功能
- 支付/财务模块
- 认证/授权变更
- 性能关键路径
- 数据迁移

**判定条件**（满足任一即 Enhanced）：
1. 变更涉及安全、认证、授权
2. 用户明确指定 `--enhanced` 或 "完整流程"
3. 变更描述含关键词：安全、支付、认证、授权、性能、迁移

**流程阶段**：
```
Standard 全部阶段
  + 安全审查（在 Architect 之后）
  + 性能测试（在 QA 之后）
  + 灰度验证（在 用户验收 之前）
```

---

## 判定伪代码

```python
def determine_flow_level(change_description: str, changed_files: list[str], user_flag: str | None = None) -> str:
    """判定 SDD 流程级别"""
    
    # 用户显式指定优先
    if user_flag in ("enhanced", "完整", "enhanced流程"):
        return "Enhanced"
    if user_flag in ("quick", "快速", "简单"):
        return "Quick"
    
    # Enhanced 关键词匹配
    enhanced_keywords = ["安全", "支付", "认证", "授权", "性能", "迁移", "隐私"]
    if any(kw in change_description for kw in enhanced_keywords):
        return "Enhanced"
    
    # Quick 判定
    if len(changed_files) <= 2:
        return "Quick"
    
    change_type = extract_change_type(change_description)  # 从 PRD/Spec 提取
    if change_type in ("docs", "chore", "style"):
        return "Quick"
    
    # 默认
    return "Standard"
```

---

## 各流程阶段对照

| 阶段 | Quick | Standard | Enhanced |
|------|:---:|:---:|:---:|
| PO（需求定义） | ✗ | ✓ | ✓ |
| BA（Spec + AC） | ✗ | ✓ | ✓ |
| Architect（Design + Tasks） | 轻量* | ✓ | ✓ |
| 安全审查 | ✗ | ✗ | ✓ |
| Coder（实现） | ✓ | ✓ | ✓ |
| Reviewer（评审） | ✗ | ✓ | ✓ |
| QA（测试验证） | 轻量† | ✓ | ✓ |
| 性能测试 | ✗ | ✗ | ✓ |
| 灰度验证 | ✗ | ✗ | ✓ |
| 用户验收 | ✗ | ✓ | ✓ |
| 归档 | ✓ | ✓ | ✓ |

> \* Quick 的 Architect 阶段跳过 Brainstorming 方案对比
> † Quick 的 QA 阶段仅验证单元测试，跳过 E2E

---

## 规则豁免

| 规则 | Quick 豁免 | 说明 |
|------|:---:|------|
| R1: 没有 Spec 不写代码 | ✓ | Quick 跳过 Spec |
| R2: 编码前 Brainstorming | ✓ | Quick 跳过方案对比 |
| R3: TDD 强制 | ✗ | 所有级别强制 TDD |
| R4: 编码后必须评审 | ✓ | Quick 跳过 Review |
| R5: 前后端契约同步 | ✓ | Quick 通常为单端变更 |
| R6: 测试自包含原则 | ✗ | 所有级别强制 |
| R7: E2E-AC 一一对应 | ✓ | Quick 跳过 E2E |
| R8: Push 前必过 Pre-commit | ✗ | 所有级别强制 |
| R9: 目标环境通过原则 | ✗ | 所有级别强制 |
| R10: PR 不直接 push main | ✓ | Quick 小变更可例外 |
