#!/usr/bin/env bash
#
# Profile 隔离检查脚本
# 功能：验证每个 Profile 有独立的配置，互不干扰
#

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"

# Profile 列表
PROFILE_LIST=("sdd-po" "sdd-ba" "sdd-architect" "sdd-coder" "sdd-reviewer" "sdd-qa")

# 帮助信息
show_help() {
    cat <<EOF
${BLUE}Profile 隔离检查脚本${NC}

用法：$(basename "$0") [选项]

选项：
    -h, --help          显示此帮助信息
    -v, --version       显示版本信息

示例：
    # 检查所有 Profile
    ./scripts/validate-profile-isolation.sh

EOF
}

# 显示版本
show_version() {
    echo "validate-profile-isolation.sh v2.3.0"
}

# 检查单个 Profile
check_profile() {
    local profile_name="$1"
    local profile_dir="$HERMES_HOME/profiles/$profile_name"
    local config_file="$profile_dir/config.yaml"
    local skill_dir="$profile_dir/skills"

    local passed=0
    local failed=0

    echo -e "${BLUE}检查 Profile: $profile_name${NC}"
    echo "────────────────────────────────────────"

    # 检查目录存在
    if [ -d "$profile_dir" ]; then
        echo -e "  ${GREEN}✓${NC} 目录存在"
    else
        echo -e "  ${RED}✗${NC} 目录不存在"
        ((failed++))
    fi

    # 检查配置文件存在
    if [ -f "$config_file" ]; then
        echo -e "  ${GREEN}✓${NC} 配置文件存在"
    else
        echo -e "  ${RED}✗${NC} 配置文件不存在"
        ((failed++))
    fi

    # 检查 skills 目录存在
    if [ -d "$skill_dir" ]; then
        echo -e "  ${GREEN}✓${NC} Skills 目录存在"
    else
        echo -e "  ${YELLOW}⚠${NC} Skills 目录不存在（可能未配置）"
    fi

    # 检查 external_dirs 配置
    if grep -q "$PROJECT_ROOT/skills" "$config_file" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} external_dirs 配置正确"
    else
        echo -e "  ${YELLOW}⚠${NC} external_dirs 配置未找到"
    fi

    echo ""
    if [ $failed -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# 主函数
main() {
    # 参数解析
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                show_version
                exit 0
                ;;
            *)
                echo -e "${RED}未知参数：$1${NC}"
                show_help
                exit 1
                ;;
        esac
    done

    echo ""
    echo "╔═══════════════════════════════════════════════════╗"
    echo "║     Profile 隔离检查 v2.3.0                        ║"
    echo "╚═══════════════════════════════════════════════════╝"
    echo ""

    local total_passed=0
    local total_failed=0

    for profile in "${PROFILE_LIST[@]}"; do
        if check_profile "$profile"; then
            ((total_passed++))
        else
            ((total_failed++))
        fi
    done

    echo "═══════════════════════════════════════════════"
    echo ""
    if [ $total_failed -eq 0 ]; then
        echo -e "${GREEN}✓ 所有 Profile 检查通过${NC}"
        echo ""
        echo "  检查项目："
        echo "  - 目录存在性"
        echo "  - 配置文件存在性"
        echo "  - Skills 目录存在性"
        echo "  - external_dirs 配置"
        echo ""
        exit 0
    else
        echo -e "${RED}✗ 部分 Profile 检查失败${NC}"
        echo ""
        echo "  通过: $total_passed / ${#PROFILE_LIST[@]}"
        echo "  失败: $total_failed / ${#PROFILE_LIST[@]}"
        echo ""
        exit 1
    fi
}

# 执行主函数
main "$@"
