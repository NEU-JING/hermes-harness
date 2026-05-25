# 模板: conftest.py
# 用途: 自动跳过 CI-only 测试（本地开发时），CI 环境正常运行。
# 依赖: pytest.ini 中已注册 ci_only marker。

# SDD: CI-only marker support — auto-skip locally, run only in CI
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
