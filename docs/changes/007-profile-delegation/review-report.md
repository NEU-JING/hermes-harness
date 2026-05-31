# Review Report — 007: Profile Delegation

> **变更 ID**: `007-profile-delegation`
> **评审日期**: 2026-05-31
> **评审人**: Reviewer Agent (sdd-reviewer)
> **评审范围**: 8 个文件的完整变更（7 修改 + 1 新建）
> **评审结论**: ⚠️ **有条件通过**（1 CRITICAL, 2 MAJOR, 2 MINOR）

---

## 评审结论

**有条件通过** — 存在 1 个 CRITICAL 问题（AC10 向后兼容性违反），需返回 Coder 修复后重新评审。2 个 MAJOR 问题和 2 个 MINOR 问题可在 QA 阶段同步修复。

| 评审阶段 | 结果 | 严重问题数 |
|---------|:----:|:---------:|
| Phase 1 — Spec 合规 | ⚠️ 有条件通过 | 1 CRITICAL |
| Phase 2 — 代码质量 | ⚠️ 有条件通过 | 2 MAJOR, 2 MINOR |
| Phase 3 — 架构一致性 | ✅ 通过 | 0 |

---

## Phase 1 — Spec 合规检查

### AC 覆盖矩阵

| AC | 描述 | 验证结果 | 说明 |
|:---:|------|:---:|------|
| AC1 | sdd-flash Profile 规格（file,skills） | ✅ | setup-sdd-profiles.sh / delegate-protocol.md / SKILL.md 三处一致 |
| AC2 | sdd-pro Profile 规格（file,terminal,skills,github） | ✅ | 同上三处一致验证通过 |
| AC3 | sdd-reviewer Profile 规格（file,terminal,skills,github） | ✅ | 同上三处一致验证通过 |
| AC4 | PO 委托使用 sdd-flash | ✅ | delegate-protocol.md + ROLE_TO_PROFILE_DEFAULT 一致 |
| AC5 | BA 委托使用 sdd-flash | ✅ | delegate-protocol.md + ROLE_TO_PROFILE_DEFAULT 一致 |
| AC6 | Architect 委托使用 sdd-pro | ✅ | delegate-protocol.md + ROLE_TO_PROFILE_DEFAULT 一致 |
| AC7 | Coder 委托使用 sdd-pro | ✅ | delegate-protocol.md + ROLE_TO_PROFILE_DEFAULT 一致 |
| AC8 | Reviewer 委托使用 sdd-reviewer | ✅ | delegate-protocol.md + ROLE_TO_PROFILE_DEFAULT 一致 |
| AC9 | QA 委托使用 sdd-flash | ✅ | delegate-protocol.md + ROLE_TO_PROFILE_DEFAULT 一致 |
| **AC10** | **无配置保持向后兼容** | **❌ CRITICAL** | **见下方详细分析** |
| AC11 | Profile 不存在回退警告 | ✅ | get_profile_for_role() 正确输出 WARNING 并返回 None |
| AC12 | AGENTS.md 覆盖生效 | ✅ | load_profile_mapping() 解析逻辑正确（regex 匹配） |
| AC13 | 工具集最小化验证 | ✅ | sdd-flash 仅 file,skills，不含 terminal/github |
| AC14 | sdd-rules.md 默认映射 ≤ 20 行 | ✅ | ROLE_TO_PROFILE_DEFAULT 段共 13 行 |
| AC15 | orchestrator SKILL.md version: 2.1.0 | ✅ | frontmatter + 标题均为 v2.1.0 |

**覆盖率**: 14/15 AC 通过 (93.3%)

---

### ❌ CRITICAL #1: AC10 — 向后兼容性违反

| 维度 | 详细 |
|------|------|
| **严重级别** | CRITICAL |
| **涉及文件** | `skills/sdd/sdd-orchestrator/scripts/orchestrator.py` |
| **涉及方法** | `load_profile_mapping()` (line 277-312) + `get_profile_for_role()` (line 314-334) |
| **违反的 AC** | AC10 |
| **违反的 Spec 条款** | R5: "AGENTS.md 无 role_to_profile 配置时，整个系统保持变更前行为不变" |

**问题描述**：

`load_profile_mapping()` 总是返回完整的默认映射（`ROLE_TO_PROFILE_DEFAULT`），不区分「AGENTS.md 有 opt-in 配置」和「AGENTS.md 无配置」两种场景。当用户已通过 `setup-sdd-profiles.sh` 创建了 3 个 Profile，但 AGENTS.md 未启用 `sdd_config.role_to_profile`（当前 AGENTS.md 中该段全部为注释）时，`get_profile_for_role()` 仍会找到 Profile 名称，`_check_profile_exists()` 返回 `True`，最终 `delegate_agent()` 会携带 `profile` 参数。

这与 Spec 的明确要求冲突：

> **Spec 数据模型设计说明**：「当 AGENTS.md 无覆盖时不启用 Profile 模式（保持完全向后兼容）；当 AGENTS.md 主动声明 `sdd_config.role_to_profile` 时，与默认映射浅合并，覆盖指定角色。」

> **Design 3.8 向后兼容策略**：「AGENTS.md 是否有 sdd_config.role_to_profile? → NO → 不启用 Profile 模式」

**当前代码路径**：
```
AGENTS.md 无 active role_to_profile
  → load_profile_mapping() 返回完整默认映射 (6 条目)
  → get_profile_for_role("po") → "sdd-flash"
  → _check_profile_exists("sdd-flash") → True（Profile 已创建）
  → delegate_task 携带 profile: "sdd-flash"  ❌ 违反 AC10
```

**修复建议**：

在 `load_profile_mapping()` 中增加「是否检测到 active opt-in」的判断逻辑：

```python
def load_profile_mapping(self) -> Dict[str, str]:
    """加载合并后的 role→profile 映射。若无 AGENTS.md opt-in，返回空映射。"""
    mapping = dict(self.ROLE_TO_PROFILE_DEFAULT)
    has_opt_in = False

    agents_path = self.project_root / "AGENTS.md"
    if agents_path.exists():
        try:
            content = agents_path.read_text()
            in_section = False
            for line in content.split("\n"):
                if "role_to_profile:" in line and not line.strip().startswith("#"):
                    in_section = True
                    has_opt_in = True
                    continue
                if in_section:
                    # ... existing parsing logic ...
            
            if not has_opt_in:
                return {}  # 无 opt-in → 空映射 → 不启用 Profile
        except Exception as e:
            print(f"⚠️  解析 AGENTS.md 失败: {e}，使用默认映射")
    
    return mapping
```

或者，在 `get_profile_for_role()` 入口增加 gating 检查：
```python
def get_profile_for_role(self, role: str) -> Optional[str]:
    if not self._has_agents_md_opt_in():
        return None  # 无 opt-in → 直接回退
    # ... existing logic ...
```

---

## Phase 2 — 代码质量检查

### MAJOR #2: orchestrator.py:191 — 初始化版本号未更新

| 维度 | 详细 |
|------|------|
| **严重级别** | MAJOR |
| **文件** | `skills/sdd/sdd-orchestrator/scripts/orchestrator.py` |
| **行号** | 191 |
| **代码** | `"orchestrator_version": "2.0.0"` |

`init_state_file()` 方法中硬编码版本号为 `"2.0.0"`，未同步更新为 `"2.1.0"` 或使用 `self.VERSION` 常量（已在 line 155 定义为 `"2.1.0"`）。新创建的 `.sdd-state.json` 会显示错误的编排器版本。

**修复建议**：
```python
# 改为使用 VERSION 常量
"orchestrator_version": self.VERSION,
```

---

### MAJOR #3: orchestrator.py:677 — CLI 描述版本号未更新

| 维度 | 详细 |
|------|------|
| **严重级别** | MAJOR |
| **文件** | `skills/sdd/sdd-orchestrator/scripts/orchestrator.py` |
| **行号** | 677 |
| **代码** | `description="SDD Orchestrator v2.0"` |

`main()` 函数的 argparse 描述仍为 `"v2.0"`，应为 `"v2.1"`。`--help` 输出会显示错误的版本号。

**修复建议**：
```python
parser = argparse.ArgumentParser(description="SDD Orchestrator v2.1")
```

---

### MINOR #4: AGENTS.md 解析器匹配注释行

| 维度 | 详细 |
|------|------|
| **严重级别** | MINOR |
| **文件** | `skills/sdd/sdd-orchestrator/scripts/orchestrator.py` |
| **行号** | 295 |
| **代码** | `if "role_to_profile:" in line:` |

当前判断未排除注释行。AGENTS.md 中的 `#   role_to_profile:`（注释行）也会触发 `in_section = True`。虽然后续的 `line.startswith("#")` 检查会跳过注释行的内容解析，但 `in_section` 会被错误地设为 `True`。当前 AGENTS.md 结构下无害（因为紧跟着的映射行也都是注释），但如果未来文档结构调整可能产生意外行为。

**修复建议**：
```python
if "role_to_profile:" in line and not line.strip().startswith("#"):
    in_section = True
    continue
```

---

### MINOR #5: AGENTS.md 解析器空行退出策略

| 维度 | 详细 |
|------|------|
| **严重级别** | MINOR |
| **文件** | `skills/sdd/sdd-orchestrator/scripts/orchestrator.py` |
| **行号** | 299-301 |
| **代码** | `if line.strip() == "": in_section = False` |

解析器在遇到空行时退出 `role_to_profile` 段。这对单一块配置正常，但若用户配置中包含空行分隔的多个映射组（虽然当前格式不要求），解析会提前终止。当前格式下无害，属防御性编程建议。

**修复建议**：考虑使用缩进级别检测替代空行检测，或至少记录此限制在注释中。

---

## Phase 3 — 架构一致性检查

| 检查项 | 结果 | 说明 |
|--------|:---:|------|
| 模块划分与 Design 一致 | ✅ | 4 层架构（规则定义/编排器内核/初始化配置/数据模型）全部正确实现 |
| 接口定义与 Design 一致 | ✅ | `load_profile_mapping()`, `get_profile_for_role()`, `_check_profile_exists()` 签名匹配 Design 3.4 |
| 数据流与 Design 一致 | ✅ | delegate_agent → get_profile_for_role → load_profile_mapping → _check_profile_exists 路径正确 |
| Profile 字段位置合规 | ✅ | 所有 7 处 YAML `profile` 字段均在 `goal` 之后、`context` 之前 |
| STATE_ROLE_MAP 完整 | ✅ | 6 个角色全部映射（po/ba/architect/coder/reviewer/qa） |
| ROLE_TO_PROFILE_DEFAULT 完整 | ✅ | 6 个角色全部映射，值正确 |
| setup-sdd-profiles.sh 匹配设计 | ✅ | 3 Profile 创建参数与 Design 3.6 一致，幂等设计正确 |
| sdd-init 升级步骤 | ✅ | Step B4.x 完整覆盖 Profile 检测、创建、降级处理 |
| sdd-state-schema.md 扩展 | ✅ | profile + profile_history 字段正确添加，字段说明完整 |
| delegate-protocol.md 旧引用清除 | ✅ | 无 sdd-po/sdd-ba 等旧 6-Profile 名称残留 |
| 向后兼容策略 | ⚠️ | 策略框架正确但实现有偏差（见 CRITICAL #1） |

**架构一致性结论**: ✅ 通过（1 个已在上方 CRITICAL 中覆盖的实现偏差）

---

## 问题清单汇总

| # | 严重级别 | 文件 | 行号 | 问题描述 | 修复建议 |
|---|:---:|------|:---:|---------|---------|
| 1 | **CRITICAL** | orchestrator.py | 277-334 | AC10 向后兼容违反：无 AGENTS.md opt-in 时仍启用 Profile | 增加 `has_opt_in` 判断，无 opt-in 时返回空映射 |
| 2 | MAJOR | orchestrator.py | 191 | 初始化版本号 `"2.0.0"` 未同步 | 改为 `self.VERSION` |
| 3 | MAJOR | orchestrator.py | 677 | CLI argparse 描述 `"v2.0"` 未更新 | 改为 `"v2.1"` |
| 4 | MINOR | orchestrator.py | 295 | AGENTS.md 解析器匹配注释行 | 增加 `not line.strip().startswith("#")` |
| 5 | MINOR | orchestrator.py | 299 | 空行退出策略不够健壮 | 建议使用缩进级别检测 |

---

## 语法验证

| 文件 | 类型 | 结果 |
|------|:---:|:---:|
| orchestrator.py | Python 3 | ✅ `ast.parse()` 通过 |
| setup-sdd-profiles.sh | Bash | ✅ `bash -n` 通过 |

---

## 附录：变更文件清单

| # | 文件 | 操作 | 行数 | 状态 |
|---|------|:---:|:---:|:---:|
| 1 | `skills/sdd/shared/sdd-rules.md` | MODIFY | +13 | ✅ |
| 2 | `AGENTS.md` | MODIFY | +11 | ✅ |
| 3 | `skills/sdd/sdd-orchestrator/SKILL.md` | MODIFY | 版本 2.0.3→2.1.0 | ✅ |
| 4 | `skills/sdd/sdd-orchestrator/references/delegate-protocol.md` | MODIFY | 版本 2.0.2→2.1.0 | ✅ |
| 5 | `skills/sdd/sdd-orchestrator/scripts/orchestrator.py` | MODIFY | +~120 行 | ⚠️ 3 问题 |
| 6 | `skills/sdd/sdd-init/SKILL.md` | MODIFY | +31 行 (B4.x) | ✅ |
| 7 | `scripts/setup-sdd-profiles.sh` | **NEW** | 72 行 | ✅ |
| 8 | `skills/sdd/shared/sdd-state-schema.md` | MODIFY | +15 行 | ✅ |

---

## 下一步行动

1. **必须修复** CRITICAL #1：增加 opt-in gating 逻辑
2. **应修复** MAJOR #2, #3：同步版本号
3. **建议修复** MINOR #4, #5：增强解析器健壮性
4. 修复后重新运行 Reviewer Agent 验证

---

*报告由 Reviewer Agent (sdd-reviewer) 生成，遵循三阶段评审流程。*
