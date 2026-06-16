# Design: Profile+Soul 架构落地与机制验证

> 变更 ID: 001-profile-soul-架构落地与机制验证
> 版本: 1.0 | 最后更新: 2026-06-16
> 基于 Spec v1.0

---

## 1. 架构总览

### 1.1 核心设计原则

| 原则 | 说明 |
|------|------|
| **零侵入** | 不修改 Hermes Agent 核心代码，所有能力通过 Profile 配置和脚本实现 |
| **完全隔离** | 每个 Profile 独立配置、独立模型、独立 Skill，互不干扰 |
| **声明式驱动** | 所有配置集中在 AGENTS.md，脚本从配置自动生成，不硬编码 |
| **可审计** | 全流程模型使用可追溯、可验证、可复盘 |

### 1.2 系统组件关系

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGENTS.md (单一真相源)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ sdd-po       │  │ sdd-ba       │  │ sdd-architect│ ...     │
│  │ model: glm   │  │ model: glm   │  │ model: glm   │         │
│  │ soul: po     │  │ soul: ba     │  │ soul: arch   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                init-profiles.sh (模板化生成器)                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 模板库: config.yaml.template + SOUL.md.template         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ~/.hermes/profiles/                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ sdd-po   │  │ sdd-ba   │  │ sdd-arch │  │ ...      │       │
│  │ config   │  │ config   │  │ config   │  │          │       │
│  │ SOUL.md  │  │ SOUL.md  │  │ SOUL.md  │  │          │       │
│  │ skills@  │  │ skills@  │  │ skills@  │  │          │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                orchestrator.py (状态机调度器)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ 状态转换     │  │ Kanban 调度   │  │ 门禁检查     │         │
│  │ 模型审计     │  │ 断点续传     │  │ 产物校验     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Profile 配置架构

### 2.1 目录结构标准

```
~/.hermes/profiles/<profile-name>/
├── config.yaml          # 模型、Provider、API Key 配置
├── SOUL.md              # 角色思维特质定义
└── skills/              # Skill 符号链接
    ├── po-agent/        # → /root/workspace/hermes-harness/skills/sdd/po-agent
    ├── ba-agent/        # → ...
    └── ...
```

### 2.2 6 个 Profile 配置（完全声明式，用户可自定义）

**模型配置集中在 AGENTS.md，用户部署时自定义**：

```yaml
sdd_config:
  # 👇 用户在这里定义每个角色用什么模型
  role_to_profile:
    po:
      name: sdd-po
      model: doubao-seed-2.0-pro
      provider: volcengine
      skill: po-agent
    ba:
      name: sdd-ba
      model: doubao-seed-2.0-pro
      provider: volcengine
      skill: ba-agent
    architect:
      name: sdd-architect
      model: doubao-seed-2.0-pro  # 用户可以改成 glm-5.1 或其他
      provider: volcengine
      skill: architect-agent
    coder:
      name: sdd-coder
      model: doubao-seed-2.0-code
      provider: volcengine
      skill: coder-agent
    reviewer:
      name: sdd-reviewer
      model: deepseek-v4-pro
      provider: deepseek
      skill: reviewer-agent
    qa:
      name: sdd-qa
      model: doubao-seed-2.0-pro
      provider: volcengine
      skill: qa-agent
```

**设计原则**：
- ✅ **单一真相源**：所有模型配置集中在 AGENTS.md
- ✅ **零硬编码**：脚本完全从配置读取，不写死任何模型名
- ✅ **用户友好**：部署时只需要修改一个文件
- ✅ **可扩展**：新增模型/Provider 不需要改脚本，只需要改配置

---

## 3. 三层一致性保障的文档分块生成机制

### 3.1 机制概述

**问题**：大文档（spec.md / design.md）一次性生成时，易触发模型输出长度限制，且易出现前后不一致、术语不统一等问题。

**解决方案**：三层分块生成机制，确保文档一致性和完整性。

### 3.2 L1: 文档地图 + 递归分块

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
│   └── ...
├── reference_registry:   # 跨章节引用注册表
│   ├── "T1": "Task 1: 文档地图生成"
│   └── ...
└── naming_conventions:   # 命名约定
    ├── "模块命名": "PascalCase"
    └── ...
```

#### 递归分块算法

```python
def generate_chunk(section_name, depth=0, max_depth=3):
    # 1. 行数估算
    estimated_lines = estimate_lines(section_name)

    # 2. 如果小于阈值，直接生成
    if estimated_lines <= SAFE_LINES[depth]:
        return write_section(section_name, context=full_document_map)

    # 3. 否则拆分成子章节，递归继续
    child_sections = generate_sub_outline(section_name)
    update_document_map(child_sections)  # 追加到 reference_registry

    results = []
    for child in child_sections:
        results.append(generate_chunk(child, depth + 1, max_depth))

    # 4. 合并 + 去重 + 格式校正
    return merge_chunks(results)
```

**分块粒度阈值**：

| 深度 | 粒度 | 安全行数 | 携带上下文 |
|------|------|---------|-----------|
| 0 | 大章节（如 "2. 技术方案"） | ≤ 500 行 | 完整文档地图 |
| 1 | 小节（如 "2.1 方案A"） | ≤ 200 行 | 完整文档地图 + 父章节摘要 |
| 2 | 子小节（如 "2.1.1 原理"） | ≤ 100 行 | 完整文档地图 + 父小节完整内容 |
| 3 | 要点级 | ≤ 50 行 | 完整文档地图 + 降级处理标记 |

#### 合并与去重机制

所有分块生成完成后，自动执行：

| 检查项 | 执行方式 |
|-------|---------|
| **标题层级连续性** | 正则匹配所有 `##` 标题，检查编号连续且层级跳变不超过 1 级 |
| **重复内容清理** | 相邻分块 5 行滑动窗口比较，相似度 > 80% 则去重 |
| **过渡语统一** | 每章开头过渡语风格统一，避免连续使用相同句式 |
| **引用编号校正** | 扫描所有 `Table X` / `Figure X` / `Section X`，按出现顺序重新编号 |

#### 极端情况降级方案

如果 L3 分块后还是超长（单个段落极其复杂）：

1. **先写要点列表**：不写详细说明，先把所有要点列出来（控制在 10 行以内）
2. **再逐个要点展开**：每个要点单独作为一个分块
3. **标记人工审核**：在一致性审计报告中标注 `⚠️ 此部分分块深度超过 L3，建议人工审核连贯性`

### 3.3 L2: 上下文锚定

**每个分块生成时携带的上下文**：

```
[ 上下文头（固定携带）]
1. 全局文档地图（完整 outline + glossary + reference_registry）
2. 当前分块的位置（如 "2.1 方案A"，属于第 2 章的第 1 节）
3. 前一个分块的最后 5 行内容（保证衔接自然）
4. 后一个分块的标题和开头 2 行（保证逻辑连贯）

[ 分块内容 ]
... 生成本节内容 ...

[ 上下文尾（约束检查） ]
生成分块后，自动检查：
- 是否使用了 glossary 中未定义的术语？
- 是否新增了需要加入 reference_registry 的引用？
- 与前一个分块的衔接是否自然？
```

### 3.4 L3: 一致性审计

文档全部生成完成后，自动执行审计：

| 审计项 | 检查方法 |
|-------|---------|
| **术语一致性** | 提取所有专业术语，检查是否全部在 glossary 中定义，且定义前后一致 |
| **引用完整性** | 提取所有 `Table X` / `Figure X` / `Section X`，检查目标是否存在 |
| **编号连续性** | 检查所有标题编号、表格编号、图表编号是否连续无重复 |
| **格式一致性** | 检查代码块、列表、表格格式是否统一 |
| **分块深度标记** | 标记所有深度 > L3 的分块，提示人工审核 |

**审计输出**：`consistency-audit.json`，包含通过率、失败项、修复建议。

---

## 4. orchestrator 状态机增强

### 4.1 状态转换图

```
IDLE → PO_ENTRY → PO_CHECK → PO_DONE
                               ↓
                        BA_ENTRY → BA_CHECK → BA_DONE
                                           ↓
                                  ARCHITECT_ENTRY → ARCHITECT_CHECK → ARCHITECT_DONE
                                                                    ↓
                                                          CODER_ENTRY → ...
```

### 4.2 新增能力

| 能力 | 实现方式 |
|------|---------|
| **Kanban 任务状态轮询** | 每 10s 检查一次任务状态，完成后自动触发 transition |
| **任务失败自动处理** | 任务进入 blocked 状态时，自动记录原因到 `.sdd-state.json`，支持重试 |
| **模型使用审计** | 每个阶段完成后，记录实际使用的模型、Provider、Kanban 任务 ID |
| **断点续传** | 会话断开后，从当前状态继续执行，不重复已完成工作 |
| **进度可视化** | status 命令输出进度条 `[●●●○○○○○]` |
| **产物哈希校验** | 每个产物的 SHA256 记录在状态文件中，防止意外修改 |

### 4.3 门禁检查增强

| 门禁级别 | 检查内容 |
|---------|---------|
| **L1 (PRD → PO_DONE)** | PRD 必须包含 5 大章节（背景/目标/用户场景/功能范围/验收标准） |
| **L1+L2 (Spec → BA_DONE)** | Spec 必须包含 AC，且格式符合 Given-When-Then 规范 |
| **L2 (Design → ARCHITECT_DONE)** | Design 必须包含架构图、接口定义、数据结构、任务拆分 |
| **L2.5 (Code → REVIEW)** | 代码必须有对应的测试用例 |

---

## 5. 数据模型

### 5.1 .sdd-state.json 结构

```json
{
  "change_id": "001-xxx",
  "flow_level": "Standard",
  "current_state": "BA_DONE",
  "previous_state": "BA_CHECK",
  "state_history": [
    {
      "from_state": "IDLE",
      "to_state": "PO_ENTRY",
      "at": "2026-06-16T00:59:26Z",
      "trigger": "sdd_start",
      "kanban_task_id": "t_xxxxxx",
      "model_used": "doubao-seed-2.0-pro",
      "provider_used": "volcengine"
    }
  ],
  "artifacts": {
    "prd.md": {
      "sha256": "xxx",
      "generated_at": "2026-06-16T01:55:34Z",
      "kanban_task_id": "t_xxxxxx"
    }
  },
  "blocked_reason": null,
  "metadata": {
    "orchestrator_version": "2.1.0"
  }
}
```

### 5.2 document-map.json 结构

见 3.2 节。

---

## 6. 接口定义

### 6.1 orchestrator.py 命令行接口

```bash
# 状态转换
python3 orchestrator.py transition <change_id> <target_state>

# 查看当前状态
python3 orchestrator.py status <change_id>

# 断点续传
python3 orchestrator.py resume <change_id>

# 模型使用审计
python3 orchestrator.py audit <change_id>
```

### 6.2 init-profiles.sh 命令行接口

```bash
# 标准初始化
bash scripts/init-profiles.sh

# 列表查询
bash scripts/init-profiles.sh -l

# 强制重建（交互确认）
bash scripts/init-profiles.sh -f

# 版本信息
bash scripts/init-profiles.sh -v
```

### 6.3 验证脚本接口

```bash
# Profile 隔离检查
bash scripts/validate-profile-isolation.sh

# Soul 注入验证
bash scripts/validate-soul-injection.sh

# Workspace 绑定验证
bash scripts/validate-workspace-binding.sh

# 端到端流程冒烟测试
bash scripts/validate-end-to-end.sh
```

---

## 7. 任务拆分（Tasks）

见 tasks.md。

---

## 8. 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 火山引擎模型不稳定（返回空） | 高 | 中 | 增加重试机制（已配置 3 次重试）；极端情况下允许临时切换到 doubao-seed-2.0-pro 作为 fallback |
| Profile 权限问题 | 中 | 低 | 初始化脚本包含权限检查和错误提示 |
| 分块合并后格式错乱 | 中 | 低 | L3 一致性审计包含格式检查，自动校正常见问题 |
| 文档地图不完整导致上下文丢失 | 高 | 低 | 文档地图生成后必须先通过 L0 检查，才能开始分块生成 |
