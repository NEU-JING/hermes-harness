# SDD 模型选择实战验证报告（生产环境）

> **日期**: 2026-06-16
> **项目**: hermes-harness
> **变更**: 001-profile-soul-架构落地与机制验证

---

## 核心结论

**模型选择的第一优先级是「输出长度上限」，其次才是推理能力。**

这是通过 2 次任务失败、耗时 30 分钟的真实生产环境验证得出的结论，而非理论推测。

---

## 失败案例复现（原始配置）

### 初始 AGENTS.md 配置（错误）

| Profile | 模型 | Provider | 失败阶段 | 失败原因 |
|---------|------|---------|---------|---------|
| sdd-ba | doubao-seed-2.0-pro | 火山引擎 | BA_ENTRY | 输出长度不足，截断导致 write_file 参数不完整 |
| sdd-architect | glm-5.1 | 火山引擎 | ARCHITECT_ENTRY | 输出长度不足，截断导致 write_file 参数不完整 |

### 错误日志

```bash
# BA 阶段失败日志
╭─ ⚕ Hermes ───────────────────────────────────────────────────────────────────╮
⚠️  Response truncated (finish_reason='length') - model hit max output tokens
    .
╰───────────────────────────────────────────────────────────────────────────────╯
  ┊ ✍️ preparing write_file…

Error: Response truncated due to output length limit
```

**根因链**:
```
1. Model max output tokens ≈ 2000
2. BA 阶段需要生成 ≈ 500 行 spec.md ≈ 6000 tokens
3. 模型输出在中间被截断
4. write_file 的 content 参数不完整
5. Agent 异常退出，但退出码是 0（成功）
6. 没有调用 kanban_complete（协议违反）
7. 调度器检测到 protocol violation → 重试 → 同样失败 → 标记为 blocked
```

---

## 修复后配置（生产验证通过）

| Profile | 模型 | Provider | 状态 | 核心理由 |
|---------|------|---------|------|---------|
| sdd-po | doubao-seed-2.0-pro | 火山引擎 | ✅ 通过 | PRD 约 200 行，输出可控 |
| sdd-ba | **deepseek-v4-pro** | DeepSeek | ✅ 通过 | Spec 约 500 行+详细AC，需要大输出 |
| sdd-architect | **deepseek-v4-pro** | DeepSeek | ✅ 通过 | Design + Tasks 约 400 行，需要大输出+强推理 |
| sdd-coder | doubao-seed-2.0-code | 火山引擎 | ⏳ 待验证 | 按 Task 拆分，单 Task 输出可控 |
| sdd-reviewer | deepseek-v4-pro | DeepSeek | ⏳ 待验证 | 异构评审 + 强推理 |
| sdd-qa | doubao-seed-2.0-pro | 火山引擎 | ⏳ 待验证 | 测试报告输出可控 |

**输出长度对比（实测）**:
- doubao-seed-2.0-pro: ~2000 tokens max output → ❌ 不够生成 spec.md
- deepseek-v4-pro: ~8000 tokens max output → ✅ 可以一次性生成完整 spec.md

---

## 模型选择决策树（生产版本）

```
开始选择模型
    ↓
┌─ 这个阶段需要生成 > 300 行文档吗？
│  ├─ Yes → 必须用 deepseek-v4-pro（或同等输出长度模型）
│  │     影响阶段：BA、Architect
│  │
│  └─ No → 进入下一层判断
│
├─ 这个阶段需要强推理能力吗？
│  ├─ Yes → deepseek-v4-pro / glm-5.1
│  │     影响阶段：Reviewer、Architect（已在上一层覆盖）
│  │
│  └─ No → 进入下一层判断
│
└─ 这个阶段需要代码生成能力吗？
   ├─ Yes → doubao-seed-2.0-code
   │     影响阶段：Coder
   │
   └─ No → doubao-seed-2.0-pro
         影响阶段：PO、QA
```

---

## 关键参数参考

### 各阶段预期输出长度

| 阶段 | 产物 | 预期行数 | 预估 tokens | 推荐模型 |
|------|------|---------|-----------|---------|
| PO | prd.md | 150-250 | 2000-3000 | doubao-seed-2.0-pro |
| BA | spec.md | 400-600 | 5000-8000 | **deepseek-v4-pro** |
| Architect | design.md + tasks.md | 300-500 | 4000-6000 | **deepseek-v4-pro** |
| Coder | 代码 + completion-report.md | 按 Task 拆分 | 可控 | doubao-seed-2.0-code |
| Reviewer | review-report.md | 150-300 | 2000-4000 | deepseek-v4-pro |
| QA | qa-report.md | 100-200 | 1500-3000 | doubao-seed-2.0-pro |

### Provider 切换注意事项

从火山引擎切换到 DeepSeek Provider 时，必须验证：
1. API Key 有足够额度
2. 网络可以访问 api.deepseek.com（不需要代理）
3. 模型名称拼写正确：`deepseek-v4-pro`（不是 `deepseek-chat` 或其他）

**验证命令**:
```bash
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer sk-xxxxxx" \
  | jq '.data[].id' | grep deepseek
```

---

## 经验教训

1. **不要信任模型文档的 max output 参数** - 实际生产环境中经常会更低，可能是服务端限流
2. **不要假设"推理能力强 = 输出长度大"** - glm-5.1 推理能力强但输出长度限制比 deepseek-v4-pro 小得多
3. **截断是静默失败** - 不会有明确的"输出太长"错误，只会看到 `finish_reason='length'` 在 debug 日志里
4. **协议违反是连锁反应** - 输出截断 → write_file 失败 → Agent 异常退出但 rc=0 → 不调用 kanban_complete → 调度器认为崩溃 → blocked

---

## 快速检查清单

启动 SDD 流程前必须确认：
- [ ] sdd-ba config.yaml 用的是 deepseek-v4-pro
- [ ] sdd-architect config.yaml 用的是 deepseek-v4-pro
- [ ] DeepSeek API Key 有效且有额度
- [ ] 网络可以访问 api.deepseek.com
- [ ] orchestrator.py 的 role_to_profile 映射正确
