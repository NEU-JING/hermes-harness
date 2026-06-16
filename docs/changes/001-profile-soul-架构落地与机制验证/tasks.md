# Tasks: Profile+Soul 架构落地与机制验证

> 变更 ID: 001-profile-soul-架构落地与机制验证
> 版本: 1.0 | 最后更新: 2026-06-16
> 基于 Design v1.0

---

## 任务统计

| 优先级 | 数量 |
|--------|------|
| P0 | 6 |
| P1 | 3 |
| P2 | 1 |
| **总计** | **10** |

---

## Phase 1: Profile 配置与初始化（P0）

### Task 1-1: 完善 AGENTS.md 的 sdd_config 声明式配置
- **优先级**: P0
- **负责角色**: Coder
- **估时**: 30min
- **前置依赖**: 无
- **验收标准**:
  - AGENTS.md 的 `sdd_config.role_to_profile` 完整定义 6 个角色的 Profile 映射
  - 每个角色包含 `name`、`model`、`provider`、`skill` 四个字段
  - 每个角色的 Soul 描述包含核心思维模式、角色原则、禁止事项三要素
  - **零硬编码原则**：脚本完全从配置读取，不写死任何模型名或 Profile 名
  - YAML 格式正确，无语法错误

### Task 1-2: 创建 Profile 模板库
- **优先级**: P0
- **负责角色**: Coder
- **估时**: 45min
- **前置依赖**: Task 1-1
- **验收标准**:
  - `scripts/templates/profile/config.yaml.template` 包含所有必要的配置字段
  - `scripts/templates/profile/SOUL.md.template` 包含标准化的三要素结构
  - 模板中的占位符（`{{model}}`、`{{provider}}`、`{{role_name}}` 等）定义清晰
  - 模板格式正确，可被脚本正确替换

### Task 1-3: 实现 init-profiles.sh 初始化脚本
- **优先级**: P0
- **负责角色**: Coder
- **估时**: 60min
- **前置依赖**: Task 1-2
- **验收标准**:
  - 支持标准初始化（`bash scripts/init-profiles.sh`）
  - 支持列表查询（`-l`）
  - 支持强制重建（`-f`，带交互确认）
  - 自动检测 Hermes 版本 ≥ v2.1.0，版本过低时拒绝执行
  - Profile 已存在时默认跳过（`--force` 除外）
  - 在 Linux 和 macOS 下均可正常运行
  - 输出创建/更新成功的 Profile 数量统计和每个 Profile 的处理日志

---

## Phase 2: 机制验证工具集（P0）

### Task 2-1: 实现 Profile 隔离检查脚本
- **优先级**: P0
- **负责角色**: Coder
- **估时**: 45min
- **前置依赖**: Task 1-3
- **验收标准**:
  - 脚本路径：`scripts/validate-profile-isolation.sh`
  - 输出每个 Profile 加载的模型名称、Provider 名称的对比表
  - 验证修改一个 Profile 的配置不影响其他 Profile
  - 失败项输出明确的错误信息（文件路径、期望值 vs 实际值）
  - 退出码：0 = 全部通过，1 = 存在失败项

### Task 2-2: 实现 Soul 注入验证脚本
- **优先级**: P0
- **负责角色**: Coder
- **估时**: 45min
- **前置依赖**: Task 1-3
- **验收标准**:
  - 脚本路径：`scripts/validate-soul-injection.sh`
  - 验证每个 Profile 系统提示词中包含对应 SOUL.md 的关键特质关键词
  - 核心思维模式、角色原则、禁止事项三要素的关键词都必须被检测到
  - 输出检测覆盖率报告（每个 Profile 命中了多少个关键词）
  - 退出码：0 = 全部通过，1 = 存在失败项

### Task 2-3: 实现 Workspace 绑定验证脚本
- **优先级**: P0
- **负责角色**: Coder
- **估时**: 30min
- **前置依赖**: Task 1-3
- **验收标准**:
  - 脚本路径：`scripts/validate-workspace-binding.sh`
  - 验证 Kanban Worker 的 CWD 被正确设置为项目根目录
  - 验证产物被写入 `docs/changes/{change_id}/` 目录
  - 退出码：0 = 全部通过，1 = 存在失败项

---

## Phase 3: orchestrator 状态机增强（P0-P1）

### Task 3-1: 实现 Kanban 任务状态轮询与自动 transition
- **优先级**: P0
- **负责角色**: Coder
- **估时**: 60min
- **前置依赖**: 无
- **验收标准**:
  - 每 10s 检查一次 Kanban 任务状态
  - 任务完成（done）后自动触发对应的状态转换和门禁检查
  - 任务失败（blocked）后自动记录原因到 `.sdd-state.json.blocked_reason`
  - 支持 `--watch` 模式持续监控
  - 轮询间隔可通过环境变量 `ORCHESTRATOR_POLL_INTERVAL` 配置

### Task 3-2: 实现模型使用审计功能
- **优先级**: P1
- **负责角色**: Coder
- **估时**: 45min
- **前置依赖**: Task 3-1
- **验收标准**:
  - 每个阶段完成后，在 `.sdd-state.json.state_history` 中记录实际使用的模型、Provider、Kanban 任务 ID
  - 新增 `orchestrator.py audit <change_id>` 命令输出模型使用审计报告
  - 审计报告包含：阶段名称、任务 ID、模型、Provider、执行时长
  - 支持导出 JSON 格式的审计报告

### Task 3-3: 实现门禁检查增强（L1 / L1+L2 / L2 / L2.5）
- **优先级**: P1
- **负责角色**: Coder
- **估时**: 90min
- **前置依赖**: Task 3-1
- **验收标准**:
  - **L1 检查（PRD）**: 检查是否包含背景/目标/用户场景/功能范围/验收标准 5 大章节
  - **L1+L2 检查（Spec）**: 检查是否包含 AC 且格式符合 Given-When-Then 规范
  - **L2 检查（Design）**: 检查是否包含架构图/接口定义/数据结构/任务拆分
  - **L2.5 检查（Code）**: 检查代码是否有对应的测试用例
  - 门禁检查失败时不允许进入下一阶段，输出详细的失败原因
  - 门禁检查结果记录在 `.sdd-state.json.lint_results`

### Task 3-4: 实现进度可视化与断点续传
- **优先级**: P2
- **负责角色**: Coder
- **估时**: 60min
- **前置依赖**: Task 3-1
- **验收标准**:
  - `orchestrator.py status <change_id>` 输出进度条 `[●●●○○○○○]`
  - 显示当前 Kanban 任务 ID 和状态
  - 显示已生成的产物清单
  - `orchestrator.py resume <change_id>` 从当前状态继续执行
  - 产物 SHA256 哈希记录在 `.sdd-state.json.artifacts` 中

---

## Phase 4: 文档分块生成机制实现（P0）

### Task 4-1: 在 ba-agent Skill 中集成三层分块生成机制
- **优先级**: P0
- **负责角色**: Coder
- **估时**: 120min
- **前置依赖**: 无
- **验收标准**:
  - ba-agent 生成 spec.md 时，先生成文档地图（document-map.json）
  - 按 Requirement 分块生成，每个 R 单独作为一个分块
  - 每个分块生成时携带完整的文档地图和上下文锚定信息
  - 所有分块完成后执行 L3 一致性审计
  - 合并后的 spec.md 格式正确、编号连续、术语统一
  - 单个 Requirement 超过 200 行时自动递归分块（按小节拆分）

### Task 4-2: 在 architect-agent Skill 中集成三层分块生成机制
- **优先级**: P0
- **负责角色**: Coder
- **估时**: 120min
- **前置依赖**: Task 4-1
- **验收标准**:
  - architect-agent 生成 design.md / tasks.md 时，先生成文档地图
  - 按"地图→方案→架构→任务"四阶段分块生成
  - 每个分块生成时携带完整的文档地图和上下文锚定信息
  - 所有分块完成后执行 L3 一致性审计
  - 合并后的文档格式正确、编号连续、术语统一
  - 单个章节超过 500 行时自动递归分块

---

## Phase 5: 文档更新与指南编写（P0）

### Task 5-1: 更新 AGENTS.md 补充 Profile 配置示例
- **优先级**: P0
- **负责角色**: Coder
- **估时**: 30min
- **前置依赖**: Task 1-1
- **验收标准**:
  - 补充 Reviewer 角色的完整 config.yaml 示例（含 DeepSeek Provider 配置）
  - 补充 SOUL.md 完整示例
  - 示例格式正确，可直接复制使用
  - 不破坏现有 YAML 配置格式

### Task 5-2: 更新 architecture.md 补充 Profile+Soul 机制说明
- **优先级**: P0
- **负责角色**: Coder
- **估时**: 45min
- **前置依赖**: Task 1-1
- **验收标准**:
  - 补充 Profile+Soul 双层架构的机制说明
  - 补充状态机调度流程图
  - 补充模型选型和分配策略说明
  - 与现有 architecture.md 风格一致

### Task 5-3: 新增 PROFILES-GUIDE.md 操作指南
- **优先级**: P0
- **负责角色**: Coder
- **估时**: 60min
- **前置依赖**: Task 1-3
- **验收标准**:
  - 包含 Profile 创建流程的完整步骤
  - 包含 Profile 管理（查看、更新、删除）的操作说明
  - 包含验证工具集的使用方法
  - 包含常见故障排查章节（至少 5 个常见问题及解决方案）
  - 包含最佳实践建议

---

## Phase 6: 端到端测试与验证（P1）

### Task 6-1: 实现端到端流程冒烟测试脚本
- **优先级**: P1
- **负责角色**: QA
- **估时**: 60min
- **前置依赖**: Task 2-1, 2-2, 2-3
- **验收标准**:
  - 脚本路径：`scripts/validate-end-to-end.sh`
  - 自动运行一个完整 SDD 流程（PO → BA → Architect）
  - 检查所有产物的路径清单和存在性
  - 输出测试报告（通过率、耗时统计）
  - 退出码：0 = 全部通过，1 = 存在失败项

---

## 依赖关系图

```
Task 1-1 (AGENTS.md 配置)
    ↓
Task 1-2 (模板库)
    ↓
Task 1-3 (init 脚本)
    ├───────────┬───────────┐
    ↓           ↓           ↓
Task 2-1    Task 2-2    Task 2-3    (验证脚本)
    │           │           │
    └───────────┴───────────┘
                ↓
Task 6-1 (端到端测试)

Task 3-1 (轮询 + auto transition)
    ├───────────┬───────────┐
    ↓           ↓           ↓
Task 3-2    Task 3-3    Task 3-4    (orchestrator 增强)

Task 4-1 (ba-agent 分块)
    ↓
Task 4-2 (architect-agent 分块)

Task 1-1
    ├───────────┬───────────┐
    ↓           ↓           ↓
Task 5-1    Task 5-2    Task 5-3    (文档更新)
```

---

## 关键路径

**Task 1-1 → Task 1-2 → Task 1-3 → Task 4-1 → Task 4-2**

这是最核心的路径，决定了整个 Profile+Soul 架构的落地。其他任务（验证脚本、orchestrator 增强、文档更新）可以并行进行。
