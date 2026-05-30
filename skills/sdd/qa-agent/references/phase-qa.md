# Phase QA 指南

> **版本**: 1.0  
> **日期**: 2026-05-30

---

## 什么是 Phase QA？

Phase QA 是增量交付模式下的测试验证，包含：
1. 当前 Phase 的全量测试
2. 前面 Phase 的回归测试（抽样）

---

## Phase QA 流程

```
1. 读取 .sdd-state.json 确定 current_sub_phase
2. 获取当前 Phase 的测试范围
3. 运行当前 Phase 的全量测试
4. 运行前面 Phase 的回归测试（10% 抽样）
5. 验证 AC 覆盖
6. 产出 Phase QA Report
7. 更新 .sdd-state.json phase_status
```

---

## 测试范围

### 当前 Phase 测试

从 `tasks.md` 获取当前 Phase 的测试文件：

```markdown
## Phase 1: 基础数据层

**验证**:
```bash
pytest tests/test_path.py -v
pytest tests/test_radar.py -v
```
```

### 回归测试

前面 Phase 的核心测试（10% 抽样）：

```bash
# Phase 2 QA 时的回归测试
# 运行 Phase 1 核心测试（关键路径）
pytest tests/test_path.py::test_tables_exist -v
pytest tests/test_path.py::test_diagnosis_recommend_path -v
pytest tests/test_radar.py::test_time_decay_calculation -v
```

---

## Phase QA Report 结构

```markdown
# Phase QA Report

> **变更 ID**: [你的变更ID]  
> **Phase**: phase_1_path_radar  
> **日期**: 2026-05-30

---

## Phase 1 测试结果

### 概览

| 测试类型 | 总数 | 通过 | 失败 | 跳过 |
|----------|:----:|:----:|:----:|:----:|
| 当前 Phase | 99 | 99 | 0 | 0 |
| 回归测试 | 29 | 29 | 0 | 0 |
| **总计** | **128** | **128** | **0** | **0** |

**结论**: ✅ 通过

**是否可交付**: ✅ 是

---

### AC 覆盖矩阵

| Phase | AC | 测试 | 结果 |
|-------|:---:|------|:----:|
| Phase 1 | AC1 | test_path.py::test_tables_exist | ✅ |
| Phase 1 | AC2 | test_path.py::test_diagnosis_* | ✅ |
| ... | ... | ... | ... |

**AC 覆盖度**: 14/14 = 100%

---

### 环境差异说明

| 环境 | 配置 | 影响 |
|------|------|------|
| 测试 | SQLite | 并发测试跳过 |
| 生产 | PostgreSQL | 无影响 |

---

## 其他 Phase 状态

| Phase | 测试状态 | AC 覆盖 | 结论 |
|-------|:--------:|:-------:|------|
| Phase 1 | 128/128 | 100% | ✅ 通过 |
| Phase 2 | — | — | 未开始 |

---

## 建议

Phase 1 测试全部通过，可进入用户验收阶段。
