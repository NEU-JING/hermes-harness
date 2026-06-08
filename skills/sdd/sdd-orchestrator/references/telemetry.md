# Telemetry 匿名统计

> **用途**: 可选匿名使用统计，帮助了解 SDD 流程的实际使用模式
> **版本**: 1.0 | 2026-06-09
> **默认**: **关闭**（opt-in）

---

## 数据格式

每条事件写入 `~/.hermes/telemetry/{change_id}/events.ndjson`（NDJSON = JSON Lines）：

```json
{"timestamp":"2026-06-09T10:30:00Z","command":"transition","phase_from":"PO_ENTRY","phase_to":"PO_CHECK","duration_ms":45000}
{"timestamp":"2026-06-09T10:30:05Z","command":"transition","phase_from":"PO_CHECK","phase_to":"PO_DONE","duration_ms":5000}
{"timestamp":"2026-06-09T10:31:00Z","command":"delegate","phase_from":"PO_ENTRY","phase_to":"BA_ENTRY","duration_ms":55000}
{"timestamp":"2026-06-09T11:00:00Z","command":"user_confirm","phase":"PO_DONE","duration_ms":null}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|:---:|------|------|
| `timestamp` | string | ✅ | ISO 8601 时间戳 | `2026-06-09T10:30:00Z` |
| `command` | string | ✅ | 事件类型 | `transition` / `delegate` / `user_confirm` / `lint_check` |
| `phase_from` | string | 条件 | 来源阶段 | `PO_ENTRY` |
| `phase_to` | string | 条件 | 目标阶段 | `PO_CHECK` |
| `phase` | string | 条件 | 当前阶段（user_confirm 时） | `PO_DONE` |
| `duration_ms` | integer | 否 | 耗时（毫秒），null 表示用户等待 | `45000` |
| `result` | string | 否 | 结果 | `passed` / `failed` / `blocked` |

### 隐私承诺

**绝不记录**：
- 文件内容、路径、项目名
- 用户输入消息
- Agent 输出内容
- 环境变量或 API key
- IP 地址或设备标识

**仅记录**：
- 状态机转换事件（from/to + 耗时）
- Agent 委托事件（阶段名 + 耗时）
- 用户确认事件（阶段名）
- Lint 检查结果（通过/失败）

---

## 启用方式

### AGENTS.md 配置

```yaml
# 取消注释以启用 telemetry（默认关闭）
telemetry:
  enabled: true   # 设置为 true 启用
```

### 环境变量强制关闭

即使 AGENTS.md 启用了，以下任一变量会强制关闭：

```bash
export DO_NOT_TRACK=1
export HERMES_TELEMETRY_DISABLE=1
```

---

## 禁用方式

| 方式 | 作用范围 | 优先级 |
|------|---------|:----:|
| AGENTS.md 不配置或 `enabled: false` | 项目级 | 低 |
| `HERMES_TELEMETRY_DISABLE=1` | 会话级 | 中 |
| `DO_NOT_TRACK=1` | 全局 | 高 |

`DO_NOT_TRACK=1` 在任何情况下都优先于其他配置。

---

## 数据存储

| 存储位置 | 说明 | 保留策略 |
|---------|------|---------|
| `~/.hermes/telemetry/{change_id}/events.ndjson` | 每 Change 单文件追加 | 60 天后自动清理 |
| `~/.hermes/telemetry/{change_id}/manifest.json` | 汇总信息 | 同 events.ndjson |

### 清理

```bash
# 手动清理 30 天前的数据
find ~/.hermes/telemetry/ -type d -mtime +30 -exec rm -rf {} + 2>/dev/null

# 完全禁用删除（不推荐）
test -f ~/.hermes/telemetry/DISABLE_AUTO_CLEANUP && echo "auto-cleanup disabled" || echo "auto-cleanup active"
```
