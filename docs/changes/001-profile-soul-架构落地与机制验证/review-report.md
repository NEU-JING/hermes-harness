# Code Review Report

> 变更 ID: 001-profile-soul-架构落地与机制验证
> 评审日期: 2026-06-16
> 评审人: sdd-reviewer (deepseek-v4-pro)
> 流程级别: Standard

---

## Summary

**评审结论：不通过 — 存在 6 个 CRITICAL 问题，3 个 MAJOR 问题**

核心问题集中在三个方面：
1. **orchestrator.py 缺失 R5/R6/R7/R9 四项关键需求的实现**（无轮询、无重试、无审计、无进度条）
2. **架构严重不一致** — orchestrator 硬编码默认 3 个 Profile（sdd-flash/sdd-pro/sdd-reviewer），与 AGENTS.md/Design 定义的 6 个 Profile（sdd-po/sdd-ba/sdd-architect/sdd-coder/sdd-reviewer/sdd-qa）完全不一致
3. **R3 验证脚本缺失 validate-end-to-end.sh + R8 模板目录缺失**

代码本身（init-profiles.sh、验证脚本）结构良好，但核心编排器功能严重不完整。

---

## Critical Issues (必须修复，阻断合并)

### C1: orchestrator.py 完全缺失 Kanban 任务轮询机制
- **文件**: `skills/sdd/sdd-orchestrator/scripts/orchestrator.py`
- **行号**: `delegate_agent()` 方法（line 520-621）
- **严重级别**: CRITICAL
- **违反 AC**: AC11, AC12, AC13, AC14
- **问题**: `delegate_agent()` 调用 `hermes kanban create` 创建任务后就结束了，没有任何轮询等待机制。Spec 要求每 10s 轮询一次，自动检测任务完成并推进状态，支持 3 次失败重试，3 次均失败后标记 BLOCKED。
- **现状**: 创建任务后打印"⏳ 等待任务完成..."就返回了，不等待也不检查结果。
- **修复建议**:
```python
def delegate_agent(self, change_id, state):
    # ... 创建 Kanban 任务 ...
    task_id = extract_task_id(result.stdout)
    
    # 轮询等待任务完成
    max_retries = 3
    for attempt in range(max_retries + 1):
        poll_interval = 10  # seconds
        while True:
            time.sleep(poll_interval)
            task_status = self._poll_kanban_task(task_id)
            if task_status == "done":
                self.transition(change_id, next_gate_state)
                return
            elif task_status == "blocked":
                if attempt < max_retries:
                    # 重试
                    break
                else:
                    # 3次失败 → BLOCKED
                    self._set_blocked(change_id, task_id, error_info)
                    return
```

### C2: orchestrator.py 默认 Profile 映射与 AGENTS.md/Design 严重不一致
- **文件**: `skills/sdd/sdd-orchestrator/scripts/orchestrator.py`
- **行号**: 268-275 (`ROLE_TO_PROFILE_DEFAULT`)
- **严重级别**: CRITICAL
- **违反 Design**: Section 2.2 定义 6 个 Profile，AGENTS.md 定义 6 个 Profile
- **问题**: orchestrator 硬编码默认 3 个 Profile：
  - `sdd-flash` (覆盖 PO/BA/QA → DOUBAO_CHAT) — AGENTS.md/Design 中是 `sdd-po`/`sdd-ba`/`sdd-qa` 配 doubao-seed-2.0-pro
  - `sdd-pro` (覆盖 Architect/Coder → DOUBAO_REASONING) — AGENTS.md/Design 中是 `sdd-architect`(glm-5.1) + `sdd-coder`(doubao-seed-2.0-code)
  - `sdd-reviewer` (唯一一致)
- **影响**: 使用这张表的任何代码都会创建错误的 Profile。`setup-sdd-profiles.sh` 也创建的是这三个 Profile，与 `init-profiles.sh`（创建 6 个）完全重复且冲突。
- **修复建议**: `ROLE_TO_PROFILE_DEFAULT` 应与 AGENTS.md 保持一致，或删除硬编码默认，完全从 AGENTS.md 读取：
```python
ROLE_TO_PROFILE_DEFAULT = {
    "po": "sdd-po",
    "ba": "sdd-ba",
    "architect": "sdd-architect",
    "coder": "sdd-coder",
    "reviewer": "sdd-reviewer",
    "qa": "sdd-qa",
}
```

### C3: orchestrator.py 缺失 model_audit 功能（R7 完全未实现）
- **文件**: `skills/sdd/sdd-orchestrator/scripts/orchestrator.py`
- **严重级别**: CRITICAL
- **违反 AC**: AC21, AC22
- **问题**: 代码中完全不存在以下内容：
  - `.sdd-state.json` 无 `model_audit` 字段写入逻辑
  - 无 `audit` CLI 子命令
  - 无模型/Provider 记录逻辑
  - 无模型一致性对比逻辑
- **修复建议**: 在 `transition()` 成功后写入 `model_audit` 记录；新增 `do_audit()` 方法实现审计报告输出。

### C4: orchestrator.py 门禁检查仍为文件存在检查，未升级为内容质量检查（R6 未实现）
- **文件**: `skills/sdd/sdd-orchestrator/scripts/orchestrator.py`
- **行号**: `execute_lint()` 方法 (line 377-457)
- **严重级别**: CRITICAL
- **违反 AC**: AC15, AC16, AC17, AC18, AC19, AC20
- **问题**: `execute_lint()` 只检查文件是否存在（`prd.md` / `spec.md` / `design.md`），完全没有执行 Spec 要求的：
  - L1: PRD 章节完整性检查（5 大章节正则匹配）
  - L1+L2: AC 格式检查（`#### Scenario AC{n}:` + WHEN/THEN/AND）
  - L2: Design 架构图/接口/数据结构/任务拆分检查
  - L2.5: 代码测试覆盖检查
- **修复建议**: 为每个 lint level 实现内容正则检查。示例：
```python
# L1: PRD 章节完整性
required_sections = [r'## 背景与目标|## 背景', r'## 用户场景', 
                     r'## 功能范围', r'## 非功能需求|## NFR', r'## 验收标准']
prd_content = (change_dir / "prd.md").read_text()
for pattern in required_sections:
    if not re.search(pattern, prd_content):
        errors.append(f"PRD 缺少章节: {pattern}")
```

### C5: 缺失 validate-end-to-end.sh（R3 第 4 个验证脚本）
- **文件**: `scripts/validate-end-to-end.sh` — 不存在
- **严重级别**: CRITICAL
- **违反 AC**: AC24（端到端流程产物完整性验证）
- **问题**: Spec R3 明确要求 4 个独立验证脚本，目前只交付了 3 个（isolation / soul / workspace），缺少端到端流程冒烟测试脚本。
- **修复建议**: 创建 `scripts/validate-end-to-end.sh`，验证 `docs/changes/{change_id}/` 下包含 prd.md / spec.md / design.md / review-report.md / qa-report.md 等完整产物链。

### C6: 缺失模板目录 scripts/templates/profile/（R8 未实现）
- **文件**: `scripts/templates/profile/` — 不存在
- **严重级别**: CRITICAL
- **违反 AC**: R8 约束项（模板库位 `scripts/templates/profile/`）
- **问题**: Spec R8 要求提供模板库 `scripts/templates/profile/` 包含 `config.yaml.tmpl` / `SOUL.md.tmpl` / `roles.json`。这些文件完全缺失。当前 `init-profiles.sh` 硬编码生成 config.yaml（line 206-211）而非从模板渲染。
- **注意**: `init-profiles.sh` 硬编码所有 Profile/Skill 映射（line 22-31），未从 AGENTS.md 的 `role_to_profile` 读取模型/Provider，这与 R8 "基于 AGENTS.md 配置自动生成"的要求矛盾。

---

## Major Issues (建议修复，合并前须修复)

### M1: init-profiles.sh 和 setup-sdd-profiles.sh 功能重复且互相冲突
- **文件**: `scripts/init-profiles.sh` vs `scripts/setup-sdd-profiles.sh`
- **严重级别**: MAJOR
- **问题**: 两个脚本做同一件事（创建 SDD Profile），但：
  - init-profiles.sh 创建 6 个 Profile（sdd-po/sdd-ba/sdd-architect/sdd-coder/sdd-reviewer/sdd-qa）
  - setup-sdd-profiles.sh 创建 3 个 Profile（sdd-flash/sdd-pro/sdd-reviewer）
  - Profile 名称、数量、模型分配完全不同
  - 各自有不同的配置逻辑
- **影响**: 用户不知道该用哪个，且用错会创建与 AGENTS.md 不匹配的 Profile
- **修复建议**: 明确两个脚本的定位或合并为一个。SDD 框架应只有一套 Profile 体系。`setup-sdd-profiles.sh` 当前与 orchestrator 的 ROLE_TO_PROFILE_DEFAULT 配套使用，但该默认值本身就有问题（见 C2）。

### M2: orchestrator.py 的 project_root 推导不健壮
- **文件**: `skills/sdd/sdd-orchestrator/scripts/orchestrator.py`
- **行号**: 158
- **严重级别**: MAJOR
- **问题**: `self.project_root = Path(project_root)` 默认 `"."`，依赖 CWD。但 Design Section 5 明确要求 "使用脚本位置推导绝对路径，不依赖 CWD"（`Path(__file__).resolve().parents[4]`）。
- **影响**: 在非项目目录执行 `orchestrator.py start ...` 会指向错误路径。
- **修复建议**:
```python
def __init__(self, project_root: str = None):
    if project_root is None:
        # 从脚本位置推导项目根目录
        self.project_root = Path(__file__).resolve().parents[4]
    else:
        self.project_root = Path(project_root).resolve()
```

### M3: validate-soul-injection.sh 验证逻辑过于宽松
- **文件**: `scripts/validate-soul-injection.sh`
- **行号**: 110-122
- **严重级别**: MAJOR
- **违反 AC**: AC9（Spec 说 "系统提示词中是否包含对应 SOUL.md 的关键特质关键词"，实际只检查文件存在和内容关键词覆盖率）
- **问题**: 
  1. 脚本只 grep SOUL.md 文件内容，不验证系统提示词是否真正注入了 Soul 内容
  2. 关键词覆盖率阈值设为 60%（line 111），太宽松 — 3 个关键词中只匹配 2 个就通过
  3. 失败时退出码为 1 （line 180）但开头提示说 "部分未完全通过"，语气模糊
- **修复建议**: 最低阈值提高到 100%（3/3 完全匹配对应角色定义的核心特质关键词），或降级为 2/3 但明确标注为 WARNING 而非通过。

---

## Minor Issues (可选优化)

### m1: orchestrator.py status 命令无进度条显示
- **文件**: `skills/sdd/sdd-orchestrator/scripts/orchestrator.py`
- **行号**: `status()` 方法 (line 706-736)
- **违反 AC**: AC25
- **问题**: AC25 要求进度条 `[●●○○○○○○]`，当前 status 只输出纯文本状态。进度条实现简单，但属于体验增强。
- **修复建议**: 添加 `_render_progress_bar(current_state)` 方法。

### m2: init-profiles.sh 强制模式使用 read -p 在 macOS 下可能有问题
- **文件**: `scripts/init-profiles.sh`
- **行号**: 270-271
- **严重级别**: MINOR
- **问题**: `read -p " 确认继续？(y/N): " -n 1 -r` 中 `-p` prompt 在 macOS 的 bash 3.x 上行为不同（某些版本不支持 `-p` 与 `-n` 同时使用）。
- **修复建议**: 拆分为 `echo` + `read`：
```bash
echo -n "  确认继续？(y/N): "
read -n 1 -r
```

### m3: 缺少测试文件 — 验证脚本没有被测试
- **严重级别**: MINOR
- **问题**: 项目完全没有测试文件（搜索 `test_*.py` / `*_test.py` / `test_*.sh` 返回 0 结果）。虽然 Shell 脚本测试通常较难，但至少应有基本的冒烟测试。
- **修复建议**: 添加 `scripts/tests/` 目录，包含基本的冒烟测试脚本。

### m4: 验证脚本 output 模式不一致
- **文件**: `scripts/validate-*.sh`
- **问题**: 三个验证脚本的退出条件不一致：
  - validate-profile-isolation.sh: 失败→exit 1, 通过→exit 0 ✓
  - validate-soul-injection.sh: 部分失败→exit 1, 通过→exit 0 ✓（但 exit 1 时消息说 "未完全通过" 而非 "失败"）
  - validate-workspace-binding.sh: 失败→exit 1, 通过→exit 0 ✓
- 轻微的语言不一致（"未完全通过" vs "检查失败"），但功能上符合 AC "退出码 0=全部通过 1=存在失败项"。

---

## Good Points

+ **init-profiles.sh 结构清晰**：参数解析、版本检查、权限验证、Profile 创建、统计输出五个阶段划分明确
+ **验证脚本独立性好**：每个脚本可独立运行，符合 R3 要求
+ **orchestrator.py 状态机设计合理**：Enum-based 状态定义、StateType 分类、TRANSITIONS 表清晰
+ **AGENTS.md 更新完整**：Profile 能力矩阵、Soul 配置示例、Workspace 规范、三层架构图齐全
+ **PROFILES-GUIDE.md 文档质量好**：包含快速开始、配置、Soul、验证工具、FAQ、最佳实践六章
+ **architecture.md 更新详细**：Profile+Soul 双层架构、Workspace 绑定原理、版本兼容性降级方案齐全
+ **orchestrator skill doc 严谨**：SKILL.md 有 mermaid 状态图、转换矩阵表、委托协议规范、集成说明
+ **异构评审模式已体现在 design/AGENTS.md 中**：Reviewer 使用 DeepSeek 独立 Provider 的架构决策有明确记录

---

## 评审统计

| 维度 | 结果 |
|------|:----:|
| AC 总数 | 25 |
| AC 被覆盖并验证通过 | 12 |
| AC 部分覆盖（存在缺陷）| 4 (AC8/AC9 validation logic, AC23 incomplete) |
| AC 未覆盖 | 9 (AC11-14, AC15-20, AC21-22, AC25) |
| CRITICAL 问题 | 6 |
| MAJOR 问题 | 3 |
| MINOR 问题 | 4 |

## 问题汇总表

| # | 严重级别 | 文件 | 问题摘要 |
|---|:---:|------|---------|
| C1 | CRITICAL | orchestrator.py:520-621 | 缺失 Kanban 任务轮询/重试/阻塞机制 |
| C2 | CRITICAL | orchestrator.py:268-275 | Profile 默认映射与 AGENTS.md/Design 不一致 |
| C3 | CRITICAL | orchestrator.py (全文件) | 缺失 model_audit 功能（R7） |
| C4 | CRITICAL | orchestrator.py:377-457 | 门禁检查未升级为内容质量检查（R6） |
| C5 | CRITICAL | scripts/ (缺失) | validate-end-to-end.sh 不存在（R3） |
| C6 | CRITICAL | scripts/templates/ (缺失) | 模板目录不存在（R8） |
| M1 | MAJOR | init-profiles.sh vs setup-sdd-profiles.sh | 两个脚本重复且 Profile 定义冲突 |
| M2 | MAJOR | orchestrator.py:158 | project_root 依赖 CWD 而非脚本路径推导 |
| M3 | MAJOR | validate-soul-injection.sh:110 | 阈值 60% 过松且不验证实际系统提示词注入 |
| m1 | MINOR | orchestrator.py:706 | status 命令无进度条 |
| m2 | MINOR | init-profiles.sh:270 | read -p 在 macOS bash 3.x 兼容性 |
| m3 | MINOR | 项目全局 | 无任何测试文件 |
| m4 | MINOR | validate-*.sh | 输出措辞微不一致 |

---

## 下一步建议

1. **优先修复 C1-C4** (orchestrator.py) — 这四个问题是 R5/R6/R7 的核心缺失，需返回 Coder 补充实现
2. **修复 C2 并统一 Profile 体系** — 删除 `setup-sdd-profiles.sh` 或将其与 `init-profiles.sh` 合并，消除 3 Profile vs 6 Profile 的歧义
3. **创建 C5 + C6** — 补充 validate-end-to-end.sh 和模板目录
4. **修复 M1-M3** — 消除脚本冲突、健壮路径推导、收紧 Soul 验证逻辑
5. **修复后重新 Review** — 修复全部 CRITICAL 问题后，转入 QA 阶段
