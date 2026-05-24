# Architect → Coder 交接清单

> Architect Agent 在完成 Design + Tasks 后，确认以下清单再交给 Coder Agent。

---

## 交接前自查

### Design 文档

- [ ] 技术方案对比完成（≥2 方案，Standard/Enhanced）
- [ ] 架构设计清晰（含架构图或 ASCII 图）
- [ ] 关键决策记录完整（选项、选择、理由）
- [ ] 每个模块有接口定义
- [ ] 产出物清单完整（文件路径精确）

### Tasks 文档

- [ ] 每 Task 估时 ≤ 15min
- [ ] 每 Task 有 exact 文件路径
- [ ] 每 Task 有依赖声明
- [ ] 每 Task 有 AC 覆盖编号
- [ ] 每 Task 有验证命令（含期望输出）
- [ ] 执行顺序明确（依赖图）

### 数据/API 契约

- [ ] 数据模型定义完整（字段、类型、约束）
- [ ] API 契约完整（请求/响应/错误码）
- [ ] 前端接口无歧义（如涉及前端）

---

## Coder Agent 接收确认

Coder Agent 收到 Design + Tasks 后应确认：

1. Tasks 的每个步骤能独立执行（不需要额外上下文）
2. 文件路径能直接 `write_file`（不需要猜测位置）
3. 验证命令能在本地运行（不需要 CI 环境）

如有疑问，Coder Agent 应：
- 优先从 Design 中寻找答案
- 如 Design 未覆盖 → 标记为 "需 Architect 澄清" 并暂停
