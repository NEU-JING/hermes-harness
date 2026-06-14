# Design 基线合并指南

> **用途**: 归档时将 change 的 design.md 关键决策合并到 `docs/current/design.md`
> **版本**: 1.0 | 2026-06-09

---

## `docs/current/design.md` 格式规范

```markdown
# 架构设计汇总

> 此文件由归档流程自动维护，反映当前生产版本的架构全貌
> 每次归档在末尾追加一个新 `##` 章节

---

## v1.0: {Change ID} — {简短描述}

**归档日期**: 2026-01-15

### 关键决策

| 决策 | 选项 | 选择 | 理由 |
|------|------|------|------|
| 框架选型 | FastAPI / Django / Flask | FastAPI | 异步支持好，Pydantic 集成 |
| 数据库 | Postgres / MySQL / SQLite | Postgres | 事务完整性，JSONB 支持 |

### 架构变更

| 模块 | 变更 | 影响范围 |
|------|------|---------|
| auth/ | 新增 OAuth2 支持 | Login API |
| course/ | 重构章节模型 | Course DB schema |

### 模块变更

#### 新增模块

| 模块路径 | 职责 | 依赖 |
|---------|------|------|
| app/services/oauth.py | OAuth2 认证服务 | fastapi, httpx |

#### 修改模块

| 模块路径 | 变更内容 |
|---------|---------|
| app/models/course.py | 新增 Chapter.position 字段 |

---

## v2.0: {Change ID} — {简短描述}

...
```

---

## 归档合并流程

### Step 3 执行规范

归档时 orchestrator 执行 Step 3：

1. 读取 `changes/{id}/design.md`
2. 提取以下信息：
   - **变更 ID + 描述**（从 change 目录名或 sdd-state 获取）
   - **关键决策**（方案对比表中的选择项）
   - **架构变更**（新增/修改/删除的模块）
   - **数据模型变更**（如涉及）
3. 以 `## v{N}.{M}: {Change ID} — {描述}` 格式追加到 `docs/current/design.md`
4. 如果 `docs/current/design.md` 不存在，创建它

### 信息提取模板

```python
def extract_design_summary(change_id):
    design_path = f"docs/changes/{change_id}/design.md"
    
    sections = {
        "key_decisions": extract_section(design_path, "方案对比|关键决策"),
        "arch_changes": extract_section(design_path, "架构变更|模块划分|数据模型"),
        "new_modules": extract_all(design_path, r"### 方案.*|### 模块.*"),
    }
    
    return sections
```

### 追加格式

```markdown
## v1.0: 003-user-auth — 用户认证 OAuth2 支持

**归档日期**: 2026-06-09

### 关键决策

| 决策 | 选择 | 理由 |
|------|------|------|
| OAuth2 库 | authlib | 社区成熟，支持微信/GitHub |

### 架构变更

| 模块 | 变更 | 影响 |
|------|------|------|
| auth/ | 新增 OAuth2 router | Login API |
```

---

## 向后兼容

1. **`docs/current/design.md` 不存在时**：Step 3 自动创建
2. **归档时 design.md 无有效信息**：追加最小条目（仅变更 ID + 日期 + "无设计变更"）
3. **旧归档格式兼容**：已归档的 change 不受影响，新归档才使用此格式
