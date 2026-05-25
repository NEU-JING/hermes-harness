# 安装指南

## 前置条件

- **Hermes Agent >= v2.0**：确认方法：终端输入 `hermes --version`

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/NEU-JING/hermes-harness.git
cd hermes-harness
```

### 2. 运行安装脚本

```bash
./install.sh
```

脚本会将 `skills/sdd/` 目录复制到 `~/.hermes/skills/sdd/`。

### 3. 验证安装

```bash
ls ~/.hermes/skills/sdd/
```

预期输出：

```
architect-agent  ba-agent  coder-agent  po-agent  qa-agent
reviewer-agent   sdd-init  sdd-orchestrator  sdd-structure-lint  shared
```

### 4. 初始化你的项目

```bash
cd /path/to/your-project
# 对 Hermes Agent 说："初始化 SDD"
```

## 卸载

```bash
rm -rf ~/.hermes/skills/sdd/
```

## 升级

```bash
cd hermes-harness
git pull
./install.sh
```

> install.sh 幂等：已有安装时会提示跳过，不会自动覆盖。如需强制重装请先卸载。

## 常见问题

**Q: 安装后 Hermes Agent 不识别 Skill？**
A: 检查 `~/.hermes/config.yaml` 中 `skills_dir` 是否指向 `~/.hermes/skills`。新会话重启生效。

**Q: install.sh 提示"已有安装"？**
A: 你之前装过。如需重装：`rm -rf ~/.hermes/skills/sdd/ && ./install.sh`
