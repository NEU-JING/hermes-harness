# Profile 配置与使用指南

> **文档版本**：2.3.0  
> **最后更新**：2026-06-16

---

## 目录

1. [架构概述](#架构概述)
2. [快速开始](#快速开始)
3. [Profile 配置](#profile-配置)
4. [Soul 模式](#soul-模式)
5. [验证工具](#验证工具)
6. [常见问题](#常见问题)
7. [最佳实践](#最佳实践)

---

## 架构概述

### 什么是 Profile？

Profile 是 Hermes Agent 的配置隔离机制，每个 Profile 有独立的：
- 模型配置
- Provider 配置
- Skill 集
- 思维特质（Soul）

### Profile + Soul 架构

```
┌─────────────────────────────────────┐
│        AGENTS.md（单一真相源）       │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│    init-profiles.sh（模板生成器）   │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│     ~/.hermes/profiles/             │
│  ┌─────────┐ ┌─────────┐ ┌───────┐ │
│  │ sdd-po  │ │ sdd-ba  │ │ ...   │ │
│  │ config  │ │ config  │ │       │ │
│  │ SOUL.md │ │ SOUL.md │ │       │ │
│  └─────────┘ └─────────┘ └───────┘ │
└─────────────────────────────────────┘
```

---

## 快速开始

### 1. 初始化 Profile

```bash
# 克隆项目
git clone https://github.com/NEU-JING/hermes-harness.git
cd hermes-harness

# 初始化 Profile
./scripts/init-profiles.sh
```

### 2. 验证安装

```bash
# 检查 Profile 列表
./scripts/validate-profile-isolation.sh

# 检查 Soul 文件
./scripts/validate-soul-injection.sh

# 检查 Workspace
./scripts/validate-workspace-binding.sh
```

### 3. 开始使用

```bash
# 使用 SDD 流程
hermes chat -q "用 SDD 流程开发一个待办事项应用"
```

---

## Profile 配置

### 配置文件位置

每个 Profile 的配置文件位于：
```
~/.hermes/profiles/<profile-name>/config.yaml
```

### 配置示例

```yaml
# ~/.hermes/profiles/sdd-reviewer/config.yaml
models:
  default:
    provider: deepseek
    model: deepseek-v4-pro

skills:
  external_dirs:
    - /path/to/hermes-harness/skills
```

### 修改 Profile 配置

1. 编辑对应 Profile 的 `config.yaml`
2. 重启 Hermes 会话生效
3. 使用 `hermes -p <profile-name>` 测试

---

## Soul 模式

### 什么是 Soul？

Soul 是每个 Profile 的思维特质定义文件，位于：
```
~/.hermes/profiles/<profile-name>/SOUL.md
```

### SOUL.md 结构

```markdown
# <Profile 名称>

## 核心思维模式
- 思维特质 1
- 思维特质 2

## 角色原则
- 原则 1
- 原则 2

## 禁止事项
- ❌ 禁止行为 1
- ❌ 禁止行为 2
```

### 示例：sdd-reviewer

```markdown
# sdd-reviewer（代码评审专家）

## 核心思维模式
1. 批判性思维：假设代码有问题，直到证明它没问题
2. 开发者视角切换："如果我来维护这段代码，我会遇到什么坑？"

## 评审原则
- 对事不对人：评价代码，不评价开发者
- 给出具体建议：不只说"不好"，要说"怎么更好"
- 解释为什么：说明这样改的理由

## 禁止事项
- ❌ 不做风格自行车棚争论
- ❌ 不要求"完美"，只要求"可接受"
```

---

## 验证工具

### 1. validate-profile-isolation.sh

检查每个 Profile 的独立性：

```bash
./scripts/validate-profile-isolation.sh
```

检查项目：
- 目录存在性
- 配置文件存在性
- Skills 目录存在性
- external_dirs 配置

### 2. validate-soul-injection.sh

检查每个 Profile 的 Soul 文件：

```bash
./scripts/validate-soul-injection.sh
```

检查项目：
- SOUL.md 文件存在性
- 关键章节（核心思维模式/角色原则/禁止事项）
- 关键词覆盖率

### 3. validate-workspace-binding.sh

检查 Workspace 配置：

```bash
./scripts/validate-workspace-binding.sh
```

检查项目：
- 项目根目录存在性
- docs/ 目录存在性
- skills/ 目录存在性
- AGENTS.md 存在性

---

## 常见问题

### Q: 如何更新 Profile？

A: 使用 `--force` 选项重新初始化：
```bash
./scripts/init-profiles.sh --force
```

### Q: 如何禁用 Soul 模式？

A: 重命名或删除 SOUL.md 文件：
```bash
mv ~/.hermes/profiles/sdd-po/SOUL.md ~/.hermes/profiles/sdd-po/SOUL.md.disabled
```

### Q: 如何自定义模型？

A: 编辑对应 Profile 的 `config.yaml`：
```yaml
models:
  default:
    provider: custom-provider
    model: custom-model
```

### Q: 如何添加新的 Profile？

A: 
1. 在 AGENTS.md 中添加配置
2. 使用 `hermes profile create <name>` 创建
3. 配置 SOUL.md 和 config.yaml

### Q: Profile 之间会互相影响吗？

A: 不会！每个 Profile 完全隔离，有独立的配置和状态。

---

## 最佳实践

1. **使用 AGENTS.md 作为单一真相源**：所有 Profile 配置在 AGENTS.md 中定义
2. **定期验证**：使用验证脚本检查 Profile 状态
3. **版本控制**：将 AGENTS.md 提交到 Git
4. **备份配置**：定期备份 ~/.hermes/profiles/ 目录
5. **测试变更**：在测试 Profile 上先验证再推广
