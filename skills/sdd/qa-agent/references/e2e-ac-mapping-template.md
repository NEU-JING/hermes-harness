# E2E-AC 映射模板

> QA Agent 使用此模板生成 AC → E2E 的覆盖矩阵。

---

## 映射方法

1. 从 `spec.md` 提取所有 AC 编号
2. 在 E2E 测试文件中搜索每个 AC 编号的引用
3. 生成覆盖矩阵

---

## 搜索规则

```bash
# 在 E2E 测试文件中搜索 AC 引用
grep -rn "AC[0-9]" tests/e2e/ --include="*.spec.*"
```

---

## 覆盖矩阵

| AC 编号 | E2E 文件:行号 | 覆盖状态 | 备注 |
|:---:|------|:---:|------|
| AC1 | `login.spec.js:12` | ✓ | |
| AC2 | `login.spec.js:35` | ✓ | |
| AC3 | — | ✗ | **缺失！** |

---

## 缺失覆盖处理

缺失覆盖的 AC 标记为 QA 不通过，返回 Coder Agent 补充 E2E 测试。

**豁免情况**：
- AC 标注为 `[MANUAL]` — 需人工验证，不需要 E2E
- AC 为纯后端逻辑（无 UI）— 由单元测试覆盖，不需要 E2E
- Quick 流程 — 跳过 E2E（R7 豁免）

---

## 覆盖统计

```
总 AC 数: {total}
E2E 覆盖: {covered}
覆盖率: {percentage}%
缺失: {uncovered}
```
