# Tasks — SDD 框架全量一致性修复（D1-D10）

> Architect Agent 产出，Coder Agent 执行。每 Task 2-15 分钟。

---

## 执行约定

1. **工作目录**：`/root/workspace/hermes-harness`
2. **每 Task 完成后**：commit，格式 `fix(consistency): T{N} {描述}`
3. **验证方式**：手动自检（检查文件存在 + grep delegate_task 数）
4. **分支约定**：所有变更提交到 feature 分支 `fix/001-consistency`，完成后 PR → main

---

## Task 执行顺序

```
T1 → T2 → T3 → T4 → T5 → T6 → T7 → T8
```

---

## T1: 创建 QUIRKS.md

**估时**：2m
**依赖**：无
**AC 覆盖**：AC1
**产出**：`/root/workspace/hermes-harness/QUIRKS.md`

### Steps

1. 从模板复制QUIRKS.md：
```bash
cp /root/workspace/hermes-harness/templates/QUIRKS.md /root/workspace/hermes-harness/QUIRKS.md
```

2. 验证：
```bash
test -f /root/workspace/hermes-harness/QUIRKS.md && echo "EXISTS" || echo "MISSING"
wc -l /root/workspace/hermes-harness/QUIRKS.md
```

3. Commit：
```bash
git add QUIRKS.md
git commit -m "fix(consistency): T1 创建 QUIRKS.md（D1）"
```

---

## T2: 精简 AGENTS.md

**估时**：10m
**依赖**：T1
**AC 覆盖**：AC2-AC6
**产出**：修改 `/root/workspace/hermes-harness/AGENTS.md`

### Steps

1. 重写 AGENTS.md 为纯配置格式（≤60行），结构：
   - 项目信息（name, description, repo, version: 2.6.0）
   - 技术栈
   - 路径约定
   - SDD 配置
   - 项目约束（constitution, quirks）
   - SDD Profile 映射（role_to_profile）

2. 移除以下文档章节（移至 T3）：
   - "SDD Profile 架构概述"（ASCII图 + 原理）
   - "Soul 模式配置"
   - "Workspace 配置规范"
   - "Profile 能力矩阵"

3. 更新 role_to_profile 注释，使用实际模型名（deepseek-v4-flash/pro）

4. 验证：
```bash
wc -l /root/workspace/hermes-harness/AGENTS.md
grep "version:" /root/workspace/hermes-harness/AGENTS.md
# 确认 ≤ 60 行
[ $(wc -l < /root/workspace/hermes-harness/AGENTS.md) -le 60 ] && echo "✅ ≤60行" || echo "❌ 超过60行"
```

5. Commit：
```bash
git add AGENTS.md
git commit -m "fix(consistency): T2 精简 AGENTS.md（D2-D3）"
```

---

## T3: 补充 docs/current/architecture.md

**估时**：5m
**依赖**：T2
**AC 覆盖**：AC6
**产出**：修改 `/root/workspace/hermes-harness/docs/current/architecture.md`

### Steps

1. 从当前 AGENTS.md 中提取被移除的文档章节，追加到 architecture.md：
   - Profile 架构概述（含 ASCII 图）
   - Soul 模式配置
   - Workspace 配置规范
   - Profile 能力矩阵

2. 在 architecture.md 中添加版本记录

3. 验证：
```bash
grep -c "Profile 架构" /root/workspace/hermes-harness/docs/current/architecture.md
grep -c "Soul 模式" /root/workspace/hermes-harness/docs/current/architecture.md
```

4. Commit：
```bash
git add docs/current/architecture.md
git commit -m "fix(consistency): T3 architecture.md 补充 Profile+Soul 章节（D3）"
```

---

## T4: Sync SKILL.md 与 8 个缺失 Reference 文件

**估时**：5m
**依赖**：无
**AC 覆盖**：AC7-AC10
**产出**：SKILL.md + 8 个 ref 文件同步到源码

### Steps

1. 同步 SKILL.md：
```bash
cp ~/.hermes/skills/sdd/sdd-orchestrator/SKILL.md /root/workspace/hermes-harness/skills/sdd/sdd-orchestrator/SKILL.md
```

2. 同步 8 个缺失 ref 文件：
```bash
for f in kanban-profile-integration.md profile-soul-architecture.md 4-layer-document-consistency.md phase-consistency-audit.md sdd-for-planning.md model-output-truncation-bug.md model-selection-production-validation.md orchestrator-fix-patterns.md; do
  cp ~/.hermes/skills/sdd/sdd-orchestrator/references/$f /root/workspace/hermes-harness/skills/sdd/sdd-orchestrator/references/$f
  echo "✅ $f"
done
```

3. 验证：
```bash
grep "version:" /root/workspace/hermes-harness/skills/sdd/sdd-orchestrator/SKILL.md
grep -c "delegate_task" /root/workspace/hermes-harness/skills/sdd/sdd-orchestrator/SKILL.md
ls /root/workspace/hermes-harness/skills/sdd/sdd-orchestrator/references/kanban-profile-integration.md
```

4. Commit：
```bash
git add skills/sdd/sdd-orchestrator/
git commit -m "fix(consistency): T4 Sync SKILL.md v2.6.0 + 8 ref 文件（D5-D7）"
```

---

## T5: 迁移 6 个旧 Reference 文件

**估时**：15m
**依赖**：T4
**AC 覆盖**：AC11-AC12
**产出**：6 个 ref 文件 delegate_task → Kanban 替换

### Steps

1. 对每个旧 ref 文件，编辑替换 delegate_task 引用：
   - `delegate-protocol.md`：头部添加 `⚠️ 已迁移` 标记；将委托描述替换为 Kanban create
   - `state-machine.md`：将 delegate_task 替换为 kanban create
   - `incremental-mode.md`：将 delegate_task 替换为 kanban create
   - `interrupt-recovery.md`：将 delegate_task 替换为 kanban create
   - `skill-maintenance-pattern.md`：将 delegate_task 替换为 kanban create
   - `pr-and-review-flow.md`：将 delegate_task 替换为 kanban create

2. 对 delegate-protocol.md，使用 `> **历史存档**` 标记保留旧内容

3. 验证：
```bash
for f in delegate-protocol.md state-machine.md incremental-mode.md interrupt-recovery.md skill-maintenance-pattern.md pr-and-review-flow.md; do
  count=$(grep -c "delegate_task" /root/workspace/hermes-harness/skills/sdd/sdd-orchestrator/references/$f 2>/dev/null || echo 0)
  echo "$f: $count delegate_task refs"
done
```

4. Commit：
```bash
git add skills/sdd/sdd-orchestrator/references/
git commit -m "fix(consistency): T5 迁移 6 个旧 ref 文件 delegate_task→Kanban（D8）"
```

---

## T6: 增强 orchestrator.py 上下文传播

**估时**：10m
**依赖**：无
**AC 覆盖**：AC13-AC15
**产出**：修改 `/root/workspace/hermes-harness/skills/sdd/sdd-orchestrator/scripts/orchestrator.py`

### Steps

1. 在 `delegate_agent()` 方法中增加 `_build_context_for_stage()` 函数

2. 将上下文注入到 `task_body` 的 `## 前置上下文` 章节

3. 上下文内容根据阶段动态填充：
   - PO→BA: PRD 摘要
   - BA→Architect: AC 列表摘要
   - Architect→Coder: 方案选择理由

4. 同步到 installed skill：
```bash
cp /root/workspace/hermes-harness/skills/sdd/sdd-orchestrator/scripts/orchestrator.py ~/.hermes/skills/sdd/sdd-orchestrator/scripts/orchestrator.py
```

5. 验证 orchestrator.py 语法：
```bash
python3 -c "import py_compile; py_compile.compile('/root/workspace/hermes-harness/skills/sdd/sdd-orchestrator/scripts/orchestrator.py', doraise=True); print('✅ Syntax OK')"
```

6. Commit：
```bash
git add skills/sdd/sdd-orchestrator/scripts/orchestrator.py
git commit -m "fix(consistency): T6 上下文传播机制（D9）"
```

---

## T7: 修复 Profile API Key 配置

**估时**：5m
**依赖**：无
**AC 覆盖**：AC16-AC17
**产出**：6 个 Profile config.yaml

### Steps

1. 对每个 Profile，移除 config.yaml 中的 api_key 字段（继承主配置）：

```bash
for p in sdd-po sdd-ba sdd-architect sdd-coder sdd-qa; do
  config=~/.hermes/profiles/$p/config.yaml
  # 移除 api_key 行和 delegation 块
  # 使用 python 或 sed
  python3 -c "
import yaml
with open('$config') as f:
    d = yaml.safe_load(f)
if 'api_key' in d.get('model', {}):
    del d['model']['api_key']
d.pop('delegation', None)
with open('$config', 'w') as f:
    yaml.dump(d, f, default_flow_style=False)
print('✅ Fixed $p')
"
done
```

2. 验证：
```bash
for p in sdd-po sdd-ba sdd-architect sdd-coder sdd-reviewer sdd-qa; do
  echo "=== $p ==="
  grep "api_key" ~/.hermes/profiles/$p/config.yaml || echo "  ✅ 无 api_key"
done
```

3. **注意**：sdd-reviewer 也需要移除 api_key，但保留 deepseek-v4-pro 模型配置

---

## T8: 归档补全与 Cleanup

**估时**：5m
**依赖**：T2, T4
**AC 覆盖**：D4
**产出**：manifest 补全 + deprecated 文件删除

### Steps

1. 删除 deprecated 文件：
```bash
rm /root/workspace/hermes-harness/scripts/setup-sdd-profiles.sh.deprecated
```

2. 验证 manifest 已在之前修复步骤中完成：
```bash
test -f /root/workspace/hermes-harness/docs/archive/001-profile-soul-架构落地与机制验证/manifest.json && echo "✅ manifest.json exists"
```

3. 更新 docs/current/ 的版本记录（prd.md、spec.md、design.md）

4. Commit：
```bash
git add docs/current/ scripts/setup-sdd-profiles.sh.deprecated
git commit -m "fix(consistency): T8 归档补全 + cleanup（D4）"
```

---

## 汇总

| # | Task | 估时 | 产出文件数 | 缺陷覆盖 |
|---|------|:---:|:---:|:--------:|
| T1 | 创建 QUIRKS.md | 2m | 1 | D1 |
| T2 | 精简 AGENTS.md | 10m | 1 | D2-D3 |
| T3 | architecture.md 补充 | 5m | 1 | D3 |
| T4 | Sync SKILL.md + 8 ref | 5m | 9 | D5-D7 |
| T5 | 迁移 6 个旧 ref 文件 | 15m | 6 | D8 |
| T6 | 上下文传播增强 | 10m | 1 | D9 |
| T7 | Profile API Key 修复 | 5m | 6 | D10 |
| T8 | 归档补全 + cleanup | 5m | 2 | D4 |
| **总计** | | **57m** | **27** | **D1-D10** |
