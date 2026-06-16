# PRD: Profile+Soul 架构落地与机制验证

> 变更 ID: 001-profile-soul-架构落地与机制验证
> 版本: 1.0 | 最后更新: 2026-06-16

---

## 背景与目标

**背景**:
Hermes SDD 框架的核心创新是 **Profile + Soul 双层差异化架构**，通过独立 Profile 配置（模型/Provider/工具集）+ SOUL.md 思维特质（人格/思维模式/输出风格）实现真正的角色分离。目前架构设计已完成（architecture.md、AGENTS.md），但需要实际落地配置并验证各机制是否按预期工作。

**目标**:
1. 完成 6 个 SDD Profile 的完整配置（config.yaml + SOUL.md）
2. 验证 Profile 隔离机制、Soul 思维特质注入、Workspace 绑定机制的正确性
3. 通过端到端流程走通，确认异构评审模式、跨阶段产物传递正常工作
4. 产出可复用的 Profile 初始化脚本和验证工具

---

## 用户场景

### 场景 1：SDD 框架维护者初始化 Profile 环境

- **角色**: SDD 框架维护者 / 开发者
- **前置条件**: Hermes Agent v2.1.0+ 已安装，项目代码已克隆
- **操作流程**:
  1. 运行 `scripts/init-profiles.sh` 脚本
  2. 脚本自动创建 6 个 Profile（sdd-po、sdd-ba、sdd-architect、sdd-coder、sdd-reviewer、sdd-qa）
  3. 每个 Profile 自动配置对应的 config.yaml（模型、Provider、工具集）
  4. 每个 Profile 自动配置对应的 SOUL.md（角色思维特质）
- **期望结果**:
  - 6 个 Profile 全部创建成功
  - 每个 Profile 的 config.yaml 包含正确的模型和 Provider 配置
  - 每个 Profile 的 SOUL.md 包含该角色特有的思维模式、工作原则、禁止事项
  - 运行 `hermes profile list` 能看到所有 6 个 Profile

### 场景 2：SDD 框架维护者验证 Profile 隔离机制

- **角色**: SDD 框架维护者 / 开发者
- **前置条件**: 6 个 Profile 已创建完成
- **操作流程**:
  1. 使用 `hermes -p sdd-po` 启动 PO Profile
  2. 验证加载的是 doubao-seed-2.0-pro 模型和火山引擎 Provider
  3. 验证 PO 的 Soul 思维特质已注入系统提示词
  4. 使用 `hermes -p sdd-reviewer` 启动 Reviewer Profile
  5. 验证加载的是 deepseek-v4-pro 模型和 DeepSeek Provider
  6. 验证 Reviewer 的批判性思维 Soul 已注入
- **期望结果**:
  - 不同 Profile 启动时加载各自独立的模型配置
  - 不同 Profile 启动时加载各自独立的 Provider 配置
  - SOUL.md 内容正确注入到系统提示词中
  - Profile 之间完全隔离，互不影响

### 场景 3：SDD 框架维护者验证端到端 SDD 流程

- **角色**: SDD 框架维护者 / 开发者
- **前置条件**: 6 个 Profile 配置完成且隔离验证通过
- **操作流程**:
  1. 使用 orchestrator 发起一个测试变更（如一个简单的 Skill 增强）
  2. 观察 Kanban 调度器正确分配任务到对应 Profile 的 Worker
  3. 验证每个阶段的产物（prd.md → spec.md → design.md → 代码 → review-report.md）正确生成
  4. 验证 Workspace 的 dir 类型绑定正确，产物持久化到项目目录
- **期望结果**:
  - Kanban 任务正确分配给对应的 Profile Worker
  - 每个阶段产物按预期生成，路径正确
  - 产物持久化在项目的 `docs/changes/` 目录下
  - 异构评审模式生效（Reviewer 使用不同的模型/Provider）

---

## 功能范围

### In Scope（本次包含）

1. **6 个 Profile 的完整配置**
   - sdd-po: PO 角色配置（doubao-seed-2.0-pro + 火山引擎 + 用户思维 Soul）
   - sdd-ba: BA 角色配置（doubao-seed-2.0-pro + 火山引擎 + MECE 思维 Soul）
   - sdd-architect: Architect 角色配置（glm-5.1 + 火山引擎 + 架构思维 Soul）
   - sdd-coder: Coder 角色配置（doubao-seed-2.0-code + 火山引擎 + TDD 思维 Soul）
   - sdd-reviewer: Reviewer 角色配置（deepseek-v4-pro + DeepSeek + 批判性思维 Soul）
   - sdd-qa: QA 角色配置（doubao-seed-2.0-pro + 火山引擎 + 破坏性测试 Soul）

2. **Profile 初始化脚本**
   - `scripts/init-profiles.sh`: 一键创建所有 Profile 的 Shell 脚本
   - 支持增量更新（Profile 已存在时跳过或更新）

3. **机制验证工具集**
   - Profile 隔离检查脚本
   - Soul 注入验证脚本
   - Workspace 绑定验证脚本
   - 端到端流程冒烟测试脚本

4. **文档更新**
   - AGENTS.md 的 Profile 配置示例完善
   - architecture.md 的机制说明补充
   - 新增 PROFILES-GUIDE.md（Profile 使用指南）

5. **【P0】orchestrator 状态机自动化**
   - 新增 Kanban 任务状态轮询机制（每 10s 检查一次）
   - 任务完成后自动触发门禁检查（transition）
   - 任务失败后自动更新 .sdd-state.json 的 blocked_reason 字段
   - 最多 3 次自动重试机制
   - 目标：实现真正"无人值守"的全自动流程驱动

6. **【P1】门禁检查增强**
   - L1 检查：PRD 必须包含（背景/目标/用户场景/功能范围/验收标准）5 大章节
   - L1+L2 检查：Spec 必须包含 AC 且格式符合 Given-When-Then 规范
   - L2 检查：Design 必须包含（架构图/接口定义/数据结构/任务拆分）
   - L2.5 检查：代码必须有对应的测试用例
   - 目标：门禁不再是"文件存在检查"，而是"内容质量检查"

7. **【P1】模型使用审计**
   - 每个阶段完成后，在 .sdd-state.json 中记录实际使用的模型、Provider、Kanban 任务ID
   - 新增 `orchestrator.py audit` 命令输出模型使用审计报告
   - 目标：事后可审计，确认各阶段确实用了正确的模型

8. **【P1】Profile 标准化初始化脚本**
   - 从 AGENTS.md 的 role_to_profile 配置自动生成所有 Profile
   - 自动生成 config.yaml（模型/Provider/API Key）
   - 自动生成 SOUL.md（从模板库生成各角色思维特质）
   - 支持增量更新（Profile 已存在时跳过或覆盖）
   - 目标：一行命令完成 6 个 Profile 的完整初始化

9. **【P2】体验优化**
   - orchestrator status 增加进度条可视化 `[●●●○○○○○]`
   - orchestrator status 显示当前 Kanban 任务ID和产物清单
   - Kanban 任务 body 增加前置产物路径、输出格式要求
   - 新增中断恢复机制（会话断开后重新连接继续执行）
   - 新增产物哈希校验（防止手动修改）

### Out of Scope（本次不包含）

1. 不修改 Hermes Agent 核心代码（零侵入原则）
2. 不新增 SDD 流程阶段（保持现有 6 阶段不变）
3. 不修改现有 Skill 的核心逻辑（只做配置层面调整）
4. 不涉及多租户 Profile 隔离
5. 不涉及 Profile 的动态切换（热重载）

---

## 非功能需求（NFR）

| 类别 | 要求 | 指标 |
|------|------|------|
| 性能 | Profile 切换快速 | `hermes -p <profile>` 启动时间 < 2 秒 |
| 安全 | 敏感信息安全 | API Key 等敏感信息只存于各 Profile 的 `config.yaml`，不提交到 Git |
| 可用性 | 脚本可用性 | 初始化脚本在 Linux/macOS 下均可正常运行 |
| 可维护性 | 配置一致性 | 所有 Profile 配置遵循统一的目录结构和命名规范 |
| 可扩展性 | 新增 Profile 便捷 | 新增一个 Profile 的时间 < 10 分钟（基于模板） |
| 可靠性 | 隔离性保证 | 一个 Profile 的配置变更不影响其他任何 Profile |

---

## 验收标准（高层级）

1. ✅ **6 个 Profile 创建完成**：`~/.hermes/profiles/` 目录下存在 sdd-po、sdd-ba、sdd-architect、sdd-coder、sdd-reviewer、sdd-qa 共 6 个 Profile 目录

2. ✅ **每个 Profile 配置完整**：每个 Profile 目录下包含：
   - `config.yaml`：正确的模型、Provider、工具集配置
   - `SOUL.md`：该角色特有的思维特质定义

3. ✅ **Profile 隔离验证通过**：
   - sdd-po 启动时使用 doubao-seed-2.0-pro 模型
   - sdd-reviewer 启动时使用 deepseek-v4-pro 模型和 DeepSeek Provider
   - 修改一个 Profile 的配置不影响其他 Profile

4. ✅ **Soul 注入验证通过**：启动任意 Profile 时，SOUL.md 的内容出现在系统提示词中，影响 Agent 的输出风格

5. ✅ **Workspace 绑定验证通过**：Kanban Worker 启动时正确 cd 到项目目录，产物写入 `docs/changes/{change_id}/`

6. ✅ **端到端流程验证通过**：使用一个测试变更走通 PO → BA → Architect → Coder → Reviewer → QA 全流程，各阶段产物正常生成

7. ✅ **文档完整**：AGENTS.md、architecture.md 已更新，新增 PROFILES-GUIDE.md

---

## 风险与假设

### 风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|:---:|------|
| Hermes 版本不兼容，Profile 功能异常 | 高（流程阻塞） | 中 | 在初始化脚本中加入版本检测，提前报错并给出降级方案 |
| SOUL.md 内容未正确注入系统提示词 | 中（角色差异化失效） | 低 | 编写专门的验证脚本，检查系统提示词是否包含 Soul 内容 |
| API Key 配置错误导致模型调用失败 | 中（无法验证） | 中 | 在验证脚本中加入模型连通性检查，提前发现配置问题 |
| Workspace 路径计算错误，产物写入位置不对 | 高（跨阶段共享失效） | 中 | 使用绝对路径推导，加入路径存在性检查和写入权限验证 |

### 假设

- Hermes Agent 版本 ≥ v2.1.0，支持 Profile 功能和 Kanban `--assignee` 参数
- 用户已配置好各 Provider 的 API Key（火山引擎、DeepSeek）
- 执行初始化脚本的用户对 `~/.hermes/profiles/` 目录有读写权限
- 项目代码位于 `hermes-harness` 目录，脚本可以正确推导绝对路径
- Kanban gateway 已配置好，支持跨 Profile 任务通知
