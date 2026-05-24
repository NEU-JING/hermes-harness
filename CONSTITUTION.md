# CONSTITUTION.md — Hermes SDD

> 项目宪法。SDD 编排器在每个阶段检查合规性。

## 代码原则

1. **TDD 强制**：所有可测试的功能代码必须先写测试
2. **测试自包含**：测试不依赖预置数据或外部状态
3. **Pre-commit 强制**：所有代码提交前必须通过 format + lint

## 架构原则

1. **Skill 即模块**：每个 Skill 职责单一，接口清晰（SKILL.md YAML frontmatter）
2. **简洁优先**：能用简单指令的不引入复杂机制
3. **参考即模板**：references/ 目录文件可直接作为 Agent 的输入模板

## 协作原则

1. **文档驱动**：先写 Spec，再写代码
2. **评审必做**：代码合并前必须 Review
3. **增量提交**：每 Task 一个 commit

## 项目特有约束

- Skills 产出路径：开发期 `skills/sdd/`，部署期 `~/.hermes/skills/sdd/`
- SKILL.md 必须符合 hermes-agent-skill-authoring 规范
- 共享文件（shared/）不含 YAML frontmatter，为纯参考文档
