# Design — SDD 框架全量一致性修复（D1-D10）

> **Technical Design Document**
> Change ID: `001-修复sdd框架一致性缺陷-quirks-md缺失-agent`
> 版本：1.0 | 状态：Draft

---

## 一、产出物清单

### 新建文件

```
project-root/
├── QUIRKS.md                          [D1: 新建，从 templates/ 复制]
├── skills/sdd/sdd-orchestrator/
│   ├── references/kanban-profile-integration.md      [D7: 新建]
│   ├── references/profile-soul-architecture.md       [D7: 新建]
│   ├── references/4-layer-document-consistency.md    [D7: 新建]
│   ├── references/phase-consistency-audit.md        [D7: 新建]
│   ├── references/sdd-for-planning.md               [D7: 新建]
│   ├── references/model-output-truncation-bug.md    [D7: 新建]
│   ├── references/model-selection-production-validation.md [D7: 新建]
│   └── references/orchestrator-fix-patterns.md      [D7: 新建]
```

### 修改文件

```
project-root/
├── AGENTS.md                            [D2-D3: 精简至纯配置]
├── docs/current/architecture.md         [D3: 补充 Profile+Section 章节]
├── docs/current/prd.md                  [D4: 追加版本更新记录]
├── docs/current/spec.md                 [D4: 追加 Delta 章节]
├── docs/current/design.md               [D4: 追加 Delta 章节]
├── skills/sdd/sdd-orchestrator/SKILL.md [D5: 全量替换为 v2.6.0]
├── skills/sdd/sdd-orchestrator/references/delegate-protocol.md    [D8]
├── skills/sdd/sdd-orchestrator/references/state-machine.md        [D8]
├── skills/sdd/sdd-orchestrator/references/incremental-mode.md     [D8]
├── skills/sdd/sdd-orchestrator/references/interrupt-recovery.md   [D8]
├── skills/sdd/sdd-orchestrator/references/skill-maintenance-pattern.md [D8]
├── skills/sdd/sdd-orchestrator/references/pr-and-review-flow.md   [D8]
├── skills/sdd/sdd-orchestrator/scripts/orchestrator.py            [D9: task body 增强]
├── ~/.hermes/profiles/sdd-*/config.yaml                           [D10: 修复 API Key]
├── docs/archive/001-profile-soul-架构落地与机制验证/manifest.json [D4: 归档补全]
```

### 删除文件

```
project-root/scripts/setup-sdd-profiles.sh.deprecated  [D4: 清理]
```

**总计**: ~30 个文件变更（8 新建，18 修改，1 删除）

---

## 二、技术方案对比（Brainstorming）

### 方案 A：全量替换安装版（Sync from Installed）

**描述**：将已修复的 installed skill（`~/.hermes/skills/sdd/sdd-orchestrator/`）全量复制回源码目录。installed 版本已是 v2.6.0，包含所有引用文件和更新后的 orchestrator.py。

**优点**：
- 最大程度复用已完成的修复工作
- 一致性高（installed 版本经过实战验证）
- 速度快（全量 cp 即可，无需逐文件修补）

**缺点**：
- installed 版本可能包含与 repo 路径相关的差异（如符号链接 vs 硬路径）
- 无法细粒度控制哪些变更回到 repo（可能存在不相关的实验性改动）
- 全量替换会覆盖 repo 中可能存在的自定义内容

---

### 方案 B：增量修复源码（逐文件 Patch）

**描述**：不依赖 installed 版本，对源码逐文件进行针对性修复。SKILL.md 替换 Agent Delegation 章节，references/ 文件逐个添加/修改。

**优点**：
- 精细控制（只恢复需要的变更）
- 保留源码的历史注释和项目特定内容
- 可审计（每处改动都有明确的 PR 记录）

**缺点**：
- 工作量大（6 个 references/ 文件逐个迁移）
- 容易遗漏（installed 版本中 8 个新参考文件需要手动从 installed copy 过来）
- 协调风险（不同文件的 delegate_task→Kanban 替换需保持术语一致）

**适用场景**：长期维护、需要完整审计追溯的正式项目

---

### 方案 C：混合模式（Template-based Sync + Targeted Patches）

**描述**：将 SKILL.md 和所有 references/ 文件从 installed 复制到源码，再对差异进行定向 patch。8 个缺失的 reference 文件直接复制；6 个旧 reference 文件用 `diff` 识别 installed vs source 的差异后选择性 patch；orchestrator.py 的 D9 上下文增强单独实现。

**优点**：
- 兼顾修复速度和精准控制
- 缺失文件直接复制（零风险）
- 旧文件差异定向合并（避免覆盖不需要的改动）
- D9 是纯新增逻辑，不与 installed 版本冲突

**缺点**：
- 需要两步操作（sync + patch），流程稍复杂
- 依赖 `diff` 工具，结果需要人工审查

**适用场景**：本变更的实际情况 — 既有大量同步需求（SKILL.md + 8 个 ref），又有定向修复需求（6 个旧 ref + orchestrator.py）

---

### 方案对比总结

| 维度 | 方案 A 全量替换 | 方案 B 增量修复 | **方案 C 混合模式** |
|------|:---:|:---:|:---:|
| 修复速度 | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| 精准控制 | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 审计可追溯 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 一致性保障 | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| 执行风险 | 中（可能覆盖无关内容） | 低 | 低 |

**最终选择**：方案 C — 混合模式

**理由**：
1. SKILL.md 和 8 个缺失 ref 文件：直接 sync installed → source（文件级复制零风险）
2. 6 个旧 ref 文件：用 `diff` 识别 delegate_task 相关行 → 定向 patch（不覆盖无关段）
3. orchestrator.py 的 D9 增强：独立实现（不与 installed 版本冲突）
4. Profile API Key（D10）：独立配置层面的工作，不依赖文件 sync

---

## 三、架构设计

### 整体架构

```
                          ┌─────────────────────────┐
                          │    install.sh           │
                          │                        │
                          │  cp -r skills/sdd/      │
                          │    → ~/.hermes/skills/  │
                          └─────────┬───────────────┘
                                    │
              ┌─────────────────────▼──────────────────────┐
              │          SOURCE REPO (hermes-harness)      │
              │                                            │
              │  skills/sdd/sdd-orchestrator/              │
              │  ├── SKILL.md           (v2.6.0 ← sync)   │
              │  ├── scripts/                              │
              │  │   └── orchestrator.py (D9 增强)         │
              │  └── references/                           │
              │      ├── kanban-profile-integration.md  ←  │
              │      ├── profile-soul-architecture.md   ←  │
              │      ├── ... 6 more ref files           ←  │
              │      └── delegate-protocol.md   (D8 迁移)  │
              └────────────────────────────────────────────┘
                                    │
              ┌─────────────────────▼──────┐
              │    AGENTS.md (纯配置)       │
              │    • version: 2.6.0         │
              │    • role_to_profile 映射   │
              │    • 无文档内容             │
              └────────────────────────────┘
```

### 上下文传播设计（D9）

```
┌─ orchestrator.delegate_agent() ──────────────────────────┐
│                                                           │
│  def build_task_body(change_id, state):                   │
│      body = {                                             │
│          "change_id": change_id,                          │
│          "stage": stage_name,                             │
│          "context": {                                     │
│              "前置摘要": self._get_prev_summary(),         │
│              "关键决策": self._get_adrs(),                 │
│              "约束条件": self._get_constraints(),          │
│              "前置产物路径": self._get_prereq_paths()      │
│          }                                                │
│      }                                                    │
│      return body                                           │
│                                                           │
│  _get_prev_summary():                                      │
│    - PO→BA: prd.md 核心假设摘要（≤200字）                  │
│    - BA→Architect: spec.md AC 列表摘要                    │
│    - Architect→Coder: design.md 方案选择理由              │
│                                                           │
│  context 注入 --body                                      │
└───────────────────────────────────────────────────────────┘
```

### 关键决策

| 决策 | 选项 | 选择 | 理由 |
|------|------|:---:|------|
| SKILL.md 升级方式 | 全量替换 / 增量 patch / 混合 | **混合（方案C）** | 兼顾速度与精度 |
| AGENTS.md 去文档化 | 手动提取章节 / 工具分割 | **手动提取** | 每章节需要判断归属，工具无法做语义分割 |
| D9 上下文注入 | --body 全量 / 文件引用 | **--body 摘要 + 文件引用** | body 有 token 限制，完整内容留文件引用 |
| Profile API Key | 删除 api_key 字段 / 替换有效 key | **删除 api_key 字段** | 继承主配置最干净，不绑定特定 Provider |
| 旧 ref 文件迁移标记 | 修改内容 / 添加历史存档标记 | **添加 `⚠️ 已迁移` 头部 + 保留旧内容** | 保持向后参考价值 |

---

## 四、详细设计

### 模块 1：SKILL.md 与 References 同步（D5-D8）

**职责**：将 installed v2.6.0 同步回源码 repo，确保 install.sh 安装后得到正确版本

**步骤**：
1. `cp ~/.hermes/skills/sdd/sdd-orchestrator/SKILL.md {repo}/skills/sdd/sdd-orchestrator/SKILL.md`
2. `cp ~/.hermes/skills/sdd/sdd-orchestrator/references/kanban-profile-integration.md {repo}/.../references/`
3. `cp` 其余 7 个缺失 ref 文件
4. 对 6 个旧 ref 文件：`diff` installed vs source → patch 仅 delegate_task 相关行
5. 在 `delegate-protocol.md` 头部添加 `⚠️ 已迁移` 标记
6. 同步版本号到 frontmatter

**验证**：`grep -c "delegate_task" {repo}/SKILL.md` 结果 0

---

### 模块 2：AGENTS.md 重构（D2-D3）

**职责**：AGENTS.md 从 174 行精简到 ≤60 行纯配置

**结构**：
```markdown
# AGENTS.md — Hermes SDD 项目配置

## 项目信息
- name: "Hermes SDD"
- repo: "https://github.com/NEU-JING/hermes-harness"
- version: "2.6.0"

## 技术栈
...

## 路径约定
...

## SDD 配置
- flow_engine: "sdd/sdd-orchestrator"
- default_flow_level: "Standard"

## 项目约束
- constitution: "CONSTITUTION.md"
- quirks: "QUIRKS.md"

## SDD Profile 映射
sdd_config:
  role_to_profile:
    po: "sdd-po"
    ba: "sdd-ba"
    architect: "sdd-architect"
    coder: "sdd-coder"
    reviewer: "sdd-reviewer"
    qa: "sdd-qa"
  profile_enabled: true
```

**移除的内容** → 移至 `docs/current/architecture.md`：
- Profile 架构概述（ASCII 图 + 原理说明）
- Soul 模式配置（示例 + 启用/禁用）
- Workspace 配置规范（类型对比 + 最佳实践）
- Profile 能力矩阵

---

### 模块 3：QUIRKS.md 创建（D1）

**职责**：从 `templates/QUIRKS.md` 复制到项目根目录

```bash
cp templates/QUIRKS.md QUIRKS.md
```

**内容**：包含 SDD 框架的特殊约定（如 Kanban worker 行为约束、PowerUser 模式说明）

---

### 模块 4：上下文传播增强（D9）

**职责**：增强 orchestrator.py 的 `delegate_agent()` 方法，使 task body 包含跨阶段上下文

**实现**：

```python
def _build_context_for_stage(self, change_id, state):
    """构建跨阶段上下文"""
    change_dir = self.changes_dir / change_id
    context = {}
    
    # 前置摘要：根据当前阶段读取前置产物
    if state == State.BA_ENTRY:
        prd_path = change_dir / "prd.md"
        if prd_path.exists():
            # 提取 PRD 前 30 行作为摘要
            context["前置摘要"] = prd_path.read_text()[:1000]
    elif state == State.ARCHITECT_ENTRY:
        spec_path = change_dir / "spec.md"
        if spec_path.exists():
            # 提取 AC 列表摘要
            acs = re.findall(r'#### Scenario AC\d+:', spec_path.read_text())
            context["前置摘要"] = f"Spec 包含 {len(acs)} 条 AC: {', '.join(acs)}"
    elif state == State.CODER_ENTRY:
        design_path = change_dir / "design.md"
        if design_path.exists():
            # 提取最终方案选择
            match = re.search(r'\*\*最终选择\*\*：(.+)', design_path.read_text())
            context["前置摘要"] = match.group(1) if match else "方案选择（见 design.md）"
    
    # 关键决策：读取 AC 约束
    context["约束条件"] = "SDD 框架一致性修复，所有修改不破坏现有功能"
    
    return context
```

**body 格式**：
```markdown
## 前置上下文
- 变更 ID: {change_id}
- 阶段: {stage}
- 前置摘要: {_build_context_for_stage()}
- 产物路径: {change_dir}
```

---

### 模块 5：Profile API Key 修复（D10）

**职责**：清理 6 个 Profile config.yaml 中的过期 DeepSeek API Key，改为继承主配置

```bash
for p in sdd-po sdd-ba sdd-architect sdd-coder sdd-reviewer sdd-qa; do
  config=~/.hermes/profiles/$p/config.yaml
  # 移除 api_key 字段（继承主配置）
  # 移除 delegation 字段（冗余）
done
```

**修复后配置示例**：
```yaml
model:
  default: deepseek-v4-flash
  provider: deepseek
  base_url: https://api.deepseek.com/v1
# api_key: 已移除 → 继承主配置
```

> 注意：sdd-reviewer 保持 `deepseek-v4-pro` 作为 default 模型，但 api_key 同样继承主配置

---

## 五、配置与约定

### 路径约定

| 路径 | 用途 |
|------|------|
| `project-root/QUIRKS.md` | SDD 框架特殊约定（新创建） |
| `project-root/AGENTS.md` | 纯配置文件（精简后） |
| `project-root/docs/current/architecture.md` | 架构文档（补充 Profile+Soul 章节） |
| `project-root/skills/sdd/sdd-orchestrator/SKILL.md` | 升级后的 v2.6.0 版本 |
| `project-root/skills/sdd/sdd-orchestrator/references/*.md` | 参考文件（同步更新） |
| `project-root/skills/sdd/sdd-orchestrator/scripts/orchestrator.py` | D9 增强 |
| `~/.hermes/profiles/sdd-*/config.yaml` | Profile 配置（无硬编码 API Key） |

### 禁止操作

- ❌ 不修改 Hermes 源码（`/usr/local/lib/hermes-agent/`）
- ❌ 不修改其他角色 Agent 的 SKILL.md 内容（只改 sdd-orchestrator）
- ❌ 不创建新的 directory structure（只在现有目录内操作）

---

## 六、Tasks 拆分

| # | Task | 估时 | 依赖 | AC 覆盖 | 说明 |
|---|------|:---:|------|:---:|------|
| T1 | 创建 QUIRKS.md | 2m | 无 | AC1 | 从 templates/ 复制 |
| T2 | 精简 AGENTS.md | 10m | T1 | AC2-AC6 | 移除文档内容，更新版本/注释 |
| T3 | 补充 docs/current/architecture.md | 5m | T2 | AC6 | 移入 PG 的文档章节 |
| T4 | Sync SKILL.md 与 8 个 ref 文件 | 5m | 无 | AC7-AC10 | installed → source |
| T5 | 迁移 6 个旧 ref 文件 | 15m | T4 | AC11-AC12 | patch delegate_task→Kanban |
| T6 | 增强 orchestrator.py 上下文 | 10m | 无 | AC13-AC15 | D9 上下文传播 |
| T7 | 修复 Profile API Key 配置 | 5m | 无 | AC16-AC17 | 6 个 profile 清理 |
| T8 | 归档补全与 cleanup | 5m | T2,T4 | D4 | manifest + deprecated 清理 |

**总估时**：57m

---

## 七、实现顺序

```
T1 → T2 → T3 → T4 → T5 → T6 → T7 → T8
│         │         │         │
└─ D1-D3  └─ D5-D8  └─ D9     └─ D4+D10
```
