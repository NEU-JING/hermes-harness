# Tasks — 007: SDD Orchestrator v2.1.0 Profile 委托集成

> **变更 ID**: `007-profile-delegation`
> **版本**: v1.0
> **创建时间**: 2026-05-31
> **前置文档**: [prd.md](./prd.md) | [spec.md](./spec.md) | [design.md](./design.md)

---

## Task 概览

| Task | 文件 | 操作 | 预计耗时 |
|:----:|------|:----:|:--------:|
| T1 | `skills/sdd/shared/sdd-rules.md` | 修改 | 3 min |
| T2 | `AGENTS.md` | 修改 | 3 min |
| T3 | `skills/sdd/sdd-orchestrator/SKILL.md` | 修改 | 5 min |
| T4 | `skills/sdd/sdd-orchestrator/references/delegate-protocol.md` | 修改 | 5 min |
| T5 | `skills/sdd/sdd-orchestrator/scripts/orchestrator.py` | 修改 | 5 min |
| T6 | `skills/sdd/sdd-orchestrator/scripts/orchestrator.py` | 修改 | 4 min |
| T7 | `skills/sdd/sdd-init/SKILL.md` | 修改 | 4 min |
| T8 | `scripts/setup-sdd-profiles.sh` | **新建** | 5 min |
| T9 | `skills/sdd/shared/sdd-state-schema.md` | 修改 | 3 min |
| T10 | 集成验证 | 验证 | 5 min |

**总计**：约 42 分钟，10 个 Task

---

## T1: sdd-rules.md — 新增 ROLE_TO_PROFILE_DEFAULT 默认映射常量

**文件**：`skills/sdd/shared/sdd-rules.md`

**操作**：在文件末尾（`## 规则总览` 表格之后）追加 `ROLE_TO_PROFILE_DEFAULT` 常量定义。

**修改内容**：追加以下内容到文件末尾：

```markdown

---

## ROLE_TO_PROFILE_DEFAULT（编排器 v2.1.0+）

SDD 角色到 Hermes Profile 的默认映射。编排器在委托阶段根据此映射选择 Profile。
项目可通过 AGENTS.md 的 `sdd_config.role_to_profile` 覆盖指定角色的映射。

| 角色 | 默认 Profile | 说明 |
|:-----|:------------|:-----|
| `po` | `sdd-flash` | PRD 文档产出，快模型即可 |
| `ba` | `sdd-flash` | Spec 文档产出，快模型即可 |
| `architect` | `sdd-pro` | 技术设计，需高质量模型 |
| `coder` | `sdd-pro` | 编码实现，需高质量模型 |
| `reviewer` | `sdd-reviewer` | 独立评审，需高质量模型 + 独立会话 |
| `qa` | `sdd-flash` | 测试验证，快模型即可 |
```

**验证**：
```bash
# 确认 ROLE_TO_PROFILE_DEFAULT 章节存在
grep -c "ROLE_TO_PROFILE_DEFAULT" skills/sdd/shared/sdd-rules.md
# 预期输出: ≥ 2（标题行 + 映射表内引用）

# 确认 6 个角色都有映射
grep -cE "^\| \`(po|ba|architect|coder|reviewer|qa)\`" skills/sdd/shared/sdd-rules.md
# 预期输出: 6
```

---

## T2: AGENTS.md — 新增 sdd_config.role_to_profile 可选覆盖段

**文件**：`AGENTS.md`（项目根目录）

**操作**：在 `## 自定义覆盖` 段之后追加 `## SDD Profile 覆盖（可选）` 段。

**修改内容**：在文件末尾追加：

```markdown

## SDD Profile 覆盖（可选）

# Hermes v2.1.0+ 支持基于 Profile 的多 Agent 委托。
# 不声明此段 = 使用 skills/sdd/shared/sdd-rules.md 中的默认映射。
# 声明后只覆盖指定角色，未覆盖角色继续使用默认值。
# 示例：
# sdd_config:
#   role_to_profile:
#     po: "sdd-pro"        # 将 PO 升级为 pro 模型
#     coder: "sdd-flash"   # 将 Coder 降级为 flash（不推荐）
```

> **注意**：此段为带注释的配置模板，实际映射行（如 `po: "sdd-pro"`）由用户按需取消注释。初始状态下所有映射行均为注释，等效于使用默认映射。

**验证**：
```bash
# 确认新增段存在
grep -A 10 "SDD Profile 覆盖" AGENTS.md | grep -c "sdd_config"
# 预期输出: ≥ 1

# 确认文件行数 ≤ 45（原 32 行 + 新增约 10 行）
wc -l AGENTS.md
# 预期输出: 35-45
```

---

## T3: orchestrator SKILL.md — 版本号升级 & Delegation 章节更新

**文件**：`skills/sdd/sdd-orchestrator/SKILL.md`

**操作**：

### T3.1: 更新版本号

- YAML frontmatter 中 `version: 2.0.3` → `version: 2.1.0`
- 标题 `# SDD Orchestrator v2.0.3` → `# SDD Orchestrator v2.1.0`

### T3.2: 更新 "Hermes v2.1.0 Profile 集成" 章节

当前该章节标题为 `### Hermes v2.1.0 Profile 集成（变更 007 进行中）`，表格使用 6 角色设计（sdd-po/sdd-ba/...）。

**替换整个章节**为 3-Profile 正式规范。需要替换从 `### Hermes v2.1.0 Profile 集成` 到下一个 `###` 标题之间的全部内容：

```markdown
### Hermes v2.1.0 Profile 委托集成

编排器 v2.1.0 利用 Hermes Profile 隔离能力实现角色分组的模型分级委托。3 个 Profile 覆盖 6 个 SDD 角色：

#### Profile 总览

| Profile | 适用角色 | 模型 | 工具集 |
|:--------|:---------|:-----|:-------|
| `sdd-flash` | PO, BA, QA | `deepseek/deepseek-v4-flash` | `file`, `skills` |
| `sdd-pro` | Architect, Coder | `deepseek/deepseek-v4-pro` | `file`, `terminal`, `skills`, `github` |
| `sdd-reviewer` | Reviewer | `deepseek/deepseek-v4-pro` | `file`, `terminal`, `skills`, `github` |

#### Role → Profile 默认映射

定义在 `skills/sdd/shared/sdd-rules.md` 的 `ROLE_TO_PROFILE_DEFAULT` 常量中：

| 角色 | Profile |
|:-----|:--------|
| `po` | `sdd-flash` |
| `ba` | `sdd-flash` |
| `architect` | `sdd-pro` |
| `coder` | `sdd-pro` |
| `reviewer` | `sdd-reviewer` |
| `qa` | `sdd-flash` |

#### 委托流程

编排器在 `delegate_agent()` 前调用 `get_profile_for_role(role)` 解析 Profile：

1. 从 `shared/sdd-rules.md` 加载 `ROLE_TO_PROFILE_DEFAULT`
2. 检查 `AGENTS.md` 是否有 `sdd_config.role_to_profile` 覆盖
3. 浅合并覆盖到默认映射
4. 查找 role → profile 映射
5. 验证 Profile 存在（`hermes profile list`）
6. 将 profile 名称传入 `delegate_task`

#### Profile 创建

```bash
# 一键创建 3 个 Profile
bash scripts/setup-sdd-profiles.sh
```

#### 向后兼容

AGENTS.md 无 `role_to_profile` 配置时，`delegate_task` 不携带 `profile` 参数，行为与 v2.0.3 完全一致。
```

### T3.3: 更新 Agent 委托章节

在 "Agent Delegation（Agent委托）" 章节的委托格式中，新增 `profile` 字段说明。找到基础委托格式的 YAML 块，在 `goal` 行后、`context` 行前插入：

```yaml
  profile: "sdd-flash"       # 新增 v2.1.0: 可选的 Hermes Profile 名称
```

**验证**：
```bash
# 确认版本号
head -5 skills/sdd/sdd-orchestrator/SKILL.md | grep "version: 2.1.0"
head -10 skills/sdd/sdd-orchestrator/SKILL.md | grep "v2.1.0"
# 预期：两个 grep 都有输出

# 确认不再出现 "变更 007 进行中"
grep "变更 007 进行中" skills/sdd/sdd-orchestrator/SKILL.md
# 预期：无输出（该行已替换）

# 确认 Profile 总览表格使用 sdd-flash/sdd-pro/sdd-reviewer
grep "sdd-flash" skills/sdd/sdd-orchestrator/SKILL.md | head -1
grep "sdd-pro" skills/sdd/sdd-orchestrator/SKILL.md | head -1
grep "sdd-reviewer" skills/sdd/sdd-orchestrator/SKILL.md | head -1
# 预期：三个 grep 都有输出
```

---

## T4: delegate-protocol.md — 委托格式新增 profile 字段 & "Planned" → 正式规范

**文件**：`skills/sdd/sdd-orchestrator/references/delegate-protocol.md`

**操作**：

### T4.1: 更新版本号

- 版本号 `2.0.2` → `2.1.0`
- 日期更新为 `2026-05-31`
- 更新说明中新增：`- 新增 profile 可选字段，支持 Profile 委托`

### T4.2: 委托格式中新增 profile 字段

在 `### 基础委托格式` 的 YAML 块中，`goal` 后插入：

```yaml
  profile: "sdd-flash"        # v2.1.0 NEW: 可选 Profile 名称
```

### T4.3: 各阶段委托格式中添加 profile 字段

为 PO、BA、Architect、Coder、Reviewer、QA 六个阶段的委托格式 YAML 块，各在 `goal` 后插入 `profile` 行：

| 阶段 | profile 值 |
|:-----|:-----------|
| PO | `"sdd-flash"` |
| BA | `"sdd-flash"` |
| Architect | `"sdd-pro"` |
| Coder | `"sdd-pro"` |
| Reviewer | `"sdd-reviewer"` |
| QA | `"sdd-flash"` |

### T4.4: 替换 "Hermes v2.1 扩展" 章节（状态从 Planned → 正式）

将章节头部的 `**状态**: Planned（变更 007-profile-delegation 进行中）` 改为 `**状态**: 正式（v2.1.0）`。

将 6 Profile 设计表（sdd-po/sdd-ba/sdd-architect/sdd-coder/sdd-reviewer/sdd-qa）替换为 3 Profile 设计表：

```markdown
### 3 Profile 角色分组

| Profile | 适用角色 | 模型 | 预加载 Skills | 工具集 |
|:--------|:---------|:-----|:-------------|:-------|
| `sdd-flash` | PO, BA, QA | `deepseek/deepseek-v4-flash` | po-agent, ba-agent, qa-agent, sdd-orchestrator | file, skills |
| `sdd-pro` | Architect, Coder | `deepseek/deepseek-v4-pro` | architect-agent, coder-agent, sdd-orchestrator, test-driven-development, local-verifier | file, terminal, skills, github |
| `sdd-reviewer` | Reviewer | `deepseek/deepseek-v4-pro`（独立会话） | reviewer-agent, sdd-orchestrator, post-coding-review | file, terminal, skills, github |
```

### T4.5: 更新 Profile 创建命令

将 6 角色创建命令块替换为：

```bash
# 一键创建 3 个 Profile
bash scripts/setup-sdd-profiles.sh

# 或手动创建：
hermes profile create sdd-flash --model deepseek/deepseek-v4-flash --tools file,skills
hermes profile create sdd-pro --model deepseek/deepseek-v4-pro --tools file,terminal,skills,github
hermes profile create sdd-reviewer --model deepseek/deepseek-v4-pro --tools file,terminal,skills,github
```

**验证**：
```bash
# 确认版本号
head -5 skills/sdd/sdd-orchestrator/references/delegate-protocol.md | grep "2.1.0"
# 预期：有输出

# 确认不再有 "sdd-po" 或 "sdd-ba" 的旧 Profile 名
grep -c "sdd-po\|sdd-ba\|sdd-architect\|sdd-coder\|sdd-qa" skills/sdd/sdd-orchestrator/references/delegate-protocol.md
# 预期: 0（旧 6 Profile 引用已清除）

# 确认不再出现 "Planned" 状态标记（该章节）
grep "Planned" skills/sdd/sdd-orchestrator/references/delegate-protocol.md
# 预期: 0

# 确认 profile 字段出现在格式定义中
grep -c "profile:" skills/sdd/sdd-orchestrator/references/delegate-protocol.md
# 预期: ≥ 7（基础格式 + 6 个阶段）
```

---

## T5: orchestrator.py — 新增 Profile 解析方法

**文件**：`skills/sdd/sdd-orchestrator/scripts/orchestrator.py`

**操作**：在 `SDDOrchestrator` 类中新增以下 3 个方法。

### T5.1: 新增 `get_role_from_state()` 静态方法

在 `STATE_AGENT_MAP` 之后（约第 82 行）插入：

```python
# Role 映射（用于 Profile 选择）
STATE_ROLE_MAP = {
    State.PO_ENTRY: "po",
    State.BA_ENTRY: "ba",
    State.ARCHITECT_ENTRY: "architect",
    State.CODER_ENTRY: "coder",
    State.REVIEWER_ENTRY: "reviewer",
    State.QA_ENTRY: "qa",
}
```

### T5.2: 新增 `load_profile_mapping()` 方法

在 `SDDOrchestrator` 类中（约在 `determine_flow_level()` 之后）新增：

```python
    # Profile 默认映射（来自 shared/sdd-rules.md）
    ROLE_TO_PROFILE_DEFAULT = {
        "po": "sdd-flash",
        "ba": "sdd-flash",
        "architect": "sdd-pro",
        "coder": "sdd-pro",
        "reviewer": "sdd-reviewer",
        "qa": "sdd-flash",
    }

    def load_profile_mapping(self) -> Dict[str, str]:
        """加载合并后的 role→profile 映射（默认 + AGENTS.md 覆盖）。

        Returns:
            Dict[str, str]: 合并后的 role→profile 映射
        """
        mapping = dict(self.ROLE_TO_PROFILE_DEFAULT)

        # 尝试从 AGENTS.md 加载覆盖
        agents_path = self.project_root / "AGENTS.md"
        if agents_path.exists():
            try:
                import re
                content = agents_path.read_text()
                # 简单解析 sdd_config.role_to_profile 段
                # 格式: po: "sdd-flash"
                in_section = False
                for line in content.split("\n"):
                    if "role_to_profile:" in line:
                        in_section = True
                        continue
                    if in_section:
                        if line.strip() == "" or line.startswith("#"):
                            if line.strip() == "":
                                in_section = False
                            continue
                        match = re.match(r'\s*(\w+):\s*"([^"]+)"', line)
                        if match:
                            role, profile = match.groups()
                            mapping[role] = profile
                        else:
                            in_section = False
            except Exception as e:
                print(f"⚠️  解析 AGENTS.md 失败: {e}，使用默认映射")

        return mapping

    def get_profile_for_role(self, role: str) -> Optional[str]:
        """根据角色返回 Profile 名称。

        Args:
            role: 角色标识 (po/ba/architect/coder/reviewer/qa)

        Returns:
            Profile 名称，或 None（回退模式）
        """
        mapping = self.load_profile_mapping()
        profile = mapping.get(role)

        if not profile:
            print(f"⚠️  角色 '{role}' 未在映射中找到，回退到无 Profile 模式")
            return None

        if not self._check_profile_exists(profile):
            print(f"⚠️  Profile '{profile}' 不存在。运行 'bash scripts/setup-sdd-profiles.sh' 创建。")
            return None

        return profile

    def _check_profile_exists(self, profile_name: str) -> bool:
        """检查 Hermes Profile 是否存在。

        Args:
            profile_name: Profile 名称

        Returns:
            True 如果 Profile 存在
        """
        import subprocess
        try:
            result = subprocess.run(
                ["hermes", "profile", "list"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return profile_name in result.stdout
        except Exception:
            # hermes 命令不可用，假设 Profile 不存在
            return False
```

### T5.3: 更新 `VERSION` 常量

```python
VERSION = "2.1.0"
```

### T5.4: 更新文件头部注释

```python
"""
SDD Orchestrator v2.1 - 严格状态机编排器
...
"""
```

**验证**：
```bash
# 确认新增方法存在
grep -c "def load_profile_mapping" skills/sdd/sdd-orchestrator/scripts/orchestrator.py
grep -c "def get_profile_for_role" skills/sdd/sdd-orchestrator/scripts/orchestrator.py
grep -c "def _check_profile_exists" skills/sdd/sdd-orchestrator/scripts/orchestrator.py
# 预期：每个都是 1

# 确认 STATE_ROLE_MAP 有 6 个条目
grep -cE '"(po|ba|architect|coder|reviewer|qa)"' skills/sdd/sdd-orchestrator/scripts/orchestrator.py
# 预期: ≥ 6

# 确认版本号
grep 'VERSION = "2.1.0"' skills/sdd/sdd-orchestrator/scripts/orchestrator.py
# 预期：有输出

# 语法检查
python3 -c "import ast; ast.parse(open('skills/sdd/sdd-orchestrator/scripts/orchestrator.py').read()); print('OK')"
# 预期：OK
```

---

## T6: orchestrator.py — 修改 delegate_agent() 支持 Profile 参数

**文件**：`skills/sdd/sdd-orchestrator/scripts/orchestrator.py`

**操作**：修改 `delegate_agent()` 方法，在委托前解析 Profile。

在现有 `delegate_agent()` 方法体的开头（`agent_skill = STATE_AGENT_MAP.get(state)` 之后、`print(f"\n📤 委托 ...")` 之前）插入 Profile 解析逻辑：

```python
    def delegate_agent(self, change_id: str, state: State):
        """委托Agent执行任务（v2.1.0: 支持 Profile 感知委托）"""
        agent_skill = STATE_AGENT_MAP.get(state)
        if not agent_skill:
            return

        # v2.1.0: Profile 解析
        role = STATE_ROLE_MAP.get(state)
        profile = self.get_profile_for_role(role) if role else None

        if profile:
            print(f"\n🔷 委托 {agent_skill} → Profile: {profile}")
        else:
            print(f"\n📤 委托 {agent_skill}（无 Profile，使用默认模式）")

        # ... 保持现有逻辑 ...
```

在委托详情输出块中（`print(f"""...委托详情...""")`），新增 `Profile` 字段行：

```python
        print(f"""
━━━━━━━━━━━━━━━━━━━━
委托详情:
  Skill: {agent_skill}
  Profile: {profile or 'default'}   # NEW
  Goal: 产出{state.state_name.replace('_ENTRY', '').replace('_', ' ')}阶段产物
  Context:
{json.dumps(context, indent=4)}
━━━━━━━━━━━━━━━━━━━━

注: 实际应调用 delegate_task(skill='{agent_skill}', profile='{profile or ""}', context=...)
此处仅演示状态机推进逻辑。
""")
```

**验证**：
```bash
# 确认 Profile 解析逻辑在 delegate_agent 中
grep -A 5 "def delegate_agent" skills/sdd/sdd-orchestrator/scripts/orchestrator.py | grep "get_profile_for_role"
# 预期：有输出

# 语法检查
python3 -c "import ast; ast.parse(open('skills/sdd/sdd-orchestrator/scripts/orchestrator.py').read()); print('OK')"
# 预期：OK
```

---

## T7: sdd-init SKILL.md — 升级模式新增 Profile 检测与创建步骤

**文件**：`skills/sdd/sdd-init/SKILL.md`

**操作**：

### T7.1: 在 Step B1（检测现有状态）中新增 Profile 检测项

在检测列表末尾（第 10 项之后）追加：

```bash
# 11: Hermes Profile
hermes profile list 2>/dev/null | grep -c "sdd-" && echo "✓" || echo "📁 需创建"
```

### T7.2: 在 Step B2（生成升级计划）的升级计划表格中新增行

```markdown
| Hermes Profiles | $(检测结果) | $(操作) |
```

### T7.3: 在 Step B4（执行升级）末尾新增 Step B4.x

```markdown
### Step B4.x: 创建 SDD Profiles（Hermes v2.1.0+）

**前置条件**：`hermes --version` ≥ 2.1.0

1. 检测 Hermes 版本：
   ```bash
   hermes --version 2>/dev/null | grep -oP 'v?\K\d+\.\d+'
   ```

2. 版本 ≥ 2.1.0 时执行 Profile 创建脚本：
   ```bash
   bash scripts/setup-sdd-profiles.sh
   ```

3. 验证创建结果：
   ```bash
   hermes profile list | grep "sdd-"
   # 预期：sdd-flash, sdd-pro, sdd-reviewer 三个 Profile
   ```

**降级处理**：
- `hermes` 命令不可用 → 输出 "❌ hermes 未安装，跳过 Profile 创建"
- 版本 < 2.1.0 → 输出 "⚠️  Hermes 版本过低，请升级到 v2.1.0+ 以启用 Profile 委托"
- Profile 已存在 → 输出 "⏭️  Profile '{name}' 已存在，跳过"
```

**验证**：
```bash
# 确认 Step B4.x 存在
grep "Step B4.x" skills/sdd/sdd-init/SKILL.md
# 预期：有输出

# 确认 setup-sdd-profiles.sh 引用
grep "setup-sdd-profiles.sh" skills/sdd/sdd-init/SKILL.md
# 预期：有输出
```

---

## T8: setup-sdd-profiles.sh — 新建一键 Profile 创建脚本

**文件**：`scripts/setup-sdd-profiles.sh`（**新建**）

**操作**：创建可执行 Shell 脚本，幂等创建 3 个 SDD Profile。

```bash
#!/bin/bash
# setup-sdd-profiles.sh — 创建 SDD v2.1.0 所需的 3 个 Hermes Profile
# 用法: bash scripts/setup-sdd-profiles.sh
# 幂等：已存在的 Profile 跳过创建
# 需要 Hermes v2.1.0+

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "=== SDD Profile Setup (v2.1.0) ==="
echo ""

# 检查 hermes 命令
if ! command -v hermes &> /dev/null; then
    echo -e "${RED}❌ hermes 命令不可用${NC}"
    echo "   请安装 Hermes v2.1.0+: https://hermes-agent.nousresearch.com/docs"
    exit 1
fi

HERMES_VERSION=$(hermes --version 2>/dev/null | grep -oP 'v?\K\d+\.\d+' | head -1 || echo "0.0")
echo "📋 Hermes 版本: ${HERMES_VERSION}"

create_profile() {
    local name=$1
    local model=$2
    local tools=$3

    if hermes profile list 2>/dev/null | grep -q "$name"; then
        echo -e "   ${YELLOW}⏭️${NC}  Profile '${name}' 已存在，跳过"
        return 0
    fi

    echo -e "   ${GREEN}📁${NC} 创建 Profile: ${name}"
    if hermes profile create "$name" --model "$model" --tools "$tools" 2>/dev/null; then
        echo -e "   ${GREEN}✅${NC} Profile '${name}' 创建成功"
    else
        echo -e "   ${RED}❌${NC} Profile '${name}' 创建失败"
        return 1
    fi
}

echo ""
echo "创建 SDD Profiles..."
echo ""

# sdd-flash: 文档密集型 (PO/BA/QA)
create_profile "sdd-flash" \
    "deepseek/deepseek-v4-flash" \
    "file,skills" || true

# sdd-pro: 编码密集型 (Architect/Coder)
create_profile "sdd-pro" \
    "deepseek/deepseek-v4-pro" \
    "file,terminal,skills,github" || true

# sdd-reviewer: 独立评审 (Reviewer)
create_profile "sdd-reviewer" \
    "deepseek/deepseek-v4-pro" \
    "file,terminal,skills,github" || true

echo ""
echo "=== Profile 创建摘要 ==="
hermes profile list 2>/dev/null | grep "sdd-" || echo "(无 sdd- Profile)"
echo ""
echo "✅ SDD Profile 设置完成"
echo ""
echo "下一步：在 AGENTS.md 中配置 sdd_config.role_to_profile 以启用 Profile 委托"
```

**创建命令**：
```bash
mkdir -p scripts
# 用 write_file 写入上述内容到 scripts/setup-sdd-profiles.sh
chmod +x scripts/setup-sdd-profiles.sh
```

**验证**：
```bash
# 确认文件存在且可执行
test -x scripts/setup-sdd-profiles.sh && echo "OK" || echo "FAIL"
# 预期：OK

# 确认 3 个 Profile 名称都在脚本中
grep -c "sdd-flash\|sdd-pro\|sdd-reviewer" scripts/setup-sdd-profiles.sh
# 预期: ≥ 6（3 个定义 + 3 个 create_profile 调用）

# 语法检查
bash -n scripts/setup-sdd-profiles.sh && echo "OK" || echo "FAIL"
# 预期：OK
```

---

## T9: sdd-state-schema.md — Schema 新增 profile 字段

**文件**：`skills/sdd/shared/sdd-state-schema.md`

**操作**：在 `.sdd-state.json` 的 Schema 定义中新增 `profile` 和 `profile_history` 字段。

**修改内容**：在现有 Schema 的 `properties` 中（如 `metadata` 之后）追加：

```json
    "profile": {
      "type": "string",
      "description": "当前委托阶段使用的 Hermes Profile 名称。仅在启用 Profile 模式时存在。",
      "examples": ["sdd-flash", "sdd-pro", "sdd-reviewer"]
    },
    "profile_history": {
      "type": "array",
      "description": "各阶段使用的 Profile 历史记录",
      "items": {
        "type": "object",
        "properties": {
          "state": { "type": "string", "description": "阶段状态名" },
          "profile": { "type": "string", "description": "使用的 Profile 名称" },
          "resolved_at": { "type": "string", "format": "date-time", "description": "解析时间" }
        }
      }
    }
```

> 如果是 Markdown 格式的 Schema 文件（非 JSON），则在对应的数据结构描述章节中新增上述字段的文档描述。

**验证**：
```bash
# 确认 profile 字段在 schema 中
grep -c '"profile"' skills/sdd/shared/sdd-state-schema.md
# 预期: ≥ 2（字段定义 + profile_history 内引用）

# 确认 profile_history 字段在 schema 中
grep -c "profile_history" skills/sdd/shared/sdd-state-schema.md
# 预期: ≥ 1
```

---

## T10: 集成验证 — 全流程 Profile 解析验证

**操作**：执行一系列验证命令，确认所有修改的正确性和一致性。

### T10.1: 文件一致性检查

```bash
cd /root/workspace/hermes-harness

echo "=== T10.1: 文件一致性检查 ==="

# 1. sdd-rules.md 包含 6 个角色的映射
echo "--- sdd-rules.md 角色映射 ---"
grep -cE "^\| \`(po|ba|architect|coder|reviewer|qa)\`" skills/sdd/shared/sdd-rules.md
# 预期: 6

# 2. delegate-protocol.md 不再有旧 6-Profile 名称
echo "--- delegate-protocol.md 旧名称检查 ---"
OLD_COUNT=$(grep -c "sdd-po\|sdd-ba\|sdd-architect\|sdd-coder\|sdd-qa" skills/sdd/sdd-orchestrator/references/delegate-protocol.md 2>/dev/null || echo "0")
echo "旧 Profile 引用数: $OLD_COUNT (预期 0)"

# 3. orchestrator SKILL.md 版本号
echo "--- orchestrator SKILL.md 版本号 ---"
grep "version: 2.1.0" skills/sdd/sdd-orchestrator/SKILL.md
grep "v2.1.0" skills/sdd/sdd-orchestrator/SKILL.md | head -1

# 4. orchestrator.py 语法
echo "--- orchestrator.py 语法 ---"
python3 -c "import ast; ast.parse(open('skills/sdd/sdd-orchestrator/scripts/orchestrator.py').read()); print('✅ 语法正确')"

# 5. setup script 语法
echo "--- setup-sdd-profiles.sh 语法 ---"
bash -n scripts/setup-sdd-profiles.sh && echo "✅ 语法正确"

echo ""
echo "=== 集成验证完成 ==="
```

### T10.2: Profile 映射正确性验证

```bash
echo "=== T10.2: Profile 映射正确性验证 ==="

# 验证 orchestrator.py 中 ROLE_TO_PROFILE_DEFAULT 的映射
python3 << 'EOF'
import sys
sys.path.insert(0, "skills/sdd/sdd-orchestrator/scripts")
from orchestrator import SDDOrchestrator

orch = SDDOrchestrator()
mapping = orch.ROLE_TO_PROFILE_DEFAULT

# AC4-AC9: 覆盖全部 6 个角色
expected = {
    "po": "sdd-flash",        # AC4
    "ba": "sdd-flash",        # AC5
    "architect": "sdd-pro",   # AC6
    "coder": "sdd-pro",       # AC7
    "reviewer": "sdd-reviewer", # AC8
    "qa": "sdd-flash",        # AC9
}

all_ok = True
for role, profile in expected.items():
    actual = mapping.get(role)
    status = "✅" if actual == profile else "❌"
    if actual != profile:
        all_ok = False
    print(f"  {status} {role:12} → {actual}  (期望: {profile})")

print()
if all_ok:
    print("✅ AC4-AC9 全部通过：6 个角色 Profile 映射正确")
else:
    print("❌ 存在映射不匹配")
    sys.exit(1)
EOF
```

### T10.3: 向后兼容验证

```bash
echo "=== T10.3: 向后兼容验证 ==="

# 验证：AGENTS.md 无 role_to_profile 时 load_profile_mapping 返回默认映射
python3 << 'EOF'
import sys
sys.path.insert(0, "skills/sdd/sdd-orchestrator/scripts")
from orchestrator import SDDOrchestrator

orch = SDDOrchestrator(".")
mapping = orch.load_profile_mapping()

# 确认映射包含所有 6 个角色
assert len(mapping) >= 6, f"映射条目不足: {len(mapping)}"
assert mapping.get("po") == "sdd-flash"
assert mapping.get("coder") == "sdd-pro"
assert mapping.get("reviewer") == "sdd-reviewer"

print("✅ 向后兼容：默认映射包含全部 6 个角色")
print(f"   映射条目: {len(mapping)}")
EOF
```

**验证**：
```bash
# 运行全部集成验证
bash -x << 'SCRIPT'
cd /root/workspace/hermes-harness
echo "=== T10 集成验证 ==="

# 检查所有修改的文件存在
FILES=(
    "skills/sdd/shared/sdd-rules.md"
    "AGENTS.md"
    "skills/sdd/sdd-orchestrator/SKILL.md"
    "skills/sdd/sdd-orchestrator/references/delegate-protocol.md"
    "skills/sdd/sdd-orchestrator/scripts/orchestrator.py"
    "skills/sdd/sdd-init/SKILL.md"
    "scripts/setup-sdd-profiles.sh"
)

ALL_EXIST=true
for f in "${FILES[@]}"; do
    if [ -f "$f" ]; then
        echo "  ✅ $f"
    else
        echo "  ❌ $f 缺失"
        ALL_EXIST=false
    fi
done

if $ALL_EXIST; then
    echo ""
    echo "✅ 所有源文件就绪 (7/7)"
else
    echo ""
    echo "❌ 部分文件缺失"
    exit 1
fi
SCRIPT
# 预期：7/7 文件就绪
```

---

## 附录 A: 文件修改顺序依赖

```
T1 (sdd-rules.md) ──┐
                     ├──▶ T3 (orchestrator SKILL.md)
T2 (AGENTS.md) ──┬──┤
                 │  └──▶ T4 (delegate-protocol.md)
                 │         │
                 │         ├──▶ T5 (orchestrator.py - 新方法)
                 │         │      │
                 │         │      └──▶ T6 (orchestrator.py - delegate_agent)
                 │         │
                 │         └──▶ T7 (sdd-init SKILL.md)
                 │
                 └──▶ T9 (sdd-state-schema.md)

T8 (setup-sdd-profiles.sh) ── 独立，无依赖

T10 (集成验证) ── 最后执行，依赖 T1-T9
```

**建议执行顺序**：T1 → T2 → T8 → T3 → T4 → T5 → T6 → T7 → T9 → T10

---

## 附录 B: 验收标准覆盖矩阵

| AC | 描述 | 覆盖 Task |
|:--:|------|:---------:|
| AC1 | sdd-flash Profile 规格 | T4, T8 |
| AC2 | sdd-pro Profile 规格 | T4, T8 |
| AC3 | sdd-reviewer Profile 规格 | T4, T8 |
| AC4 | PO 委托使用 sdd-flash | T1, T5, T6 |
| AC5 | BA 委托使用 sdd-flash | T1, T5, T6 |
| AC6 | Architect 委托使用 sdd-pro | T1, T5, T6 |
| AC7 | Coder 委托使用 sdd-pro | T1, T5, T6 |
| AC8 | Reviewer 委托使用 sdd-reviewer | T1, T5, T6 |
| AC9 | QA 委托使用 sdd-flash | T1, T5, T6 |
| AC10 | 无配置保持向后兼容 | T5, T10 |
| AC11 | Profile 不存在回退警告 | T5, T6 |
| AC12 | AGENTS.md 覆盖生效 | T2, T5 |
| AC13 | 工具集最小化验证 | T4, T8 |
| AC14 | sdd-rules.md 默认映射 ≤ 20 行 | T1 |
| AC15 | orchestrator SKILL.md version: 2.1.0 | T3 |
