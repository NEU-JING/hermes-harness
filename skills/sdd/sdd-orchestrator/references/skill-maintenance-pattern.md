# Skill Maintenance Pattern

> **Session**: 007-orchestrator-refine  
> **Date**: 2026-05-30  
> **Version**: 2.0.1

---

## Content Deduplication Strategy

### Problem
SKILL.md and references/ had overlapping content, making maintenance difficult.

### Solution
Adopt a **summary + details** architecture:

| File | Purpose | Content Type |
|:---|:---|:---|
| `SKILL.md` | Entry point, quick reference | Summary, tables, ASCII diagrams, links |
| `references/*.md` | Detailed specifications | Full state definitions, checklists, protocols |

### Migration Pattern

When content exists in both places:

1. **Keep in SKILL.md**:
   - Overview and key concepts
   - State transition tables
   - ASCII flow diagrams
   - Quick reference lists
   - Links to references/

2. **Move to references/**:
   - Detailed state definitions (entry/execution/exit conditions)
   - Exhaustive checklists
   - Multi-step protocols
   - Error handling details
   - Code examples longer than 20 lines

### Size Target

- SKILL.md should be **< 400 lines**
- Target reduction: **25-30%** from monolithic version
- Use relative links: `[details](./references/xxx.md)`

---

## Anti-Deviation Pattern

### Problem
Agents might "跑偏" (deviate) by using wrong skills or missing context when delegating tasks.

### Solution
**Mandatory `skill_view()` before `kanban create()`**

```python
# 1. Pre-delegation: Load skill explicitly
def pre_delegation_check(agent_type: str, change_id: str):
    skill_name = f"{agent_type}-agent"
    skill_info = skill_view(name=skill_name)
    
    if not skill_info.success:
        return PreCheckResult(
            success=False,
            error=f"无法加载技能: {skill_name}",
            blocking=True
        )
    return PreCheckResult(success=True, skill_info=skill_info)

# 2. Execute delegation only after skill loaded
result = kanban create(...)
```

### Skill Mapping

| Phase | Required Skill | View Command |
|:---|:---|:---|
| PO | po-agent | `skill_view(name='po-agent')` |
| BA | ba-agent | `skill_view(name='ba-agent')` |
| Architect | architect-agent | `skill_view(name='architect-agent')` |
| Coder | coder-agent | `skill_view(name='coder-agent')` |
| Reviewer | reviewer-agent | `skill_view(name='reviewer-agent')` |
| QA | qa-agent | `skill_view(name='qa-agent')` |
| Lint | sdd-structure-lint | `skill_view(name='sdd-structure-lint')` |

### Failure Handling

If `skill_view()` fails:
1. Block the flow (transition to BLOCKED state)
2. Record the error
3. Provide recovery instructions
4. Require user intervention to resume

---

## Verification Checklist

When updating this skill:

- [ ] SKILL.md line count < 400
- [ ] All references/ links are valid
- [ ] Each phase has `skill_view()` example
- [ ] Anti-deviation pattern documented
- [ ] Version number updated in frontmatter
