# Phase Review 指南

> **版本**: 1.0  
> **日期**: 2026-05-30

---

## 什么是 Phase Review？

Phase Review 是增量交付模式下的代码评审，仅针对当前 Phase 的代码变更进行评审。

与传统 Review 的区别：

| 维度 | 传统 Review | Phase Review |
|------|------------|--------------|
| 评审范围 | 全部代码变更 | 仅当前 Phase 的代码 |
| 报告结构 | 单一整体报告 | 按 Phase 分章节 |
| AC 覆盖检查 | 全量 AC | 当前 Phase 的 AC |
| 执行时机 | Coder 全部完成后 | 每 Phase Coding 完成后 |

---

## Phase Review 流程

```
1. 读取 .sdd-state.json 确定 current_sub_phase
2. 从 tasks.md 获取当前 Phase 的 Task 列表
3. 确定该 Phase 涉及的代码文件范围
4. 执行三阶段评审（Spec 合规/代码质量/架构一致性）
5. 产出 Phase Review Report
6. 更新 .sdd-state.json phase_status
```

---

## 确定代码范围

### 方式 1：Tasks 映射

从 `tasks.md` 中该 Phase 的 Tasks 推断代码范围：

```markdown
## Phase 1: 基础数据层

### T1: Path 模块数据库表
**文件**: `app/models/path.py`

### T2: Path 入学诊断 API
**文件**: `app/api/v1/paths.py`, `app/services/path_service.py`
```

**代码范围**: `app/models/path.py`, `app/api/v1/paths.py`, `app/services/path_service.py`

### 方式 2：Git Diff

通过 Git 获取 Phase 期间的变更：

```bash
# 获取 Phase 期间的 commits
# 假设 Phase 从 commit A 开始，到 commit B 结束
git diff A..B --name-only
```

### 方式 3：显式声明

在 `.sdd-state.json` 中记录：

```json
{
  "phase_status": {
    "phase_1": {
      "files_modified": [
        "app/models/path.py",
        "app/models/radar.py",
        "app/api/v1/paths.py",
        "app/api/v1/radar.py"
      ]
    }
  }
}
```

---

## Phase Review Report 结构

```markdown
# Phase Review Report

> **变更 ID**: 002-ailp-v4-refactor  
> **Phase**: phase_1_path_radar  
> **日期**: 2026-05-30

---

## Phase 1 评审结果

### 概览

| 检查项 | 结果 | 严重级别 |
|--------|------|:--------:|
| Spec 合规 | ✅ 通过 | — |
| 代码质量 | ✅ 通过 | — |
| 架构一致性 | ⚠️ 有条件通过 | MINOR |

**结论**: 有条件通过（1 个 MINOR 问题）

**是否可交付**: ✅ 是（MINOR 问题不影响交付）

**阻塞下一 Phase**: 无

---

### 详细检查

#### Spec 合规检查

| AC | 检查项 | 结果 |
|:---:|--------|:----:|
| AC1 | Path 表存在 | ✅ |
| AC2 | 入学诊断 API | ✅ |
| ... | ... | ... |

#### 代码质量检查

| 检查项 | 结果 | 说明 |
|--------|:----:|------|
| 测试覆盖 | ✅ | 24/24 测试通过 |
| 代码规范 | ✅ | 符合项目规范 |
| 文档完整 | ✅ | 关键函数有 docstring |

#### 架构一致性检查

| 检查项 | 结果 | 严重级别 | 说明 |
|--------|:----:|:--------:|------|
| 模块职责 | ✅ | — | 符合 Design 定义 |
| 接口契约 | ⚠️ | MINOR | `get_skill_radar` 返回字段缺少 `confidence` |

---

### 问题列表

#### MINOR

| # | 问题 | 位置 | 建议修复 |
|---|------|------|---------|
| 1 | 缺少 confidence 字段 | `app/services/radar_service.py:45` | 根据 Design 补充 |

---

## 其他 Phase 状态

| Phase | 状态 | 是否可交付 |
|-------|------|:----------:|
| Phase 1 | 有条件通过 | ✅ |
| Phase 2 | 未开始 | — |
| Phase 3 | 未开始 | — |

---

## 汇总

| Phase | AC 覆盖 | 测试通过 | 结论 |
|-------|:-------:|:--------:|------|
| Phase 1 | 14/14 | 293/293 | 有条件通过 |

**整体建议**: Phase 1 可进入 QA，MINOR 问题可在 QA 阶段同步修复。
```

---

## 状态更新

Review 完成后，更新 `.sdd-state.json`：

```json
{
  "phase_status": {
    "phase_1": {
      "status": "review_passed",
      "review_status": "passed",
      "review_issues": {
        "critical": 0,
        "major": 0,
        "minor": 1
      },
      "is_phase_deliverable": true,
      "blockers_for_next_phase": []
    }
  }
}
```

**状态值**: `not_started` → `coding_done` → `review_passed`/`review_failed`

---

## 检查清单

- [ ] 确定了当前 Phase 的代码范围
- [ ] 检查了该 Phase 覆盖的所有 AC
- [ ] 三阶段评审完成（Spec/代码/架构）
- [ ] 产出了 Phase Review Report
- [ ] 更新了 `.sdd-state.json`
- [ ] 明确了是否可交付和阻塞项
