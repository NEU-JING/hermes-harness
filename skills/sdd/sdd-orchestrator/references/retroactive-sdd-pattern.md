# Retroactive SDD Documentation Pattern

> **Pattern**: When code is already implemented, apply full SDD process retroactively
> **Date**: 2026-05-30 (SDD 006-orchestrator-v2)

---

## Scenario

**Problem**: Change was already implemented and committed, but full SDD documentation doesn't exist.

**Example**: sdd-orchestrator v2.0 was coded and committed as `5fbb86b` before PRD/Spec/Design existed.

---

## Solution: Retroactive SDD Process

### Phase 1: Document What Was Built

Create the SDD artifacts **based on actual implementation** (reverse engineer):

| Document | Approach | Source |
|:---|:---|:---|
| PRD | Describe problems solved, goals achieved | Commit message + code changes |
| Spec | Extract AC from implementation | Code behavior + test cases |
| Design | Document architecture decisions | Code structure + state machine |
| Tasks | List actual work done | Git commits + file changes |

### Phase 2: Review Against Implementation

**Self-review checklist**:
- [ ] Does Design match actual code structure?
- [ ] Do AC cover implemented behavior?
- [ ] Are Tasks accurate to commits?

### Phase 3: Fix Discrepancies

If review finds gaps:
1. Document as "known limitations" OR
2. Create follow-up change to fix

### Phase 4: Complete SDD Lifecycle

Proceed normally:
```
completion-report → review-report → qa-report → archive
```

---

## Example: 006-orchestrator-v2

**Already existed**:
- Commit `5fbb86b`: feat(orchestrator): v2.0重构
- 13 files changed, 4600+ lines
- All code implemented

**Retroactive SDD**:
```
1. Created docs/changes/006-orchestrator-v2/
2. Wrote PRD: Described v1.0 problems → v2.0 solutions
3. Wrote Spec: 8 requirements, 17 ACs based on implementation
4. Wrote Design: Documented 18-state machine already in code
5. Wrote Tasks: 10 tasks matching actual work done
6. Self-Review: Found integration documentation gaps
7. Fixed: Added Integration Notes to SKILL.md
8. QA: Verified all AC covered
9. Archived: Moved to docs/archive/
```

---

## Key Differences from Normal SDD

| Aspect | Normal SDD | Retroactive SDD |
|:---|:---|:---|
| Document source | Design first, then implement | Implement first, then document |
| PRD timing | Before coding | After coding |
| Spec timing | Before coding | After coding |
| Design timing | Before coding | After coding |
| Changes during process | Design → implement | Document → fix gaps → archive |
| Review focus | "Will this work?" | "Does this match reality?" |

---

## When to Use This Pattern

**Appropriate**:
- Hotfixes that couldn't wait for SDD
- Emergency patches
- Proof-of-concepts that graduated to production
- Legacy code being formalized

**Not appropriate**:
- New features (use normal SDD)
- Complex architectural changes (design-first needed)
- Multi-person collaboration (sync issues)

---

## Risk Mitigation

| Risk | Mitigation |
|:---|:---|
| Documentation drift | Strict self-review against code |
| Missing AC | Code coverage analysis |
| Design fiction | Verify every claim against implementation |
| No user validation | Acknowledge in PRD "已部署，用户反馈待收集" |

---

## Signal Phrases

User might request this pattern with:
- "补走一下SDD流程"
- "这个变更已经实现了，补一下文档"
- "归档一下这个变更"
- "补个PRD/Spec"

---

## Output Checklist

Retroactive SDD is complete when:
- [ ] All 7 documents exist (PRD/Spec/Design/Tasks/Completion/Review/QA)
- [ ] Documents match actual implementation
- [ ] Known gaps documented
- [ ] Review passes
- [ ] QA passes
- [ ] Archived to docs/archive/{id}/
- [ ] Current/基线 updated
