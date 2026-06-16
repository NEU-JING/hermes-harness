#!/usr/bin/env bash
#
# Workspace 绑定验证脚本
# 功能：验证 workspace 路径配置正确
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

# 帮助信息
show_help() {
    cat <<EOF
${BLUE}Workspace 绑定验证脚本${NC}

用法：$(basename "$0") [选项]

选项：
    -h, --help          显示此帮助信息
    -v, --version       显示版本信息

示例：
    # 验证 workspace
    ./scripts/validate-workspace-binding.sh

EOF
}

# 显示版本
show_version() {
    echo "validate-workspace-binding.sh v2.3.0"
}

# 检查项目目录结构
check_project_structure() {
    echo -e "${BLUE}检查项目目录结构${NC}"
    echo "────────────────────────────────────────"

    local passed=0
    local failed=0

    # 检查项目根目录
    if [ -d "$PROJECT_ROOT" ]; then
        echo -e "  ${GREEN}✓${NC} 项目根目录存在: $PROJECT_ROOT"
    else
        echo -e "  ${RED}✗${NC} 项目根目录不存在"
        ((failed++))
    fi

    # 检查 docs/ 目录
    if [ -d "$PROJECT_ROOT/docs" ]; then
        echo -e "  ${GREEN}✓${NC} docs 目录存在"
    else
        echo -e "  ${RED}✗${NC} docs 目录不存在"
        ((failed++))
    fi

    # 检查 skills/ 目录
    if [ -d "$PROJECT_ROOT/skills" ]; then
        echo -e "  ${GREEN}✓${NC} skills 目录存在"
    else
        echo -e "  ${RED}✗${NC} skills 目录不存在"
        ((failed++))
    fi

    # 检查 AGENTS.md
    if [ -f "$PROJECT_ROOT/AGENTS.md" ]; then
        echo -e "  ${GREEN}✓${NC} AGENTS.md 存在"
    else
        echo -e "  ${RED}✗${NC} AGENTS.md 不存在"
        ((failed++))
    fi

    echo ""
    if [ $failed -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# 检查当前工作目录
check_working_directory() {
    echo -e "${BLUE}检查当前工作目录${NC}"
    echo "────────────────────────────────────────"

    local current_dir="$(pwd)"
    if [ "$current_dir" == "$PROJECT_ROOT" ]; then
        echo -e "  ${GREEN}✓${NC} 当前目录是项目根目录"
    else
        echo -e "  ${YELLOW}⚠${NC} 当前目录不是项目根目录"
        echo -e "     建议: cd $PROJECT_ROOT"
    fi

    echo ""
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
    echo "║     Workspace 绑定验证 v2.3.0                      ║"
    echo "╚═══════════════════════════════════════════════════╝"
    echo ""

    local total_passed=0
    local total_failed=0

    if check_project_structure; then
        ((total_passed++))
    else
        ((total_failed++))
    fi

    check_working_directory

    echo "═══════════════════════════════════════════════"
    echo ""
    if [ $total_failed -eq 0 ]; then
        echo -e "${GREEN}✓ Workspace 验证通过${NC}"
        echo ""
        exit 0
    else
        echo -e "${RED}✗ Workspace 验证失败${NC}"
        echo ""
        exit 1
    fi
}

# 执行主函数
main "$@"
