# Spec: Profile+Soul 架构落地与机制验证

> 变更 ID: 001-profile-soul-架构落地与机制验证
> 版本: 1.0 | 最后更新: 2026-06-16
> 基于 PRD v1.0

---

## 功能概述

完成 SDD 框架 6 个 Profile 的完整配置落地，验证 Profile 隔离机制、Soul 思维特质注入、Workspace 绑定机制，并通过 orchestrator 状态机自动化、门禁检查增强、模型审计等增强能力实现端到端流程的"无人值守"全自动驱动。

---

## 详细需求

### Requirement 1: 6 个 Profile 的完整配置 ([P0])

**描述**: 创建 6 个 SDD Profile（sdd-po / sdd-ba / sdd-architect / sdd-coder / sdd-reviewer / sdd-qa），每个 Profile 包含 config.yaml 和 SOUL.md，以及对应的 Skill 符号链接。

**输入**:
- AGENTS.md 中的 `sdd_config.role_to_profile` 映射表
- 项目 `skills/sdd/` 目录下的各角色 Skill

**输出**:
- `~/.hermes/profiles/sdd-po/` — config.yaml + SOUL.md + skills/po-agent → 符号链接
- `~/.hermes/profiles/sdd-ba/` — config.yaml + SOUL.md + skills/ba-agent → 符号链接
- `~/.hermes/profiles/sdd-architect/` — config.yaml + SOUL.md + skills/architect-agent → 符号链接
- `~/.hermes/profiles/sdd-coder/` — config.yaml + SOUL.md + skills/coder-agent → 符号链接
- `~/.hermes/profiles/sdd-reviewer/` — config.yaml + SOUL.md + skills/reviewer-agent → 符号链接
- `~/.hermes/profiles/sdd-qa/` — config.yaml + SOUL.md + skills/qa-agent → 符号链接

**约束**:
- 模型分配必须与 AGENTS.md 的 Profile 能力矩阵一致
- SOUL.md 内容必须包含：核心思维模式、角色原则、禁止事项三部分
- config.yaml 的 `skills.external_dirs` 指向项目 `skills/` 目录

---

### Requirement 2: Profile 初始化脚本 ([P0])

**描述**: `scripts/init-profiles.sh` 一键脚本，支持标准初始化、强制重建、列表查询三种模式。自动完成 Hermes 版本检查、权限验证、Profile 创建/更新。

**输入**:
- 命令行参数：`-h` / `-l` / `-f` / `-v`
- 环境变量：`HERMES_HOME`（可选，默认 `~/.hermes`）

**输出**:
- 创建/更新成功的 Profile 数量统计
- 每个 Profile 的处理日志（成功/跳过/失败）
- 总耗时统计

**约束**:
- 必须检测 Hermes 版本 ≥ v2.1.0
- 必须在 Linux 和 macOS 下正常运行
- Profile 已存在时默认跳过（`--force` 除外）
- 强制模式需要用户交互确认

---

### Requirement 3: 机制验证工具集 ([P0])

**描述**: 提供 4 个独立验证脚本，分别验证 Profile 隔离、Soul 注入、Workspace 绑定、端到端流程。

**输入**:
- Profile 名称列表
- 项目根路径

**输出**:
- Profile 隔离检查：每个 Profile 加载的模型名称、Provider 名称的对比表
- Soul 注入验证：每个 Profile 系统提示词中是否包含对应 SOUL.md 的关键特质关键词
- Workspace 绑定验证：Kanban Worker 的 CWD 是否正确，产物是否写入 `docs/changes/{change_id}/`
- 端到端流程冒烟测试：一个完整 SDD 流程中所有产物的路径清单和存在性检查

**约束**:
- 每个验证脚本必须独立可运行
- 失败项必须输出明确错误信息（文件路径、期望值 vs 实际值）
- 退出码：0 = 全部通过，1 = 存在失败项

---

### Requirement 4: 文档更新 ([P0])

**描述**: 更新 AGENTS.md 和 architecture.md，新增 PROFILES-GUIDE.md。

**输入**:
- 当前 AGENTS.md、architecture.md 内容
- Profile 实际配置经验

**输出**:
- `AGENTS.md`：补充 Profile 配置示例（如 Reviewer 的完整 config.yaml 示例）
- `docs/current/architecture.md`：补充 Profile+Soul 双层架构的机制说明
- `docs/current/PROFILES-GUIDE.md`：Profile 创建/管理/验证的完整操作指南

**约束**:
- AGENTS.md 更新不破坏现有 YAML 配置格式
- PROFILES-GUIDE.md 必须包含常见故障排查章节

---

### Requirement 5: orchestrator 状态机自动化 ([P0])

**描述**: orchestrator 新增 Kanban 任务状态轮询机制，自动触发门禁检查和状态推进，支持失败重试和 blocked_reason 记录。

**输入**:
- 当前 `.sdd-state.json` 的状态
- 对应的 Kanban 任务 ID
- Kanban 任务的当前状态（running / blocked / done）

**输出**:
- 状态轮询：每 10s 查询一次 Kanban 任务状态
- 自动推进：任务完成后自动执行 `transition` 到下一 CHECK 状态
- 失败处理：更新 `.sdd-state.json` 的 `blocked_reason` 字段
- 重试记录：重试次数和每次失败的简要原因

**约束**:
- 最多自动重试 3 次
- 3 次均失败后状态转为 `BLOCKED`，阻塞后续流程
- 轮询超时：单个任务最长等待 `max_runtime_seconds`（取自 Kanban 任务配置）
- 轮询间隔固定 10s（不随重试次数变化）

---

### Requirement 6: 门禁检查增强 ([P1])

**描述**: 将现有门禁从"文件存在检查"升级为"内容质量检查"，分 L1 / L1+L2 / L2 / L2.5 四个级别。

**输入**:
- L1 (PRD → PO_DONE)：`prd.md` 文件路径
- L1+L2 (BA → BA_DONE)：`spec.md` 文件路径
- L2 (Architect → ARCHITECT_DONE)：`design.md` 文件路径
- L2.5 (Coder → CODER_DONE)：代码目录和测试目录路径

**输出**:
- L1 检查：PRD 是否包含（背景与目标 / 用户场景 / 功能范围 / 非功能需求 / 验收标准）5 大章节
- L1+L2 检查：Spec 是否包含 AC 且每条 AC 格式符合 `#### Scenario AC{n}:` + WHEN/THEN/AND 链
- L2 检查：Design 是否包含（架构图 / 接口定义 / 数据结构 / 任务拆分）4 部分
- L2.5 检查：代码文件是否有对应的测试文件（命名约定：`test_*.py` 或 `*_test.py`）

**约束**:
- 章节检测基于标题正则匹配（如 `^## 背景与目标`），不依赖精确标题文本
- AC 格式检测基于 `#### Scenario AC` 前缀 + `WHEN` + `THEN` 关键字
- Design 检查允许架构图为 mermaid 代码块或 ASCII 图
- L2.5 允许测试文件数为 0 的情况（标记警告但不阻塞）

---

### Requirement 7: 模型使用审计 ([P1])

**描述**: 每个阶段完成后记录实际使用的模型、Provider、Kanban 任务 ID，并提供审计报告命令。

**输入**:
- Kanban 任务完成信息（任务 ID、Worker 使用的 Profile）
- Profile 的 config.yaml（读取模型和 Provider 名称）

**输出**:
- `.sdd-state.json` 中新增 `model_audit` 数组，每项包含 stage / model / provider / kanban_task_id
- `orchestrator.py audit <change_id>` 命令输出格式化的审计报告

**约束**:
- 审计记录必须在状态推进前写入（在 transition 操作中完成）
- 审计报告按阶段顺序排列，用表格形式展示
- 审计报告对比实际模型与预期模型（取自 role_to_profile 配置），标注差异

---

### Requirement 8: Profile 标准化初始化脚本 ([P1])

**描述**: 基于 AGENTS.md 的 `role_to_profile` 配置自动生成所有 Profile，而非硬编码配置。

**输入**:
- AGENTS.md 中的 `sdd_config.role_to_profile` 映射
- Profile 模板库（SOUL.md 模板、config.yaml 模板）

**输出**:
- 根据 `role_to_profile` 自动确定 Profile 名称、模型、Provider
- 自动生成每个 Profile 的 config.yaml 和 SOUL.md
- 支持增量更新（`--force` 覆盖现有）

**约束**:
- 模板库位于 `scripts/templates/profile/` 目录
- SOUL.md 模板中留有 `{{ role_name }}`、`{{ role_description }}` 等占位符
- config.yaml 模板中留有 `{{ model }}`、`{{ provider }}` 等占位符

---

### Requirement 9: 体验优化 ([P2])

**描述**: orchestrator status 增强进度条、Kanban 任务 ID 显示、产物清单、中断恢复、产物哈希校验。

**输入**:
- 当前 `.sdd-state.json`
- 关联的 Kanban 任务 ID

**输出**:
- 进度条：根据当前状态在 6 阶段流程中的位置渲染 `[●●●○○○○○]`
- 任务信息：显示当前 Kanban 任务 ID 和状态
- 产物清单：列出已生成的文件路径
- 中断恢复：`orchestrator.py resume` 从当前状态继续
- 哈希校验：产物文件 SHA256 记录在 `.sdd-state.json` 中

**约束**:
- 进度条阶段顺序固定：PO → BA → Architect → Coder → Reviewer → QA
- 哈希校验在 transition 时自动执行，不阻塞流程（仅记录）
- 中断恢复不重复执行已完成的状态

---

### Requirement 10: 三层一致性保障的文档分块生成机制 ([P0])

**描述**: 解决模型输出长度限制 + 文档一致性问题。不能简单按章节拆分，必须通过三层机制保障全局一致性。

**核心原则**: 先定全局结构，再填局部内容，最后审计一致性。

---

#### 第一层：文档地图 + 递归分块（Document Map + Progressive Unfolding）

**输入**:
- PRD 需求点列表
- Spec 的章节划分要求

**核心输出**（先生成，所有分块共享）：
```
document-map.json
├── outline:              # 完整章节大纲（带精确编号）
│   ├── "1. 背景"
│   ├── "2. 技术方案"
│   ├── "2.1 方案A"
│   └── ...
├── glossary:             # 全局术语表（统一定义）
│   ├── "分块生成": "将大文档拆成多块，分多次写入的机制"
│   ├── "文档地图": "全局结构与元数据的抽象表示"
│   └── ...
├── reference_registry:   # 跨章节引用注册表
│   ├── "T1": "Task 1: 文档地图生成"
│   └── ...
└── naming_conventions:   # 命名约定
    ├── "模块命名": "PascalCase"
    └── ...
```

---

##### 递归分块与渐进展开（应对极端大模块）

**问题场景**: 单个章节/小节本身就超过 500 行，即使拆到章节级还是会触发模型输出长度限制。

**解决方案**: 递归分块 + 渐进展开，最大深度 3 级。

| 分块层级 | 粒度 | 安全行数 | 携带的上下文 |
|---------|------|---------|------------|
| L1 | 章节级（如"2. 技术方案"） | ≤ 500 行 | 完整文档地图 + 前后章节 |
| L2 | 小节级（如"2.1 方案A"） | ≤ 200 行 | 完整文档地图 + 父章节摘要 + 前后小节 |
| L3 | 段落级（如"2.1.1 方案A原理"） | ≤ 100 行 | 完整文档地图 + 父小节完整内容 + 前后段落开头 |

**核心原则**:
- 🎯 **文档地图永不丢弃**：所有层级的分块都必须携带完整的文档地图，这是全局一致性的锚点
- 其他上下文随层级动态调整，确保总上下文不超过模型窗口限制
- 最大分块深度 = 3 级。如果 L3 还超，说明需求本身过大，触发人工审核标记

**渐进展开流程**（Agent 内部自动决策，不需要人工干预）：
```
1. 拿到分块任务（如"写 2. 技术方案"）
2. 先做行数估算：这部分大概需要多少行？
3. 如果估算 ≤ 200 行 → 直接生成
4. 如果估算 > 200 行 → 自动执行：
   a. 先生成本小节的子大纲（2.1, 2.2, 2.3...）
   b. 将子大纲追加到文档地图的 reference_registry
   c. 逐个生成 2.1, 2.2, 2.3...（每个按 L2/L3 规则处理）
5. 如果某子小节估算还超 → 递归继续拆
```

---

##### 合并与去重机制

所有分块生成完成后，合并时必须执行：

| 检查项 | 目的 | 执行方式 |
|-------|------|---------|
| **标题层级检查** | 避免"###"下面直接接"#"的层级错乱 | 正则匹配所有标题，检查层级跳变不超过 1 级 |
| **重复内容清理** | 相邻分块可能重复同一段背景介绍 | 比对相邻 5 行，相似度 > 80% 则去重 |
| **过渡语优化** | 自动生成的过渡语可能生硬重复 | 每章开头的过渡语统一风格，避免连续使用"上一章我们讨论了..." |
| **引用编号修正** | 递归拆分新增的子项编号可能与全局编号冲突 | 扫描所有编号引用，重新按文档顺序统一编号 |

---

##### 极端情况降级方案

如果 L3 分块后还是超长（单个段落极其复杂），触发降级流程：

1. **先写要点列表**：不写详细说明，先把所有要点列出来（控制在 10 行以内）
2. **再逐个要点展开**：每个要点单独作为一个分块（特殊情况可突破 L3 深度限制）
3. **标记人工审核**：在一致性审计报告中标注"⚠️ 此部分分块深度超过 L3，建议人工审核连贯性"

降级方案确保：
- 至少能产出完整的要点结构，不会完全卡住
- 有明确标记，用户知道哪里需要特别关注

**L1 约束**:
- 文档地图必须在生成分块内容之前 100% 完成
- 文档地图大小控制在 200 行以内，确保始终能放入上下文窗口
- 任何术语必须先在 glossary 中定义，才能在正文中使用

---

#### 第二层：上下文锚定（Context Anchoring）

**每块生成时的上下文前缀**：
```
【文档地图】
（完整的 document-map.json 内容）

【相邻上下文】
前一章节最后 3 段：
...

后一章节大纲：
...

【当前块任务】
生成第 2.1 节：方案A的详细描述
```

**约束**:
- 每个分块生成时，必须携带完整的文档地图（L1）
- 必须携带前一章节的最后 3 段和后一章节的大纲（L2）
- 每个分块控制在 100 行以内
- 分块开头必须有 1-2 句过渡语，衔接前一章节内容

---

#### 第三层：一致性审计（Consistency Audit）

所有分块生成并合并后，自动执行审计：

| 审计项 | 检查方法 | 修复方式 |
|--------|---------|---------|
| **术语一致性** | grep 所有术语，确认与 glossary 定义一致 | 列出不一致的术语，给出替换建议 |
| **引用一致性** | 检查所有 `见第X章`/`T{N}`/`图X` 引用是否存在且正确 | 列出无效引用和正确的目标编号 |
| **前后衔接** | 检查每章开头的过渡语是否与前章结尾衔接 | 给出重写建议 |
| **架构一致性** | 文字描述中的模块/接口名是否与 mermaid 架构图一致 | 列出不一致的命名 |

**输出**: 一致性审计报告（通过/警告/错误 + 修复建议）

---

#### Agent 技能要求：
- ba-agent：spec.md 按 Requirement 分块，先写文档地图，再写每个 R
- architect-agent：design.md 按"地图→方案→架构→任务"四阶段分块
- 所有 Agent 默认使用三层机制，不能一次性写完整文档
**约束**:
- 不依赖任何特定模型的输出长度能力
- 分块过程对用户透明，最终产物仍是完整的单个文件
- 支持断点续传（中断后从当前章节继续，不需要从头开始）
- 一致性审计必须通过，才能推进到下一阶段门禁

---

## Acceptance Criteria（验收标准）

### 初始化脚本 — 正常流程

#### Scenario AC1: 初始化脚本创建全部 6 个 Profile

- **WHEN** 执行 `bash scripts/init-profiles.sh`
- **AND** 目标环境 Hermes Agent 版本 ≥ v2.1.0
- **AND** `~/.hermes/profiles/` 目录不存在任何 SDD Profile
- **THEN** 脚本依次创建 sdd-po、sdd-ba、sdd-architect、sdd-coder、sdd-reviewer、sdd-qa 共 6 个 Profile
- **AND** 每个 Profile 目录下存在 `config.yaml` 文件
- **AND** 每个 Profile 目录下存在 `SOUL.md` 文件
- **AND** 每个 Profile 的 `config.yaml` 中 `skills.external_dirs` 指向项目 `skills/` 目录的绝对路径
- **AND** 脚本退出码为 0
- **AND** 输出末尾显示"成功创建/更新：6 / 6 个 Profile"

#### Scenario AC2: 初始化脚本幂等性 — 重复运行跳过已存在 Profile

- **WHEN** 所有 6 个 Profile 已存在
- **AND** 执行 `bash scripts/init-profiles.sh`（非 `--force` 模式）
- **THEN** 脚本对每个已存在的 Profile 输出"Profile 已存在，跳过创建"
- **AND** 不修改任何已有 Profile 的文件内容
- **AND** 脚本退出码为 0
- **AND** 输出末尾显示"成功创建/更新：6 / 6 个 Profile"

#### Scenario AC3: 初始化脚本 — 强制模式删除并重建

- **WHEN** 执行 `bash scripts/init-profiles.sh --force`
- **AND** 用户在交互确认中回答 `y` 或 `Y`
- **THEN** 脚本删除所有已存在的 Profile 目录
- **AND** 重新创建全部 6 个 Profile
- **AND** 每个 Profile 的 `config.yaml` 和 `SOUL.md` 为全新生成的内容
- **AND** 脚本退出码为 0

#### Scenario AC4: 初始化脚本 — 强制模式用户取消

- **WHEN** 执行 `bash scripts/init-profiles.sh --force`
- **AND** 用户在交互确认中回答非 `y` 或 `Y`（或直接回车）
- **THEN** 脚本输出"已取消"
- **AND** 不修改任何已有 Profile
- **AND** 脚本退出码为 0

#### Scenario AC5: 初始化脚本 — 版本过低被拒绝

- **WHEN** 执行 `bash scripts/init-profiles.sh`
- **AND** 目标环境 Hermes Agent 版本 < v2.1.0
- **THEN** 脚本输出"错误：Hermes 版本过低（当前: {version}）"
- **AND** 脚本退出码为 1
- **AND** 不创建任何 Profile

#### Scenario AC6: 初始化脚本 — macOS 兼容性

- **WHEN** 在 macOS 环境下执行 `bash scripts/init-profiles.sh`
- **AND** Hermes Agent v2.1.0+ 已安装
- **THEN** 脚本正常完成所有前置检查和 Profile 创建
- **AND** 不使用 Linux 专有命令（如 `read -p` 之外的特定依赖）
- **AND** 脚本退出码为 0

### Profile 配置完整性

#### Scenario AC7: Profile config.yaml 模型与 Provider 正确

- **WHEN** 初始化完成后
- **AND** 读取 `~/.hermes/profiles/sdd-po/config.yaml`
- **THEN** config.yaml 中 `model` 字段值为 `doubao-seed-2.0-pro`
- **AND** `provider` 字段值为 `volcengine`（火山引擎）

- **WHEN** 读取 `~/.hermes/profiles/sdd-reviewer/config.yaml`
- **THEN** config.yaml 中 `model` 字段值为 `deepseek-v4-pro`
- **AND** `provider` 字段值为 `deepseek`

- **WHEN** 读取 `~/.hermes/profiles/sdd-architect/config.yaml`
- **THEN** config.yaml 中 `model` 字段值为 `glm-5.1`

- **WHEN** 读取 `~/.hermes/profiles/sdd-coder/config.yaml`
- **THEN** config.yaml 中 `model` 字段值为 `doubao-seed-2.0-code`

#### Scenario AC8: Profile SOUL.md 内容包含角色特质三要素

- **WHEN** 初始化完成后
- **AND** 读取任意 Profile 的 `SOUL.md` 文件
- **THEN** SOUL.md 包含"核心思维模式"章节（含至少 2 条编号的思维模式）
- **AND** 包含"角色原则"或"工作原则"章节（含至少 2 条编号的原则）
- **AND** 包含"禁止事项"章节（含至少 3 条 `❌` 前缀的禁止项）

### Profile 隔离验证

#### Scenario AC9: 不同 Profile 加载独立的模型配置

- **WHEN** 执行 `hermes -p sdd-po config show model`（或等效配置读取命令）
- **THEN** 返回的模型名称为 `doubao-seed-2.0-pro`

- **WHEN** 执行 `hermes -p sdd-reviewer config show model`
- **THEN** 返回的模型名称为 `deepseek-v4-pro`

- **AND** 两个 Profile 的模型配置互不干扰

#### Scenario AC10: Profile 配置隔离 — 修改一个不影响其他

- **WHEN** 修改 `~/.hermes/profiles/sdd-ba/config.yaml` 的模型字段为 `test-model-only`
- **AND** 分别读取其他 5 个 Profile 的 config.yaml
- **THEN** sdd-po 的模型仍为 `doubao-seed-2.0-pro`
- **AND** sdd-reviewer 的模型仍为 `deepseek-v4-pro`
- **AND** sdd-architect 的模型仍为 `glm-5.1`
- **AND** sdd-coder 的模型仍为 `doubao-seed-2.0-code`
- **AND** sdd-qa 的模型仍为 `doubao-seed-2.0-pro`
- **AND** 所有其他 Profile 的 Provider 配置也未受影响

### orchestrator 状态机自动化

#### Scenario AC11: orchestrator 自动轮询 Kanban 任务状态

- **WHEN** orchestrator 进入 PO_ENTRY 状态并创建了 Kanban 任务
- **AND** Kanban 任务已分配给 Worker 且处于 `running` 状态
- **THEN** orchestrator 每 10 秒轮询一次任务状态
- **AND** 每次轮询输出到 orchestrator 日志
- **AND** 轮询不阻塞 orchestrator 进程对 `status` 命令的响应

#### Scenario AC12: orchestrator 任务完成后自动推进状态

- **WHEN** orchestrator 轮询到 Kanban 任务状态变为 `done`
- **THEN** orchestrator 自动执行门禁检查（如 PO_ENTRY → PO_CHECK 执行 L1 检查）
- **AND** 门禁通过后自动执行 `transition` 到下一状态（如 PO_CHECK → PO_DONE）
- **AND** 更新 `.sdd-state.json` 的 `current_state` 和 `state_history`

#### Scenario AC13: orchestrator 自动重试 — 单次失败后重试成功

- **WHEN** Kanban 任务失败（状态变为 `blocked` 或 Worker 返回错误）
- **AND** 当前重试次数 < 3
- **THEN** orchestrator 自动重新创建 Kanban 任务
- **AND** 新任务 body 中包含上一次失败的简要原因
- **AND** `.sdd-state.json` 的 `model_audit` 中记录重试次数
- **AND** 重试成功后状态正常推进

#### Scenario AC14: orchestrator 自动重试 — 3 次均失败后阻塞

- **WHEN** Kanban 任务连续失败 3 次
- **THEN** orchestrator 将状态更新为 `BLOCKED`
- **AND** `.sdd-state.json` 的 `blocked_reason` 字段记录失败原因
- **AND** `blocked_reason` 包含 Kanban 任务 ID 和最后一次 Worker 输出的前 500 字符
- **AND** orchestrator 停止轮询，不再自动推进

### 门禁检查增强

#### Scenario AC15: L1 门禁 — PRD 章节完整性检查通过

- **WHEN** 执行 L1 门禁检查
- **AND** `prd.md` 包含以下 5 个章节标题：
  - `## 背景与目标`（或含"背景"的标题）
  - `## 用户场景`（或含"用户场景" / "场景"的标题）
  - `## 功能范围`（或含"功能范围" / "范围"的标题）
  - `## 非功能需求`（或含"NFR" / "非功能"的标题）
  - `## 验收标准`（或含"验收"的标题）
- **THEN** 门禁返回通过（退出码 0）
- **AND** 状态推进到 PO_CHECK → PO_DONE

#### Scenario AC16: L1 门禁 — PRD 缺少必要章节被拒绝

- **WHEN** 执行 L1 门禁检查
- **AND** `prd.md` 缺少"非功能需求"章节
- **THEN** 门禁返回不通过（退出码 1）
- **AND** 错误信息指明"缺少章节：非功能需求"
- **AND** 状态不能推进到 PO_DONE

#### Scenario AC17: L1+L2 门禁 — Spec AC 格式检查通过

- **WHEN** 执行 L1+L2 门禁检查
- **AND** `spec.md` 包含至少 5 条 AC
- **AND** 每条 AC 以 `#### Scenario AC{n}:` 开头
- **AND** 每条 AC 包含 `WHEN` 关键字
- **AND** 每条 AC 包含 `THEN` 关键字
- **THEN** 门禁返回通过（退出码 0）

#### Scenario AC18: L1+L2 门禁 — Spec AC 格式不合规被拒绝

- **WHEN** 执行 L1+L2 门禁检查
- **AND** `spec.md` 中存在 AC 不包含 `WHEN` 关键字
- **THEN** 门禁返回不通过（退出码 1）
- **AND** 错误信息指明不符合格式的 AC 编号
- **AND** 状态不能推进到 BA_DONE

#### Scenario AC19: L2 门禁 — Design 完整性检查

- **WHEN** 执行 L2 门禁检查
- **AND** `design.md` 包含：
  - 架构图（mermaid 代码块或 ASCII 图，通过 ` ```mermaid ` 或 `┌─` 等 ASCII 字符检测）
  - 接口定义章节（含 API 端点或函数签名）
  - 数据结构章节（含表格或 JSON schema）
  - 任务拆分章节（含编号的任务列表）
- **THEN** 门禁返回通过（退出码 0）

#### Scenario AC20: L2.5 门禁 — 代码测试覆盖检查

- **WHEN** 执行 L2.5 门禁检查
- **AND** 代码目录包含 3 个 `.py` 文件（非 `__init__.py`）
- **AND** 每个代码文件存在对应的 `test_*.py` 文件
- **THEN** 门禁返回通过（退出码 0）

- **WHEN** 代码目录没有测试文件
- **AND** 执行 L2.5 门禁检查
- **THEN** 门禁不阻塞（退出码 0）
- **AND** 输出警告："未找到测试文件，请确认是否需要补充"

### 模型审计

#### Scenario AC21: 模型审计记录写入

- **WHEN** orchestrator 完成 PO_ENTRY → PO_DONE 的完整推进
- **THEN** `.sdd-state.json` 的 `model_audit` 数组中新增一条记录
- **AND** 该记录包含 `stage: "PO"`、`model: "doubao-seed-2.0-pro"`、`provider: "volcengine"`、`kanban_task_id`（非空字符串）
- **AND** 记录按阶段顺序排列

#### Scenario AC22: 审计报告命令输出

- **WHEN** 执行 `python orchestrator.py audit 001-profile-soul-架构落地与机制验证`
- **THEN** 输出一个表格，包含所有已完成阶段的模型审计记录
- **AND** 表格至少有 stage / model / provider / kanban_task_id 四列
- **AND** 对于已配置 role_to_profile 的阶段，表格中标注实际模型是否与预期一致

### Workspace 绑定与端到端

#### Scenario AC23: Kanban Worker 的 Workspace 绑定到项目目录

- **WHEN** orchestrator 创建 Kanban 任务时指定 `workspace_kind: "dir"` 和 `workspace_path` 为项目绝对路径
- **AND** Kanban Worker 启动
- **THEN** Worker 的工作目录为项目根路径
- **AND** Worker 输出的产物文件路径在 `docs/changes/{change_id}/` 下

#### Scenario AC24: 端到端流程产物完整性

- **WHEN** 使用 orchestrator 发起一个测试变更
- **AND** 流程走完 PO → BA → Architect → Coder → Reviewer → QA 全阶段
- **THEN** `docs/changes/{change_id}/` 目录下存在以下文件：
  - `prd.md`（PO 阶段产出）
  - `spec.md`（BA 阶段产出）
  - `design.md`（Architect 阶段产出）
  - 至少 1 个代码文件（Coder 阶段产出）
  - `review-report.md`（Reviewer 阶段产出）
- **AND** `.sdd-state.json` 的 `current_state` 为 `DONE`

### 体验优化

#### Scenario AC25: orchestrator status 显示进度条

- **WHEN** 执行 `python orchestrator.py status 001-profile-soul-架构落地与机制验证`
- **AND** 当前状态为 `BA_ENTRY`（流程第 2 阶段）
- **THEN** 输出包含进度条 `[●●○○○○○○]`（2 个实心点）
- **AND** 进度条共 6 个位置，分别对应 PO/BA/Architect/Coder/Reviewer/QA
- **AND** 输出包含当前 Kanban 任务 ID（如有）
- **AND** 输出包含已生成产物的文件路径清单

---

## 数据模型

### .sdd-state.json（扩展字段）

在现有结构基础上新增以下字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| `blocked_reason` | string \| null | 否 | 流程阻塞原因，状态为 BLOCKED 时写入 |
| `model_audit` | array | 否 | 各阶段模型使用审计记录 |
| `model_audit[].stage` | string | 是 | 阶段名称（PO / BA / ARCHITECT / CODER / REVIEWER / QA） |
| `model_audit[].model` | string | 是 | 实际使用的模型名称 |
| `model_audit[].provider` | string | 是 | 实际使用的 Provider 名称 |
| `model_audit[].kanban_task_id` | string | 是 | 对应的 Kanban 任务 ID |
| `model_audit[].retry_count` | integer | 否 | 该阶段的重试次数（0 表示一次成功） |
| `model_audit[].completed_at` | string | 否 | 该阶段完成时间（ISO 8601） |
| `product_hashes` | object | 否 | 产物文件 SHA256 校验值 |
| `product_hashes.<filename>` | string | 否 | 文件名 → SHA256 哈希 |

### Profile 模板配置（scripts/templates/profile/）

| 文件 | 说明 |
|------|------|
| `config.yaml.tmpl` | config.yaml 模板，含 `{{ model }}` `{{ provider }}` `{{ project_root }}` 占位符 |
| `SOUL.md.tmpl` | SOUL.md 模板，含 `{{ role_name }}` `{{ role_description }}` `{{ core_traits }}` 占位符 |
| `roles.json` | 角色定义文件，包含每个角色的 model / provider / traits 元数据 |

---

## 非功能需求细化

| 类别 | 原始 NFR | 细化指标 | 验证方式 |
|------|---------|---------|---------|
| 性能 | Profile 切换快速，启动 < 2s | `hermes -p sdd-po --version` 从命令执行到输出的挂钟时间 | `time hermes -p sdd-po --version` 输出 < 2.0s |
| 安全 | API Key 不提交到 Git | `~/.hermes/profiles/*/config.yaml` 文件不在 Git 跟踪范围内 | 检查 `.gitignore` 包含 `**/profiles/*/config.yaml` 规则 |
| 可用性 | 初始化脚本 Linux/macOS 兼容 | Shell 脚本禁止使用 Linux 专有命令（如 `grep -P` 的 PCRE） | 分别在 Ubuntu 22.04 和 macOS 14 上执行 |
| 可维护性 | 配置一致性 — 统一目录结构 | 所有 Profile 目录结构完全一致 | `diff <(ls -R sdd-po) <(ls -R sdd-ba)` 无差异（除文件名外） |
| 可扩展性 | 新增 Profile < 10 分钟 | 基于模板创建一个新角色 Profile 的耗时 | 使用 `scripts/add-profile.sh` 模板化创建新 Profile 并计时 |
| 可靠性 | 隔离性 — 配置变更零影响 | 修改一个 Profile 后其他 Profile 功能不受影响 | 修改 sdd-ba 的模型配置后，sdd-reviewer 启动仍使用 deepseek-v4-pro |

---

## Out of Scope（确认）

以下内容不在本 Spec 范围内，AC 不会覆盖：

1. 不修改 Hermes Agent 核心代码（零侵入原则）
2. 不新增 SDD 流程阶段（保持现有 6 阶段不变）
3. 不修改现有 Skill 的核心逻辑（只做配置层面调整）
4. 不涉及多租户 Profile 隔离
5. 不涉及 Profile 的动态切换（热重载）
