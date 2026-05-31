#!/bin/bash
# setup-sdd-profiles.sh — 创建 SDD v2.1.0 所需的 3 个 Hermes Profile
# 用法: bash scripts/setup-sdd-profiles.sh
# 幂等：已存在的 Profile 跳过创建
# 需要 Hermes v2.1.0+

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "=== SDD Profile Setup (v2.1.0) ==="
echo ""

# 检查 hermes 命令
if ! command -v hermes &> /dev/null; then
    echo -e "${RED}❌ hermes 命令不可用${NC}"
    echo "   请安装 Hermes v2.1.0+: https://hermes-agent.nousresearch.com/docs"
    exit 1
fi

HERMES_VERSION=$(hermes --version 2>/dev/null | grep -oP 'v?\K\d+\.\d+' | head -1 || echo "0.0")
echo "📋 Hermes 版本: ${HERMES_VERSION}"

create_profile() {
    local name=$1
    local model=$2
    local tools=$3

    if hermes profile list 2>/dev/null | grep -q "$name"; then
        echo -e "   ${YELLOW}⏭️${NC}  Profile '${name}' 已存在，跳过"
        return 0
    fi

    echo -e "   ${GREEN}📁${NC} 创建 Profile: ${name}"
    if hermes profile create "$name" --model "$model" --tools "$tools" 2>/dev/null; then
        echo -e "   ${GREEN}✅${NC} Profile '${name}' 创建成功"
    else
        echo -e "   ${RED}❌${NC} Profile '${name}' 创建失败"
        return 1
    fi
}

echo ""
echo "创建 SDD Profiles..."
echo ""

# sdd-flash: 文档密集型 (PO/BA/QA)
create_profile "sdd-flash" \
    "deepseek/deepseek-v4-flash" \
    "file,skills" || true

# sdd-pro: 编码密集型 (Architect/Coder)
create_profile "sdd-pro" \
    "deepseek/deepseek-v4-pro" \
    "file,terminal,skills,github" || true

# sdd-reviewer: 独立评审 (Reviewer)
create_profile "sdd-reviewer" \
    "deepseek/deepseek-v4-pro" \
    "file,terminal,skills,github" || true

echo ""
echo "=== Profile 创建摘要 ==="
hermes profile list 2>/dev/null | grep "sdd-" || echo "(无 sdd- Profile)"
echo ""
echo "✅ SDD Profile 设置完成"
echo ""
echo "下一步：在 AGENTS.md 中配置 sdd_config.role_to_profile 以启用 Profile 委托"
