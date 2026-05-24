# 编码约定清单

> Coder Agent 提交代码前自检的编码规范清单。

---

## Python 项目

### 代码风格

- [ ] 所有代码通过 `black` 格式化
- [ ] 所有 import 通过 `isort` 排序
- [ ] 无 `ruff` 报错（E/W/F 规则）
- [ ] 类型注解完整（函数参数和返回值）
- [ ] 无 `print()` 调试语句（使用 `logging`）

### 命名规范

- [ ] 类名：PascalCase
- [ ] 函数/变量：snake_case
- [ ] 常量：UPPER_SNAKE_CASE
- [ ] 私有方法：`_leading_underscore`

### 文档

- [ ] 公开函数有 docstring
- [ ] 复杂逻辑有注释说明意图
- [ ] README 或模块级文档更新

### 依赖

- [ ] 新依赖已添加到 `requirements.txt` 或 `pyproject.toml`
- [ ] 无未使用的 import

---

## Go 项目

- [ ] 代码通过 `gofmt` 格式化
- [ ] 无 `golangci-lint` 报错
- [ ] 错误处理完整（无 `_` 忽略 error）
- [ ] 公开函数有注释

---

## 前端项目（React/TypeScript）

- [ ] 代码通过 `prettier` 格式化
- [ ] 无 `eslint` 报错
- [ ] 组件 Props 有类型定义
- [ ] 无 `any` 类型（除非有注释说明）
- [ ] 无 console.log 调试语句

---

## 通用约定

- [ ] DRY：无重复代码（≥3 次出现须提取）
- [ ] YAGNI：无“以后可能用到”的代码
- [ ] 无 TODO/FIXME（除非标注了关联 issue）
- [ ] commit message 格式正确：`type(scope): description`
