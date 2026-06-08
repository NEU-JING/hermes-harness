# Delta Spec 格式参考

> **用途**: Change 内的 spec 变更使用 delta 操作头描述，归档时按操作头合并到基线
> **版本**: 1.0 | 2026-06-09

---

## 目录结构

```
docs/
├── specs/                          # 基线 — 按 capability 分文件
│   ├── user-auth/spec.md
│   └── course-management/spec.md
└── changes/{change_id}/
    ├── specs/                      # 变更内的 delta 结构
    │   ├── user-auth/spec.md       # 仅包含操作头
    │   └── course-management/spec.md
    └── ...
```

---

## Delta 操作头定义

### ## ADDED Requirements

新增一个或多个 requirement。

```markdown
## ADDED Requirements

### Requirement: 社交登录

SHALL 支持微信扫码登录
MUST 支持 GitHub OAuth 登录

#### Scenario AC6: 微信扫码成功

- **WHEN** 用户扫描二维码
- **AND** 在微信端确认授权
- **THEN** 系统创建新用户（如首次登录）
- **AND** 返回 JWT token
```

**规则**：新增的 requirement 必须包含**完整内容**（非仅新增行）

---

### ## MODIFIED Requirements

修改已有 requirement。

```markdown
## MODIFIED Requirements

### Requirement: 用户登录

SHALL 支持邮箱+密码登录
MUST 在 5 次失败后锁定账号 30 分钟   ← 原为 15 分钟

#### Scenario AC2: 账号锁定

- **WHEN** 用户连续 5 次输错密码   ← 原为 3 次
- **THEN** 账号锁定 30 分钟        ← 原为 15 分钟
```

**规则**：
- **必须包含完整更新内容**（非仅 diff）
- 阅读者应能从 delta 文件直接理解最终状态

---

### ## REMOVED Requirements

删除已有 requirement。

```markdown
## REMOVED Requirements

### Requirement: 短信验证码登录

- **Reason**: 运营商 API 未就绪，推迟到 v2.0
- **Migration**: 受影响用户改为邮箱验证码登录

#### Scenario AC8: 短信登录

- **Reason**: 功能移除，AC 编号保留但标记已删除
```

**规则**：每个删除项必须包含 **Reason** 和 **Migration** 字段

---

### ## RENAMED Requirements

重命名 requirement。

```markdown
## RENAMED Requirements

- **FROM**: `用户注册`
- **TO**: `账号创建`
```

---

## 向后兼容规则

1. **存量 Change 无 delta 结构时**：lint 不报错，归档时跳过 spec sync
2. **空 delta 目录**：Change 无 specs/ 子目录时，归档只做 baseline-merge 的 archive 迁移
3. **混用格式**：同一 Change 内允许部分 capability 有 delta、部分无 delta

---

## 示例：完整 Change 的 specs/ 结构

```
docs/changes/003-user-auth/specs/
└── user-auth/
    └── spec.md
```

内容：

```markdown
# User Auth — Delta Spec

## ADDED Requirements

### Requirement: 社交登录

SHALL 支持微信扫码登录
MUST 支持 GitHub OAuth 登录

#### Scenario AC6: 微信扫码成功

- **WHEN** 用户扫描二维码
- **AND** 在微信端确认授权
- **THEN** 系统创建新用户（如首次登录）
- **AND** 返回 JWT token

## MODIFIED Requirements

### Requirement: 用户登录

SHALL 支持邮箱+密码登录
MUST 在 5 次失败后锁定账号 30 分钟

#### Scenario AC2: 账号锁定

- **WHEN** 用户连续 5 次输错密码
- **THEN** 账号锁定 30 分钟
```

---

## 归档合并流程

归档时 orchestrator 执行 6 步流程（见 orchestrator 文档），其中 Step 2（Spec Sync）执行以下合并逻辑：

```
变更后的 specs/                 基线 specs/
┌──────────────────┐         ┌──────────────────┐
│ ADDED            │──apply──▶│ 含新增内容       │
│ MODIFIED         │──apply──▶│ 覆盖更新         │
│ REMOVED          │──apply──▶│ 删除对应内容     │
│ RENAMED          │──apply──▶│ 重命名           │
└──────────────────┘         └──────────────────┘
```

归档后：
- 基线 specs/ 已反映全部变更
- 变更内的 specs/ 随 change 整体移入 `archive/{change_id}/`
- 历史追溯可查阅 archive/
