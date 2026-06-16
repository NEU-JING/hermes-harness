#!/usr/bin/env python3
"""
SDD Orchestrator v2.6.0 — 严格状态机编排器

职责：
1. 状态管理：维护 .sdd-state.json，驱动状态机推进
2. 门禁强制：每个状态转换必须通过对应Level的lint检查
3. Agent委托：使用 delegate_task 实际调度各角色Agent
4. 流程管控：任何偏离都阻断，必须修复后才能继续
5. Profile解析（v2.1.0）：根据角色解析Hermes Profile实现模型分级委托

用法:
    python orchestrator.py start "变更描述" [--quick|--enhanced]
    python orchestrator.py resume [change_id]
    python orchestrator.py status [change_id]
    python orchestrator.py transition <change_id> <target_state>
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum

# 状态定义
class StateType(Enum):
    INITIAL = "initial"
    EXECUTING = "executing"
    GATE = "gate"
    WAITING = "waiting"
    TERMINAL = "terminal"

class State(Enum):
    IDLE = ("IDLE", StateType.INITIAL)
    PO_ENTRY = ("PO_ENTRY", StateType.EXECUTING)
    PO_CHECK = ("PO_CHECK", StateType.GATE)
    PO_DONE = ("PO_DONE", StateType.WAITING)
    BA_ENTRY = ("BA_ENTRY", StateType.EXECUTING)
    BA_CHECK = ("BA_CHECK", StateType.GATE)
    BA_DONE = ("BA_DONE", StateType.WAITING)
    ARCHITECT_ENTRY = ("ARCHITECT_ENTRY", StateType.EXECUTING)
    ARCHITECT_CHECK = ("ARCHITECT_CHECK", StateType.GATE)
    ARCHITECT_DONE = ("ARCHITECT_DONE", StateType.WAITING)
    CODER_ENTRY = ("CODER_ENTRY", StateType.EXECUTING)
    CODER_CHECK = ("CODER_CHECK", StateType.GATE)
    REVIEWER_ENTRY = ("REVIEWER_ENTRY", StateType.EXECUTING)
    REVIEWER_CHECK = ("REVIEWER_CHECK", StateType.GATE)
    QA_ENTRY = ("QA_ENTRY", StateType.EXECUTING)
    QA_CHECK = ("QA_CHECK", StateType.GATE)
    USER_ACCEPT = ("USER_ACCEPT", StateType.WAITING)
    ARCHIVE_ENTRY = ("ARCHIVE_ENTRY", StateType.EXECUTING)
    DONE = ("DONE", StateType.TERMINAL)
    BLOCKED = ("BLOCKED", StateType.TERMINAL)

    def __init__(self, name: str, state_type: StateType):
        self.state_name = name
        self.state_type = state_type

# Lint Level 映射
STATE_LINT_MAP = {
    (State.IDLE, State.PO_ENTRY): "L0",
    (State.PO_ENTRY, State.PO_CHECK): "L1",
    (State.BA_ENTRY, State.BA_CHECK): "L1+L2",
    (State.ARCHITECT_ENTRY, State.ARCHITECT_CHECK): "L2",
    (State.CODER_ENTRY, State.CODER_CHECK): "L2.5",
    (State.REVIEWER_ENTRY, State.REVIEWER_CHECK): "L3",
    (State.QA_ENTRY, State.QA_CHECK): "L3",
    (State.ARCHIVE_ENTRY, State.DONE): "R10+L3",
}

# Agent 映射
STATE_AGENT_MAP = {
    State.PO_ENTRY: "po-agent",
    State.BA_ENTRY: "ba-agent",
    State.ARCHITECT_ENTRY: "architect-agent",
    State.CODER_ENTRY: "coder-agent",
    State.REVIEWER_ENTRY: "reviewer-agent",
    State.QA_ENTRY: "qa-agent",
}

# Role 映射（用于 Profile 选择）
STATE_ROLE_MAP = {
    State.PO_ENTRY: "po",
    State.BA_ENTRY: "ba",
    State.ARCHITECT_ENTRY: "architect",
    State.CODER_ENTRY: "coder",
    State.REVIEWER_ENTRY: "reviewer",
    State.QA_ENTRY: "qa",
}

# 状态转换表
TRANSITIONS = {
    State.IDLE: [(State.PO_ENTRY, True)],  # (target_state, auto)
    State.PO_ENTRY: [(State.PO_CHECK, True)],
    State.PO_CHECK: [(State.PO_DONE, True)],
    State.PO_DONE: [(State.BA_ENTRY, False)],
    State.BA_ENTRY: [(State.BA_CHECK, True)],
    State.BA_CHECK: [(State.BA_DONE, True)],
    State.BA_DONE: [(State.ARCHITECT_ENTRY, False)],
    State.ARCHITECT_ENTRY: [(State.ARCHITECT_CHECK, True)],
    State.ARCHITECT_CHECK: [(State.ARCHITECT_DONE, True)],
    State.ARCHITECT_DONE: [(State.CODER_ENTRY, False)],
    State.CODER_ENTRY: [(State.CODER_CHECK, True)],
    State.CODER_CHECK: [(State.REVIEWER_ENTRY, True)],
    State.REVIEWER_ENTRY: [(State.REVIEWER_CHECK, True)],
    State.REVIEWER_CHECK: [
        (State.QA_ENTRY, True),  # review passed
        (State.CODER_ENTRY, True),  # review failed, back to coder
    ],
    State.QA_ENTRY: [(State.QA_CHECK, True)],
    State.QA_CHECK: [
        (State.USER_ACCEPT, True),  # qa passed
        (State.CODER_ENTRY, True),  # qa failed, back to coder
    ],
    State.USER_ACCEPT: [(State.ARCHIVE_ENTRY, False)],
    State.ARCHIVE_ENTRY: [(State.DONE, True)],
}

@dataclass
class StateHistoryEntry:
    from_state: str
    to_state: str
    at: str
    trigger: str
    auto: bool
    metadata: Dict = field(default_factory=dict)

@dataclass
class LintResult:
    level: str
    passed: bool
    at: str
    duration_ms: int
    errors: List[str]

@dataclass
class SDDState:
    change_id: str
    flow_level: str
    incremental_mode: bool
    current_state: str
    previous_state: Optional[str]
    state_history: List[StateHistoryEntry]
    lint_results: Dict[str, Optional[LintResult]]
    started_at: str
    updated_at: str
    metadata: Dict
    model_audit: List[Dict] = field(default_factory=list)  # C3: 模型使用审计

class SDDOrchestrator:
    """SDD编排器核心类 v2.6.0"""
    
    VERSION = "2.6.0"
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            # 从脚本位置推导项目根目录，不依赖 CWD
            self.project_root = Path(__file__).resolve().parents[4]
        else:
            self.project_root = Path(project_root).resolve()
        self.changes_dir = self.project_root / "docs" / "changes"
        self.archive_dir = self.project_root / "docs" / "archive"
        self.current_dir = self.project_root / "docs" / "current"

    def generate_change_id(self, description: str) -> str:
        """生成变更ID"""
        # 获取下一个序号
        existing = [d.name for d in self.changes_dir.iterdir() if d.is_dir()]
        numbers = [int(d.split("-")[0]) for d in existing if d.split("-")[0].isdigit()]
        next_num = max(numbers, default=0) + 1

        # 简化描述为slug
        slug = "".join(c if c.isalnum() else "-" for c in description.lower())[:30]
        slug = slug.strip("-")

        return f"{next_num:03d}-{slug}"

    def init_state_file(self, change_id: str, flow_level: str, description: str) -> SDDState:
        """初始化状态文件"""
        now = datetime.utcnow().isoformat() + "Z"

        state = SDDState(
            change_id=change_id,
            flow_level=flow_level,
            incremental_mode=False,
            current_state=State.IDLE.state_name,
            previous_state=None,
            state_history=[],
            lint_results={"L1": None, "L2": None, "L2.5": None, "L3": None},
            started_at=now,
            updated_at=now,
            metadata={
                "orchestrator_version": self.VERSION,
                "description": description,
            }
        )

        return state

    def save_state(self, change_id: str, state: SDDState):
        """保存状态文件"""
        state_file = self.changes_dir / change_id / ".sdd-state.json"
        state.updated_at = datetime.utcnow().isoformat() + "Z"

        # 转换dataclass为dict
        state_dict = {
            "change_id": state.change_id,
            "flow_level": state.flow_level,
            "incremental_mode": state.incremental_mode,
            "current_state": state.current_state,
            "previous_state": state.previous_state,
            "state_history": [asdict(h) for h in state.state_history],
            "lint_results": state.lint_results,
            "started_at": state.started_at,
            "updated_at": state.updated_at,
            "metadata": state.metadata,
        }

        with open(state_file, "w") as f:
            json.dump(state_dict, f, indent=2)

    def load_state(self, change_id: str) -> Optional[SDDState]:
        """加载状态文件"""
        state_file = self.changes_dir / change_id / ".sdd-state.json"

        if not state_file.exists():
            return None

        with open(state_file) as f:
            data = json.load(f)

        return SDDState(
            change_id=data["change_id"],
            flow_level=data["flow_level"],
            incremental_mode=data.get("incremental_mode", False),
            current_state=data["current_state"],
            previous_state=data.get("previous_state"),
            state_history=[StateHistoryEntry(**h) for h in data.get("state_history", [])],
            lint_results=data.get("lint_results", {}),
            started_at=data["started_at"],
            updated_at=data["updated_at"],
            metadata=data.get("metadata", {}),
        )

    def determine_flow_level(self, description: str, flags: Dict) -> str:
        """判定流程级别"""
        if flags.get("quick"):
            return "Quick"
        if flags.get("enhanced"):
            return "Enhanced"

        # 启发式判定
        complexity_indicators = [
            "重构", "架构", "模块", "系统", "框架",
            "重构", "rewrite", "refactor", "architecture"
        ]

        desc_lower = description.lower()
        complexity_score = sum(1 for ind in complexity_indicators if ind in desc_lower)

        # 简单规则：复杂度>2用Enhanced，默认Standard
        if complexity_score >= 3:
            return "Enhanced"
        elif complexity_score == 0 and len(description) < 50:
            return "Quick"
        else:
            return "Standard"

    # Profile 默认映射（完全对齐 AGENTS.md 的 6 个 Profile）
    ROLE_TO_PROFILE_DEFAULT = {
        "po": "sdd-po",
        "ba": "sdd-ba",
        "architect": "sdd-architect",
        "coder": "sdd-coder",
        "reviewer": "sdd-reviewer",
        "qa": "sdd-qa",
    }

    def load_profile_mapping(self) -> Dict[str, str]:
        """加载合并后的 role→profile 映射（默认 + AGENTS.md 覆盖）。

        AC10: AGENTS.md 无非注释 role_to_profile 配置时返回空映射
        （不启用 Profile 模式，保持向后兼容）。

        Returns:
            Dict[str, str]: 合并后的 role→profile 映射，或空 dict（未启用）
        """
        # 检查 AGENTS.md 是否明确启用了 Profile 模式
        agents_path = self.project_root / "AGENTS.md"
        has_user_overrides = False
        agents_overrides = {}

        if agents_path.exists():
            try:
                import re
                content = agents_path.read_text()
                # 有效角色集合（防止误匹配 convention_overrides 等段）
                valid_roles = {"po", "ba", "architect", "coder", "reviewer", "qa"}
                # 搜索 sdd_config.role_to_profile 段中的非注释映射行
                in_profile_section = False
                for line in content.split("\n"):
                    stripped = line.strip()
                    # 跳过注释行和空行
                    if stripped.startswith("#") or stripped == "":
                        continue
                    # 检测 role_to_profile 段入口
                    if "role_to_profile:" in stripped:
                        in_profile_section = True
                        continue
                    if in_profile_section:
                        # 遇到下一个顶级 key 则退出段
                        if stripped.endswith(":") and not stripped.startswith(" "):
                            in_profile_section = False
                            continue
                    if not in_profile_section:
                        continue
                    match = re.match(r'\s*(\w+):\s*"([^"]+)"', line)
                    if match:
                        role, profile = match.groups()
                        if role in valid_roles:
                            agents_overrides[role] = profile
                            has_user_overrides = True
            except Exception as e:
                print(f"⚠️  解析 AGENTS.md 失败: {e}，使用默认映射")

        # AC10: 无用户覆盖时返回空映射（不启用 Profile 模式）
        if not has_user_overrides:
            return {}

        # 有覆盖时：默认 + 覆盖浅合并
        mapping = dict(self.ROLE_TO_PROFILE_DEFAULT)
        mapping.update(agents_overrides)
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

    def execute_lint(self, level: str, change_id: str) -> Tuple[bool, List[str]]:
        """执行lint检查（v2.2: 升级为内容质量检查）"""
        import re
        change_dir = self.changes_dir / change_id

        print(f"🔍 执行 Level {level} 检查...")

        errors = []

        # Level 0: 初始化检查
        if "L0" in level:
            if not change_dir.exists():
                errors.append(f"变更目录不存在: {change_dir}")

        # Level 1: PRD 章节完整性检查（内容质量）
        if "L1" in level:
            prd_file = change_dir / "prd.md"
            spec_file = change_dir / "spec.md"

            if prd_file.exists() and prd_file.stat().st_size > 0:
                # L1: PRD 必须包含 5 大章节
                content = prd_file.read_text()
                required_sections = [
                    (r'## 背景|## 背景与目标', "背景"),
                    (r'## 用户场景|## 用例', "用户场景"),
                    (r'## 功能范围|## In Scope', "功能范围"),
                    (r'## 非功能需求|## NFR', "非功能需求"),
                    (r'## 验收标准', "验收标准"),
                ]
                for pattern, name in required_sections:
                    if not re.search(pattern, content):
                        errors.append(f"PRD 缺少章节: {name}")
            elif not prd_file.exists():
                errors.append("prd.md 不存在")
            elif prd_file.stat().st_size == 0:
                errors.append("prd.md 为空文件")

            if "L1+L2" in level:
                if spec_file.exists() and spec_file.stat().st_size > 0:
                    spec_content = spec_file.read_text()
                    # L1+L2: Spec 必须包含 AC 且格式符合 Scenario 规范
                    if not re.search(r'#### Scenario AC\d+:', spec_content):
                        errors.append("Spec 缺少 Scenario AC（格式：`#### Scenario AC{n}:`）")
                    # 检查 AC 包含 WHEN/THEN/AND
                    ac_count = len(re.findall(r'#### Scenario AC\d+:', spec_content))
                    when_count = len(re.findall(r'- \*\*WHEN\*\*', spec_content))
                    if ac_count > 0 and when_count < ac_count:
                        errors.append(f"AC 格式不完整: {ac_count} 个 Scenario 但只有 {when_count} 个 WHEN")
                elif not spec_file.exists():
                    errors.append("spec.md 不存在")

        # Level 2: 设计产物内容检查
        if "L2" in level:
            design_file = change_dir / "design.md"
            tasks_file = change_dir / "tasks.md"

            if design_file.exists() and design_file.stat().st_size > 0:
                design_content = design_file.read_text()
                # 检查包含架构图、接口定义、数据结构、任务拆分
                arch_indicators = [r'## 架构', r'架构图', r'架构总览', r'系统组件']
                if not any(re.search(p, design_content) for p in arch_indicators):
                    errors.append("Design 缺少架构描述（应包含架构图或架构总览章节）")
                if not re.search(r'## .*接口|## .*API|接口定义', design_content):
                    errors.append("Design 缺少接口定义")
                if not re.search(r'## .*数据|数据模型|数据结构', design_content):
                    errors.append("Design 缺少数据模型/结构定义")
                if not re.search(r'## .*任务|任务拆分', design_content):
                    errors.append("Design 缺少任务拆分章节")
            else:
                if not design_file.exists():
                    errors.append("design.md 不存在")

            if tasks_file.exists() and tasks_file.stat().st_size > 0:
                tasks_content = tasks_file.read_text()
                if not re.search(r'### Task ', tasks_content):
                    errors.append("tasks.md 不包含 Task 定义")
            elif not tasks_file.exists():
                errors.append("tasks.md 不存在")

        # Level 2.5: 代码产物检查
        if "L2.5" in level:
            completion_file = change_dir / "completion-report.md"
            if not completion_file.exists():
                errors.append("completion-report.md 不存在")

        # Level 3: 报告质量检查
        if "L3" in level:
            review_file = change_dir / "review-report.md"
            qa_file = change_dir / "qa-report.md"

            if "REVIEWER" in self.get_current_state(change_id):
                if not review_file.exists():
                    errors.append("review-report.md 不存在")

            if "QA" in self.get_current_state(change_id):
                if not qa_file.exists():
                    errors.append("qa-report.md 不存在")

        # R10: PR流程检查
        if "R10" in level:
            import subprocess
            try:
                result = subprocess.run(
                    ["git", "log", "-5", "--oneline", "--merges"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )
                if not result.stdout.strip():
                    errors.append("R10: 未检测到PR merge记录")
            except Exception as e:
                errors.append(f"R10检查失败: {e}")

        passed = len(errors) == 0

        if passed:
            print(f"  ✅ Level {level} 通过")
        else:
            print(f"  ❌ Level {level} 失败:")
            for err in errors:
                print(f"     - {err}")

        return passed, errors

    def get_current_state(self, change_id: str) -> str:
        """获取当前状态"""
        state = self.load_state(change_id)
        return state.current_state if state else "UNKNOWN"

    def transition(self, change_id: str, target_state: str, trigger: str = "manual", skip_delegate: bool = False) -> bool:
        """执行状态转换

        Args:
            change_id: 变更ID
            target_state: 目标状态
            trigger: 触发类型
            skip_delegate: 是否跳过Agent委托（存量任务/手动归档场景）
        """
        state = self.load_state(change_id)
        if not state:
            print(f"❌ 变更不存在: {change_id}")
            return False

        current = State[state.current_state]
        target = State[target_state]

        print(f"\n🔄 状态转换: {current.state_name} → {target.state_name}")

        # 检查转换是否合法
        valid_targets = TRANSITIONS.get(current, [])
        if target not in [t[0] for t in valid_targets]:
            print(f"❌ 非法状态转换: {current.state_name} → {target.state_name}")
            return False

        # 执行门禁检查（如果是 GATE → X 转换）
        if current.state_type == StateType.GATE:
            lint_level = STATE_LINT_MAP.get((current, target), "L1")
            passed, errors = self.execute_lint(lint_level, change_id)

            if not passed:
                print(f"⛔ 门禁检查失败，转换阻断")
                return False

        # 更新状态
        state.previous_state = state.current_state
        state.current_state = target.state_name

        # 记录历史
        history_entry = StateHistoryEntry(
            from_state=current.state_name,
            to_state=target.state_name,
            at=datetime.utcnow().isoformat() + "Z",
            trigger=trigger,
            auto=target in [t[0] for t in valid_targets if t[1]],
        )
        state.state_history.append(history_entry)

        # 保存状态
        self.save_state(change_id, state)

        print(f"✅ 转换成功: {target.state_name}")

        # 如果是执行状态，自动委托Agent（除非skip_delegate）
        if target.state_type == StateType.EXECUTING and target in STATE_AGENT_MAP:
            if skip_delegate:
                print(f"  ⏭️ 跳过Agent委托（--skip-delegate）")
            else:
                self.delegate_agent(change_id, target)

        # 如果是等待状态，提示用户
        if target.state_type == StateType.WAITING:
            self.prompt_user(change_id, target)

        return True

    def _poll_kanban_task(self, task_id: str, poll_interval: int = 5, timeout: int = 3600) -> str:
        """轮询 Kanban 任务状态，返回 done / blocked / timeout"""
        import subprocess, time
        deadline = time.time() + timeout
        while time.time() < deadline:
            result = subprocess.run(
                ["hermes", "kanban", "list"],
                capture_output=True, text=True, timeout=15
            )
            for line in result.stdout.split("\n"):
                if task_id in line and "done" in line:
                    return "done"
                if task_id in line and "blocked" in line:
                    return "blocked"
            time.sleep(poll_interval)
        return "timeout"

    def _build_context_for_stage(self, change_id: str, state: State) -> dict:
        """D9: 构建跨阶段上下文摘要，注入 Kanban task body

        Args:
            change_id: 当前变更 ID
            state: 当前目标状态（BA/ARCHITECT/CODER/REVIEWER/QA）

        Returns:
            dict: 包含前置摘要和约束条件的上下文
        """
        import re
        change_dir = self.changes_dir / change_id
        context = {}

        if state == State.BA_ENTRY:
            prd_path = change_dir / "prd.md"
            if prd_path.exists():
                text = prd_path.read_text()
                # 提取 PRD 摘要（前 200 字的核心背景）
                summary = text[:500].replace('\n', ' ').strip()
                context["前置摘要"] = f"PRD 摘要（前 500 字符）: {summary}"
        elif state == State.ARCHITECT_ENTRY:
            spec_path = change_dir / "spec.md"
            if spec_path.exists():
                text = spec_path.read_text()
                acs = re.findall(r'#### Scenario AC\d+:', text)
                context["前置摘要"] = f"Spec 包含 {len(acs)} 条 AC: {', '.join(acs)}"
        elif state == State.CODER_ENTRY:
            design_path = change_dir / "design.md"
            if design_path.exists():
                text = design_path.read_text()
                match = re.search(r'\*\*最终选择\*\*：(.+)', text)
                if match:
                    context["前置摘要"] = f"Design 方案选择: {match.group(1).strip()}"
                else:
                    context["前置摘要"] = "Design 已产出（见 design.md）"
        elif state == State.REVIEWER_ENTRY:
            spec_path = change_dir / "spec.md"
            tasks_path = change_dir / "tasks.md"
            if spec_path.exists():
                context["前置摘要"] = f"Spec 可用（{spec_path.stat().st_size} bytes）"
        elif state == State.QA_ENTRY:
            spec_path = change_dir / "spec.md"
            review_path = change_dir / "review-report.md"
            if review_path.exists():
                context["前置摘要"] = f"Review 已完成（{review_path.stat().st_size} bytes）"

        context["约束条件"] = "SDD 框架一致性修复，所有修改不破坏现有功能"
        return context

    def delegate_agent(self, change_id: str, state: State):
        """委托Agent执行任务（v2.1.0 真正的 Kanban Profile 调度）
        
        使用 Hermes 原生 Kanban 机制：
        1. hermes kanban create 创建任务，指定 --assignee=<profile>
        2. Kanban 调度器自动执行：hermes -p <profile> chat -q "work kanban task XXX"
        3. 每个 Profile 用自己的 config.yaml，天然实现不同模型用在不同阶段
        """
        agent_skill = STATE_AGENT_MAP.get(state)
        if not agent_skill:
            return
        
        # 解析 Profile
        role = STATE_ROLE_MAP.get(state)
        profile = self.get_profile_for_role(role) if role else None
        
        if not profile:
            print(f"⚠️  未找到角色 {role} 对应的 Profile，跳过委托")
            return
        
        print(f"\n🔷 委托 {agent_skill} → Profile: {profile}")
        
        # 构建任务上下文
        change_dir = self.changes_dir / change_id
        state_name = state.state_name.replace('_ENTRY', '').replace('_', ' ')
        
        context = {
            "change_id": change_id,
            "current_state": state.state_name,
            "change_dir": str(change_dir),
            "stage": state_name,
        }
        
        # 添加上下文产物路径
        if state == State.BA_ENTRY:
            context["prd_path"] = str(change_dir / "prd.md")
        elif state == State.ARCHITECT_ENTRY:
            context["spec_path"] = str(change_dir / "spec.md")
        elif state == State.CODER_ENTRY:
            context["tasks_path"] = str(change_dir / "tasks.md")
            context["design_path"] = str(change_dir / "design.md")
        elif state == State.REVIEWER_ENTRY:
            context["spec_path"] = str(change_dir / "spec.md")
            context["design_path"] = str(change_dir / "design.md")
            context["completion_path"] = str(change_dir / "completion-report.md")
        elif state == State.QA_ENTRY:
            context["spec_path"] = str(change_dir / "spec.md")
            context["review_path"] = str(change_dir / "review-report.md")
        
        # D9: 跨阶段上下文摘要
        context_extra = self._build_context_for_stage(change_id, state)
        context.update(context_extra)

        # 构建 task body
        body_lines = [f"# {change_id}: {state_name} 阶段", ""]
        body_lines.append("## 任务目标")
        body_lines.append(f"产出{state_name}阶段产物，使用 skill: {agent_skill}")
        body_lines.append("")
        body_lines.append("## 上下文")
        for k, v in context.items():
            body_lines.append(f"- {k}: {v}")
        body_lines.append("")
        body_lines.append("## 前置上下文（来自前一阶段）")
        if context.get("前置摘要"):
            body_lines.append(context["前置摘要"])
        else:
            body_lines.append("（无前置摘要 — 首个阶段或前置产物不存在）")
        body_lines.append("")
        body_lines.append("## 完成标准")
        body_lines.append("- 按要求产出所有产物文件")
        body_lines.append("- 文件格式符合 SDD 规范")
        body_lines.append("- 内容质量通过门禁检查")
        
        task_body = "\n".join(body_lines)
        
        # 验证 workspace 路径存在性（AC15/AC16）
        workspace_path = self.project_root.resolve()
        if not workspace_path.exists():
            print(f"❌ Workspace 路径不存在: {workspace_path}")
            return
        if not workspace_path.is_dir():
            print(f"❌ Workspace 路径不是目录: {workspace_path}")
            return

        # 创建 Kanban 任务（Kanban 调度器会自动 spawn Profile 对应的 Agent）
        import subprocess
        try:
            result = subprocess.run(
                ["hermes", "kanban", "create",
                 f"{change_id}: {state_name} 阶段",
                 "--assignee", profile,
                 "--body", task_body,
                 "--skill", agent_skill,
                 "--workspace", f"dir:{workspace_path}"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                # 提取 Task ID
                task_id = ""
                for line in result.stdout.split("\n"):
                    if "Task ID:" in line or "task_id:" in line:
                        task_id = line.split(":")[-1].strip()
                    elif "t_" in line:
                        import re
                        m = re.search(r'(t_\w+)', line)
                        if m:
                            task_id = m.group(1)

                print(f"✅ Kanban 任务已创建")
                print(f"   Task ID: {task_id}")
                print(f"")
                print(f"📋 调度器将自动执行: hermes -p {profile} chat -q 'work kanban task <id>'")
                print(f"   模型由 Profile 配置决定: {profile} 用自己的模型")
                print(f"")

                # C1: 轮询等待任务完成（最多重试 3 次，每次超时 3600s）
                print(f"⏳ 轮询等待任务完成...")
                max_retries = 3
                for attempt in range(max_retries):
                    print(f"   第 {attempt + 1}/{max_retries} 次轮询（间隔 5s）...")
                    status = self._poll_kanban_task(task_id, poll_interval=5, timeout=600)
                    print(f"   任务状态: {status}")

                    if status == "done":
                        print(f"✅ 任务完成！自动推进状态...")
                        # 确定下一个门禁状态
                        next_gate_states = {
                            State.PO_ENTRY: "PO_CHECK",
                            State.BA_ENTRY: "BA_CHECK",
                            State.ARCHITECT_ENTRY: "ARCHITECT_CHECK",
                            State.CODER_ENTRY: "CODER_CHECK",
                            State.REVIEWER_ENTRY: "REVIEWER_CHECK",
                            State.QA_ENTRY: "QA_CHECK",
                        }
                        next_gate = next_gate_states.get(state)
                        if next_gate:
                            self.transition(change_id, next_gate)
                        return
                    elif status == "blocked" and attempt < max_retries - 1:
                        print(f"🔄 任务阻塞，重试...")
                        continue
                    elif status == "blocked":
                        print(f"❌ 任务连续 {max_retries} 次阻塞，标记为 BLOCKED")
                        # 记录阻塞原因
                        state_data = self.load_state(change_id)
                        if state_data:
                            # 直接添加到 state_history
                            block_entry = StateHistoryEntry(
                                from_state=state.state_name,
                                to_state="BLOCKED",
                                at=datetime.utcnow().isoformat() + "Z",
                                trigger="auto",
                                auto=True,
                            )
                            state_data.state_history.append(block_entry)
                            state_data.current_state = "BLOCKED"
                            self.save_state(change_id, state_data)
                        return
                    else:
                        print(f"⏰ 任务超时（{status}），尝试重试...")
                        continue

                print(f"❌ 所有重试耗尽，任务未完成")
            else:
                print(f"❌ Kanban 任务创建失败: {result.stderr}")

        except Exception as e:
            print(f"❌ 创建任务异常: {e}")

    def prompt_user(self, change_id: str, state: State):
        """提示用户输入"""
        prompts = {
            State.PO_DONE: "PRD已完成，请说'继续'进入BA阶段",
            State.BA_DONE: "Spec已完成，请说'继续'进入Architect阶段",
            State.ARCHITECT_DONE: "Design和Tasks已完成，请说'开始编码'进入Coder阶段",
            State.USER_ACCEPT: "QA已通过，请说'归档'完成流程",
        }

        prompt = prompts.get(state, f"等待用户确认 ({state.state_name})")

        print(f"""
⏸️ 等待用户确认
━━━━━━━━━━━━━━━━━━━━
{prompt}
━━━━━━━━━━━━━━━━━━━━
""")

    def start(self, description: str, **flags) -> str:
        """启动新变更"""
        print(f"\n🚀 启动SDD流程: {description}")

        # 判定流程级别
        flow_level = self.determine_flow_level(description, flags)
        print(f"🔍 流程级别: {flow_level}")

        # 生成变更ID
        change_id = self.generate_change_id(description)
        print(f"📁 变更ID: {change_id}")

        # 创建目录
        change_dir = self.changes_dir / change_id
        change_dir.mkdir(parents=True, exist_ok=True)
        print(f"📂 创建目录: {change_dir}")

        # 初始化状态
        state = self.init_state_file(change_id, flow_level, description)
        self.save_state(change_id, state)
        print(f"📝 初始化状态文件")

        # 自动推进到PO_ENTRY
        self.transition(change_id, State.PO_ENTRY.state_name, trigger="sdd_start")

        return change_id

    def resume(self, change_id: Optional[str] = None):
        """恢复中断的变更"""
        if change_id:
            state = self.load_state(change_id)
            if not state:
                print(f"❌ 变更不存在: {change_id}")
                return

            print(f"""
🔄 恢复变更: {change_id}
━━━━━━━━━━━━━━━━━━━━
当前状态: {state.current_state}
流程级别: {state.flow_level}
开始时间: {state.started_at}
━━━━━━━━━━━━━━━━━━━━
""")

            current = State[state.current_state]

            if current.state_type == StateType.TERMINAL:
                print(f"✅ 变更已完成 ({current.state_name})")
            elif current.state_type == StateType.WAITING:
                self.prompt_user(change_id, current)
            elif current.state_type == StateType.EXECUTING:
                self.delegate_agent(change_id, current)
            else:
                print(f"⏳ 从 {current.state_name} 继续...")

        else:
            # 扫描所有进行中的变更
            print("\n📋 扫描进行中的变更...")
            for change_dir in self.changes_dir.iterdir():
                if change_dir.is_dir():
                    cid = change_dir.name
                    state = self.load_state(cid)
                    if state and State[state.current_state].state_type != StateType.TERMINAL:
                        print(f"  - {cid}: {state.current_state}")

    def status(self, change_id: Optional[str] = None):
        """显示状态"""
        if change_id:
            state = self.load_state(change_id)
            if not state:
                print(f"❌ 变更不存在: {change_id}")
                return

            print(f"""
📊 变更状态: {change_id}
━━━━━━━━━━━━━━━━━━━━
当前状态: {state.current_state}
上一状态: {state.previous_state or 'N/A'}
流程级别: {state.flow_level}
增量模式: {state.incremental_mode}

状态历史:
""")
            for h in state.state_history:
                auto_str = "(auto)" if h.auto else "(manual)"
                print(f"  {h.from_state} → {h.to_state} {auto_str}")

        else:
            print("\n📊 所有变更状态")
            for change_dir in sorted(self.changes_dir.iterdir()):
                if change_dir.is_dir():
                    cid = change_dir.name
                    state = self.load_state(cid)
                    if state:
                        status_icon = "✅" if State[state.current_state].state_type == StateType.TERMINAL else "⏳"
                        print(f"  {status_icon} {cid}: {state.current_state}")

    def do_audit(self, change_id: str):
        """输出模型使用审计报告（C3）"""
        state = self.load_state(change_id)
        if not state:
            print(f"❌ 变更不存在: {change_id}")
            return

        print(f"""
📊 模型使用审计报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
变更ID: {change_id}
总阶段数: {len(state.state_history)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        for i, entry in enumerate(state.state_history):
            model = entry.metadata.get("model", "N/A") if hasattr(entry, 'metadata') else "N/A"
            provider = entry.metadata.get("provider", "N/A") if hasattr(entry, 'metadata') else "N/A"
            print(f"  {i+1}. {entry.from_state} → {entry.to_state}")
            print(f"     触发: {'自动' if entry.auto else '手动'} | 时间: {entry.at[:19]}")

        # 显示专门的 audit 记录
        if state.model_audit:
            print(f"\n📋 详细审计记录:")
            for record in state.model_audit:
                print(f"  - 阶段: {record.get('stage')}")
                print(f"    模型: {record.get('model')}")
                print(f"    Provider: {record.get('provider')}")
                print(f"    Kanban任务: {record.get('kanban_task_id')}")
                print(f"    时间: {record.get('at')[:19]}")
                print("")

        # 模型一致性检查
        models_used = set(r.get("model") for r in state.model_audit if r.get("model"))
        if len(models_used) > 1:
            print(f"⚠️  使用了 {len(models_used)} 种不同模型: {', '.join(models_used)}")
        elif len(models_used) == 1:
            print(f"✅ 所有阶段使用同一模型: {list(models_used)[0]}")


def main():
    parser = argparse.ArgumentParser(description="SDD Orchestrator v2.1")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # start 命令
    start_parser = subparsers.add_parser("start", help="启动新变更")
    start_parser.add_argument("description", help="变更描述")
    start_parser.add_argument("--quick", action="store_true", help="Quick流程")
    start_parser.add_argument("--enhanced", action="store_true", help="Enhanced流程")

    # resume 命令
    resume_parser = subparsers.add_parser("resume", help="恢复变更")
    resume_parser.add_argument("change_id", nargs="?", help="变更ID")

    # status 命令
    status_parser = subparsers.add_parser("status", help="查看状态")
    status_parser.add_argument("change_id", nargs="?", help="变更ID")

    # transition 命令
    trans_parser = subparsers.add_parser("transition", help="手动状态转换")
    trans_parser.add_argument("change_id", help="变更ID")
    trans_parser.add_argument("target_state", help="目标状态")
    trans_parser.add_argument("--skip-delegate", action="store_true",
                            help="跳过Agent委托和轮询（用于存量任务/手动归档场景）")

    # audit 命令（C3）
    audit_parser = subparsers.add_parser("audit", help="模型使用审计")
    audit_parser.add_argument("change_id", help="变更ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    orchestrator = SDDOrchestrator()

    if args.command == "start":
        flags = {"quick": args.quick, "enhanced": args.enhanced}
        change_id = orchestrator.start(args.description, **flags)
        print(f"\n✅ 变更已启动: {change_id}")

    elif args.command == "resume":
        orchestrator.resume(args.change_id)

    elif args.command == "status":
        orchestrator.status(args.change_id)

    elif args.command == "transition":
        skip_delegate = getattr(args, 'skip_delegate', False)
        success = orchestrator.transition(args.change_id, args.target_state, trigger="manual", skip_delegate=skip_delegate)
        if success:
            print(f"\n✅ 转换完成")
        else:
            print(f"\n❌ 转换失败")
            sys.exit(1)

    elif args.command == "audit":
        orchestrator.do_audit(args.change_id)

if __name__ == "__main__":
    main()
