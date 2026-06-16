# Code Review Report (Re-Review)

> 变更 ID: 001-profile-soul-架构落地与机制验证
> 评审日期: 2026-06-16
> 评审轮次: Re-review (第 2 轮)
> 评审人: sdd-reviewer (deepseek-v4-pro)
> 流程级别: Standard

---

## Summary

**评审结论：不通过 — 存在 3 个 CRITICAL 问题，3 个 MAJOR 问题**

第 1 轮 Review 发现的 6 CRITICAL + 3 MAJOR 问题中，**5 项已完全修复**，但修复过程中引入了新的回归和残留缺陷：

1. **C3 model_audit 修复不完整** — 数据结构和读取命令已存在，但写入路径完全缺失（save_state/load_state 未序列化 model_audit，transition 中不写入审计记录）
2. **L2.5 门禁未按 AC20 实现** — 仍只检查 completion-report.md 存在性，未检查代码文件→测试文件的对应关系
3. **轮询逻辑存在 3 处偏差** — 不重建 Kanban 任务（AC13）、不标记 BLOCKED 于超时、检测方法脆弱
4. **soul-injection 验证门控/展示不一致** — 展示阈值 100% 但实际门控仍为 60%

总体评价：第 1 轮的修复方向正确，代码结构改善明显，但实现不彻底。修复这些残余 CRITICAL/MAJOR 问题后可通过。

---

## Critical Issues (必须修复，阻断合并)

### C1: model_audit 写入路径完全缺失（C3 修复回归）

- **文件**: `skills/sdd/sdd-orchestrator/scripts/orchestrator.py`
- **行号**: 152, 204-224, 226-247, 512-566
- **严重级别**: CRITICAL
- **违反 AC**: AC21, AC22
- **问题**: `model_audit` 字段在 `SDDState` dataclass 中已定义（line 152），`do_audit()` 命令也实现了读取和展示（line 862-898），但存在以下缺陷：
  1. `save_state()` (line 204-224) 的 `state_dict` 中未包含 `model_audit` — 审计记录永远写不到磁盘
  2. `load_state()` (line 226-247) 构造 `SDDState` 时未读取 `model_audit` — 即使手动写入 JSON 也读不到
  3. `transition()` (line 512-566) 中没有任何 `state.model_audit.append(...)` 调用 — 审计记录从不产生
  4. `delegate_agent()` 中创建 Kanban 任务后，没有将 task_id/model/provider 写入 model_audit

- **修复建议**:
```python
# save_state 中添加:
state_dict["model_audit"] = state.model_audit

# load_state 中添加:
model_audit=data.get("model_audit", []),

# transition() 中添加（在 save_state 之前）:
state.model_audit.append({
    "stage": current.state_name,
    "model": profile_model if profile else "default",
    "provider": profile_provider if profile else "default",
    "kanban_task_id": task_id,
    "completed_at": datetime.utcnow().isoformat() + "Z",
})
```

### C2: L2.5 门禁未按 Spec 实现代码测试覆盖检查

- **文件**: `skills/sdd/sdd-orchestrator/scripts/orchestrator.py`
- **行号**: 463-466
- **严重级别**: CRITICAL
- **违反 AC**: AC20
- **问题**: 第 1 轮 Review 指出 C4（门禁未升级为内容质量检查），Coder 修复了 L1/L1+L2/L2 的内容检查，但 L2.5 仍然只检查 `completion-report.md` 文件存在性。AC20 明确要求：
  - 检查代码目录包含 `.py` 文件（非 `__init__.py`）
  - 检查每个代码文件存在对应的 `test_*.py` 或 `*_test.py`
  - 无测试文件时不阻塞（退出码 0）但输出警告

- **当前代码** (line 463-466):
```python
if "L2.5" in level:
    completion_file = change_dir / "completion-report.md"
    if not completion_file.exists():
        errors.append("completion-report.md 不存在")
```

- **修复建议**: 替换为完整的代码+测试覆盖扫描：
```python
if "L2.5" in level:
    # 扫描代码文件中非 __init__.py 的 .py 文件
    code_files = []
    for py_file in (change_dir / "src").rglob("*.py"):
        if py_file.name != "__init__.py":
            code_files.append(py_file)
    for code_file in code_files:
        test_name = f"test_{code_file.stem}.py"
        test_path = code_file.parent / test_name
        if not test_path.exists():
            test_path = code_file.parent / f"{code_file.stem}_test.py"
        if not test_path.exists():
            print(f"  ⚠  {code_file.name} 缺少对应测试文件")
    # AC20: 不阻塞但输出警告
```

### C3: Kanban 任务轮询逻辑的多处偏差

- **文件**: `skills/sdd/sdd-orchestrator/scripts/orchestrator.py`
- **行号**: 568-583, 693-740
- **严重级别**: CRITICAL
- **违反 AC**: AC11, AC13, AC14
- **问题**: 轮询机制已实现但有三处关键偏差：

  1. **不重建 Kanban 任务 (AC13)**: blocked 时只重新轮询，未"自动重新创建 Kanban 任务"。AC13 要求 "新任务 body 中包含上一次失败的简要原因"
  2. **超时不设 BLOCKED (AC14)**: 3 次超时后只打印 "所有重试耗尽"，未将状态更新为 `BLOCKED` 且不写入 `blocked_reason`
  3. **轮询间隔与 Spec 不一致 (AC11)**: Spec 要求 "每 10 秒轮询一次"，代码使用 5s

- **修复建议**:
```python
# 1. blocked 时重建任务而非仅重试:
if status == "blocked":
    if attempt < max_retries - 1:
        # 读取 blocked reason 后重新创建任务
        last_error = self._get_task_error(task_id)
        result = subprocess.run(["hermes", "kanban", "create", ...], ...)
        task_id = extract_task_id(result.stdout)  # 新 task id
        continue
    else:
        # 3次均失败 → BLOCKED
        ...

# 2. timeout 耗尽后设 BLOCKED:
# 在 for 循环结束后:
state_data = self.load_state(change_id)
state_data.current_state = "BLOCKED"
state_data.metadata["blocked_reason"] = f"任务 {task_id} 超时（3次尝试）"
self.save_state(change_id, state_data)

# 3. 将 poll_interval 改为 10
status = self._poll_kanban_task(task_id, poll_interval=10, timeout=600)
```

---

## Major Issues (建议修复，合并前须修复)

### M1: validate-soul-injection.sh 门控与展示阈值不一致

- **文件**: `scripts/validate-soul-injection.sh`
- **行号**: 111-122
- **严重级别**: MAJOR
- **违反 AC**: AC8（Soul 内容质量验证）
- **问题**: 第 1 轮 Review 的 M3 要求将阈值从 60% 提高到 100%。Coder 修改了展示行 (line 111 `-ge 100`) 但**未修改实际通过门控** (line 118 `-ge 60`)。效果：即使覆盖率只有 60%，该函数返回 0（通过），但打印中说 "需要全匹配"。这是一个明显的未完成修复。

- **当前代码**:
```bash
# line 111-115: 展示侧用 100%
if [ "$coverage" -ge 100 ]; then
    echo -e "  ${GREEN}✓${NC} 关键词覆盖率: ${coverage}%..."
# line 118: 门控仍为 60%
if [ "$coverage" -ge 60 ]; then
    return 0
```

- **修复建议**: 将 line 118 的 `60` 改为 `100`，或将门控阈值统一为 80% 并在两个位置保持一致。

### M2: _poll_kanban_task 状态检测过于脆弱

- **文件**: `skills/sdd/sdd-orchestrator/scripts/orchestrator.py`
- **行号**: 568-583
- **严重级别**: MAJOR
- **问题**: 使用字符串匹配 `"done" in line` / `"blocked" in line` 检测 Kanban 任务状态。如果任务标题或描述中包含这些词汇，会产生误判。此外，`hermes kanban list` 的输出格式可能变化。

- **修复建议**: 使用 `hermes kanban show <task_id> --json` 并解析 JSON 中的 `status` 字段：
```python
result = subprocess.run(
    ["hermes", "kanban", "show", task_id, "--json"],
    capture_output=True, text=True, timeout=15
)
import json
data = json.loads(result.stdout)
status = data.get("task", {}).get("status", "unknown")
return status  # "done", "blocked", "running", etc.
```

### M3: init-profiles.sh 不写入模型/Provider 到 config.yaml

- **文件**: `scripts/init-profiles.sh`
- **行号**: 209
- **严重级别**: MAJOR
- **违反 AC**: AC7（"config.yaml 中 model 字段值为 doubao-seed-2.0-pro"）
- **问题**: Line 209 注释说 "config.yaml 由 Hermes 自动生成，不需要手动写入"。但 `hermes profile create` 生成的默认 config.yaml 不会自动从 AGENTS.md 读取模型/Provider 配置。这意味着初始化后 config.yaml 中的模型字段可能为空或默认值，不满足 AC7 的精确值要求。

- **修复建议**: 在 `create_profile()` 中，创建 Profile 后，根据 AGENTS.md 的 `role_to_profile` 配置写入对应的 model/provider：
```bash
# 在 hermes profile create 之后写入模型配置
cat > "$profile_dir/config.yaml" <<EOF
model:
  name: "$model_name"
provider:
  name: "$provider_name"
workdir:
  root: "$PROJECT_ROOT"
skills:
  external_dirs:
    - "$PROJECT_ROOT/skills"
EOF
```

---

## Minor Issues (可选优化)

### m1: status 命令无进度条

- **文件**: `skills/sdd/sdd-orchestrator/scripts/orchestrator.py`
- **行号**: 830-860 (`status()`)
- **违反 AC**: AC25
- **问题**: 第 1 轮 Review 的 m1 未修复。Spec 要求 `[●●○○○○○○]` 6 位置进度条。

- **修复建议**: 添加辅助方法：
```python
def _render_progress_bar(self, current_state: str) -> str:
    stages = ["PO", "BA", "ARCHITECT", "CODER", "REVIEWER", "QA"]
    state_to_stage = {
        "PO_ENTRY": 0, "PO_CHECK": 0, "PO_DONE": 1,
        "BA_ENTRY": 1, "BA_CHECK": 1, "BA_DONE": 2,
        "ARCHITECT_ENTRY": 2, "ARCHITECT_CHECK": 2, "ARCHITECT_DONE": 3,
        "CODER_ENTRY": 3, "CODER_CHECK": 3,
        "REVIEWER_ENTRY": 4, "REVIEWER_CHECK": 4,
        "QA_ENTRY": 5, "QA_CHECK": 5, "DONE": 6,
    }
    pos = state_to_stage.get(current_state, 0)
    return "[" + "●" * pos + "○" * (6 - pos) + "]"
```

### m2: 项目无任何测试文件

- **严重级别**: MINOR
- **问题**: 搜索 `test_*.py` / `*_test.py` / `test_*.sh` 返回 0 结果。SDD 框架号称 TDD 驱动，但自身无测试。

- **修复建议**: 添加 `scripts/tests/` 目录包含脚本冒烟测试。

### m3: init-profiles.sh read -p 在 macOS bash 3.x 兼容性

- **文件**: `scripts/init-profiles.sh`
- **行号**: 268
- **问题**: `read -p " 确认继续？" -n 1 -r` 在 macOS 自带的 bash 3.x 上 `-p` 与 `-n` 不兼容。

- **修复建议**:
```bash
echo -n "  确认继续？(y/N): "
read -n 1 -r
```

### m4: _poll_kanban_task 使用 `hermes kanban list` 无分页保护

- **文件**: `skills/sdd/sdd-orchestrator/scripts/orchestrator.py`
- **行号**: 573
- **问题**: 如果 Kanban 任务数量多，`hermes kanban list` 输出可能很长，字符串匹配 "done"/"blocked" 效率低。建议使用 `hermes kanban show <id>` 精确查询。

---

## Good Points

+ **C2 修复正确且彻底**: ROLE_TO_PROFILE_DEFAULT 完全对齐 AGENTS.md 的 6 个 Profile
+ **C4 L1/L1+L2/L2 内容检查完整**: execute_lint 升级为基于正则的章节/AC/架构结构检查，覆盖 AC15-AC19
+ **C5 端到端验证脚本质量好**: validate-end-to-end.sh 支持自动检测 change_id、产物文件存在性+大小检查、清晰的退出码
+ **C6 模板目录结构合理**: config.yaml.template 和 SOUL.md.template 占位符清晰，文档说明完整
+ **M1 脚本去重完成**: setup-sdd-profiles.sh 已重命名为 .deprecated
+ **M2 project_root 修复正确**: 使用 `Path(__file__).resolve().parents[4]` 自推导
+ **轮询架构骨架良好**: delegate_agent 中的 polling loop 结构清晰（retry/block/timeout 分支分明），只需修补具体行为
+ **代码整体结构改善**: orchestrator.py 从 700+ 行增长到 959 行，新增 audit 命令、轮询机制、内容门禁，功能密度提升
+ **文档质量保持**: AGENTS.md、architecture.md、PROFILES-GUIDE.md 信息密度高

---

## 评审统计

| 维度 | 第 1 轮 | 第 2 轮 (本次) |
|------|:----:|:----:|
| AC 总数 | 25 | 25 |
| AC 通过 | 12 | 17 |
| AC 部分覆盖 | 4 | 3 |
| AC 未覆盖 | 9 | 5 |
| CRITICAL 问题 | 6 | 3 |
| MAJOR 问题 | 3 | 3 |
| MINOR 问题 | 4 | 4 |

**已解决的 AC**: AC5(版本检查 ✓), AC11(轮询机制已在/偏差在间隔), AC12(自动推进 ✓), AC15(PRD检查 ✓), AC16(PRD拒绝 ✓), AC17(AC格式 ✓), AC18(AC拒绝 ✓), AC19(Design检查 ✓), AC22(audit命令 ✓), AC24(端到端脚本 ✓)

**仍待解决的 AC**: AC13(不重建任务), AC14(超时不BLOCKED), AC20(L2.5不检查测试), AC21(audit不写入), AC25(无进度条)

---

## 问题汇总表

| # | 严重级别 | 文件 | 行号 | 问题摘要 |
|---|:---:|------|:---:|---------|
| C1 | CRITICAL | orchestrator.py | 152/204-224/226-247/512-566 | model_audit 写入路径缺失 (save/load/transition 未处理) |
| C2 | CRITICAL | orchestrator.py | 463-466 | L2.5 只检查 completion-report.md 而非代码测试覆盖 |
| C3 | CRITICAL | orchestrator.py | 568-583/693-740 | 轮询不重建任务(AC13)、超时不BLOCKED(AC14)、间隔5s≠10s |
| M1 | MAJOR | validate-soul-injection.sh | 111-122 | 门控阈值60%与展示阈值100%不一致 |
| M2 | MAJOR | orchestrator.py | 568-583 | _poll_kanban_task 字符串匹配状态检测脆弱 |
| M3 | MAJOR | init-profiles.sh | 209 | 不写入模型/Provider 到 config.yaml (AC7) |
| m1 | MINOR | orchestrator.py | 830-860 | status 命令无进度条 (AC25) |
| m2 | MINOR | 项目全局 | — | 无任何测试文件 |
| m3 | MINOR | init-profiles.sh | 268 | read -p 在 macOS bash 3.x 兼容性 |
| m4 | MINOR | orchestrator.py | 568-583 | 无分页/精确查询 |

---

## 下一步建议

1. **优先修复 C1 + C2 + C3** — 这三个 CRITICAL 问题集中在 orchestrator.py，单人半天可修完
2. **修复 M1** — 一行改动（60→100），验证阈值与展示一致
3. **修复 M2 + M3** — 中等工作量，提升健壮性和 AC7 合规
4. **可选修复 m1-m4** — 不影响功能交付，可延后到后续迭代
5. **修复后进入 QA 阶段** — 修复全部 CRITICAL 问题后可推进到 QA_ENTRY
