# Model Output Truncation Bug - 实战记录

> **日期**：2026-06-16
> **变更**：001-profile-soul-架构落地与机制验证
> **影响阶段**：BA_ENTRY

---

## 现象

BA 阶段 Kanban 任务执行 2 分钟后标记为 blocked，但退出码是 0（成功）。

### Kanban 诊断信息

```
!! [error] Agent crash x2: worker exited cleanly (rc=0) without calling kanban_complete
   or kanban_block — protocol violation
```

### 日志中的真实错误

```
⚠️ Response truncated (finish_reason='length') - model hit max output tokens
⚠️ Truncated tool call detected — retrying API call...
⚠️ Truncated tool call response detected again — refusing to execute
   incomplete tool arguments.

Error: Response truncated due to output length limit
```

---

## 根因分析

### 触发条件

1. **Profile 配置的模型输出长度不够**
   - sdd-ba 配置的模型：doubao-seed-2.0-pro
   - doubao-seed-2.0-pro max output tokens：≈ 2000 tokens
   - BA 阶段需要生成的 spec.md：≈ 500 行 = ≈ 4000 tokens

2. **截断的连锁反应**
   ```
   模型开始生成 write_file 参数
   → 输出到一半达到 token 限制
   → 模型返回不完整的 JSON tool call
   → Hermes 检测到截断，重试一次
   → 再次截断
   → 放弃执行，静默退出
   → 没有调用 kanban_complete
   → 调度器认为协议违反，标记 blocked
   ```

---

## 修复方案

### 立即修复

给 BA 和 Architect Profile 换用大输出长度的模型：

```yaml
# ~/.hermes/profiles/sdd-ba/config.yaml
model:
  default: deepseek-v4-pro  # 8000 tokens 输出
  provider: deepseek
  base_url: https://api.deepseek.com/v1
  api_key: sk-...
```

### 长期修复

1. orchestrator 增加**模型输出长度校验**，根据阶段产物预期长度自动选择合适的模型
2. Agent skill 增加**分段写入**机制，生成长文档时分批 write_file
3. 门禁检查增加 **write_file 完整性校验**

---

## 验证命令

```bash
# 查看任务状态
hermes kanban list | grep blocked

# 查看详细日志
hermes kanban log <task_id>

# 检查产物是否生成
ls -la docs/changes/<change_id>/
```

---

## 关键教训

> 模型选择的第一优先级是**输出长度上限**，其次才是推理能力。

各阶段最小输出长度要求（实战得出）：

| 阶段 | 产物 | 最小输出 tokens 要求 |
|------|------|---------------------|
| PO | prd.md | 2000 |
| BA | spec.md | 4000 |
| Architect | design.md | 4000 |
| Coder | 按 Task 拆分 | 2000 per Task |
| Reviewer | review-report.md | 2000 |
| QA | qa-report.md | 2000 |
