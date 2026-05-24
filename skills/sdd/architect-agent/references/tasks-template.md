# Tasks 模板

> Architect Agent 产出，Coder Agent 执行。每 Task 2-5 分钟可完成，含 exact 文件路径和验证命令。

---

## 执行约定

1. **工作目录**：`{project_root}`
2. **每 Task 完成后**：commit，格式 `feat({scope}): T{N} {描述}`
3. **验证方式**：{手动自检 / sdd-structure-lint / CI}

---

## Task 执行顺序

```
T1 → T2 → T3 → ...
```

---

## T1: {任务名称}

**估时**：{minutes}
**依赖**：{none / T{n}}
**AC 覆盖**：{AC{n}, AC{n+1}}
**产出**：{文件路径}

### Step 1: {步骤描述}

```bash
# 具体命令
```

### Step N: Commit

```bash
git add {files}
git commit -m "feat({scope}): T1 {描述}"
```

---

## T{n}: {任务名称}

...

---

## 汇总

| # | Task | 估时 | 产出文件数 |
|---|------|:---:|:---:|
| T1 | | | |
| **总计** | | **Xh** | **N** |
