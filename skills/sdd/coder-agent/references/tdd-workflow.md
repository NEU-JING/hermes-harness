# TDD 工作流

> Coder Agent 执行每个 Task 时必须遵循 RED-GREEN-REFACTOR 循环。这是 R3 强制要求。

---

## TDD 三步循环

```
RED ──→ GREEN ──→ REFACTOR
 ↑                    │
 └────────────────────┘
```

### Step 1: RED（写失败测试）

1. 根据 AC 编写测试用例
2. 测试只覆盖当前 Task 的范围
3. 运行测试，**确认失败**（期望的失败原因）

```bash
pytest tests/path/test_feature.py::test_specific_behavior -v
# 期望: FAILED — 功能尚未实现
```

### Step 2: GREEN（最小实现）

1. 写刚好让测试通过的代码（不写多余代码）
2. 运行测试，**确认通过**
3. 如果涉及多个测试，逐个通过

```bash
pytest tests/path/test_feature.py::test_specific_behavior -v
# 期望: PASSED
```

### Step 3: REFACTOR（重构）

1. 消除重复代码
2. 改善命名
3. 提取公共函数
4. 运行全部测试，**确认全部通过**

```bash
pytest tests/path/ -v
# 期望: ALL PASSED
```

---

## 测试分类

| 测试类型 | 框架 | 执行频率 | 运行环境 |
|---------|------|---------|---------|
| 单元测试 | pytest | 每 Task | 本地 + CI |
| 集成测试 | pytest | 每阶段 | CI（可标记 CI-only） |
| E2E 测试 | Playwright | QA 阶段 | CI（必须标记 CI-only） |

---

## 测试命名规范

```
test_{被测函数}_{场景描述}
```

示例：
```python
def test_login_with_valid_credentials():
    ...

def test_login_with_invalid_email_returns_400():
    ...

def test_login_when_user_not_found_returns_404():
    ...
```

---

## 常见错误

1. **先写实现再补测试** → 违反 TDD，R3 不允许
2. **测试覆盖过大** → 一个测试覆盖多个 AC，失败时难以定位
3. **跳过 REFACTOR** → 代码质量差，Review 阶段会被打回
4. **测试依赖外部状态** → 违反 R6（测试自包含原则）
