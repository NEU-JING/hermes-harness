# CI-only 测试标记规范

> 配合 R9（目标环境通过原则），定义 CI-only 测试的标记方式和规范。

---

## 何时标记 CI-only

测试满足以下**任一**条件时，应标记为 CI-only：

| 场景 | 典型资源需求 | 示例 |
|------|------------|------|
| 数据库集成测试 | PostgreSQL/MySQL 容器 | `test_user_repository_postgres.py` |
| E2E 测试 | 浏览器环境（Playwright/Selenium） | `login.spec.js` |
| GPU 测试 | CUDA | `test_gpu_inference.py` |
| 大数据量测试 | > 2GB 内存 | `test_large_dataset_processing.py` |
| 长超时测试 | > 30 秒运行时间 | `test_model_training.py` |
| 外部服务依赖 | Redis/Kafka/MinIO | `test_message_queue_integration.py` |

---

## 标记方式

### Python (pytest)

```python
import pytest

@pytest.mark.ci_only  # CI_ONLY: 需要 Docker 环境运行 PostgreSQL
def test_user_repository_with_real_db():
    ...
```

或使用 skipif：

```python
import os
import pytest

@pytest.mark.skipif(
    os.environ.get("CI", "").lower() not in ("true", "1"),
    reason="CI_ONLY: 需要 Docker 环境"
)
def test_e2e_checkout_flow():
    ...
```

### JavaScript/TypeScript (Playwright)

```typescript
// CI_ONLY: 需要浏览器环境
test.describe('Checkout Flow', () => {
  test.skip(({ browserName }) => !process.env.CI, 'CI-only test');
  // ...
});
```

---

## 注释规范

每次标记必须附带原因注释：

```
# CI_ONLY: {简短原因}
```

**好的注释**：
- `# CI_ONLY: 需要 Docker 环境运行 PostgreSQL`
- `# CI_ONLY: Playwright E2E 测试，需要浏览器环境`
- `# CI_ONLY: GPU 推理测试，需要 CUDA`

**坏的注释**：
- `# CI only` ← 没有说明原因
- 无注释 ← 违反 R9

---

## 基础设施配置

### conftest.py（自动 skip）

```python
import os
import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "ci_only: tests that require CI environment resources"
    )

def pytest_collection_modifyitems(config, items):
    if os.environ.get("CI", "").lower() not in ("true", "1"):
        skip_ci_only = pytest.mark.skip(reason="CI-only test, skipped locally")
        for item in items:
            if "ci_only" in item.keywords:
                item.add_marker(skip_ci_only)
```

### pytest.ini

```ini
[pytest]
markers =
    ci_only: 仅在 CI 环境中运行的测试（需要 Docker/GPU/大内存等资源）
```

### CI 环境变量

CI pipeline 必须设置：

```yaml
env:
  CI: true
```

---

## QA Agent 检查

QA Agent 在环境差异标记阶段检查：

1. 搜索所有 `ci_only` / `skipif.*CI` 标记
2. 验证每个标记都有原因注释
3. 验证本地运行时这些测试被 skip
4. 验证 CI 运行时这些测试通过

**违反处理**：
- CI-only 测试未标记 → REQ，要求补充标记
- 标记了但 CI 未通过 → FAIL
- 标记了但注释缺失 → MINOR
