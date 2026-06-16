#!/usr/bin/env bash
#
# Soul 注入验证脚本
# 功能：验证每个 Profile 有 SOUL.md 文件且包含关键内容
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

# Profile 列表与对应的 Soul 关键词
declare -A PROFILE_SOUL_KEYWORDS=(
    ["sdd-po"]="用户思维|场景化|价值导向"
    ["sdd-ba"]="MECE|边界清晰|可测性"
    ["sdd-architect"]="权衡分析|分层设计|演进式"
    ["sdd-coder"]="TDD|防御式编程|可读性"
    ["sdd-reviewer"]="批判性|三阶段评审|异质视角"
    ["sdd-qa"]="破坏式|组合覆盖|回归意识"
)

PROFILE_LIST=("sdd-po" "sdd-ba" "sdd-architect" "sdd-coder" "sdd-reviewer" "sdd-qa")

# 帮助信息
show_help() {
    cat <<EOF
${BLUE}Soul 注入验证脚本${NC}

用法：$(basename "$0") [选项]

选项：
    -h, --help          显示此帮助信息
    -v, --version       显示版本信息

示例：
    # 检查所有 Profile 的 Soul 文件
    ./scripts/validate-soul-injection.sh

EOF
}

# 显示版本
show_version() {
    echo "validate-soul-injection.sh v2.3.0"
}

# 检查单个 Profile 的 Soul
check_profile_soul() {
    local profile_name="$1"
    local profile_dir="$HERMES_HOME/profiles/$profile_name"
    local soul_file="$profile_dir/SOUL.md"
    local keywords="${PROFILE_SOUL_KEYWORDS[$profile_name]}"

    local passed=0
    local failed=0
    local total_keywords=0
    local found_keywords=0

    echo -e "${BLUE}检查 Profile: $profile_name${NC}"
    echo "────────────────────────────────────────"

    # 检查 SOUL.md 文件存在
    if [ -f "$soul_file" ]; then
        echo -e "  ${GREEN}✓${NC} SOUL.md 文件存在"
    else
        echo -e "  ${RED}✗${NC} SOUL.md 文件不存在"
        ((failed++))
        echo ""
        return 1
    fi

    # 检查关键章节
    if grep -q "核心思维模式" "$soul_file"; then
        echo -e "  ${GREEN}✓${NC} 包含 '核心思维模式' 章节"
    else
        echo -e "  ${YELLOW}⚠${NC} 缺少 '核心思维模式' 章节"
    fi

    if grep -q "角色原则" "$soul_file" || grep -q "评审原则" "$soul_file"; then
        echo -e "  ${GREEN}✓${NC} 包含 '角色原则' 章节"
    else
        echo -e "  ${YELLOW}⚠${NC} 缺少 '角色原则' 章节"
    fi

    if grep -q "禁止事项" "$soul_file"; then
        echo -e "  ${GREEN}✓${NC} 包含 '禁止事项' 章节"
    else
        echo -e "  ${YELLOW}⚠${NC} 缺少 '禁止事项' 章节"
    fi

    # 检查关键词
    IFS='|' read -r -a keyword_array <<< "$keywords"
    total_keywords=${#keyword_array[@]}

    for keyword in "${keyword_array[@]}"; do
        if grep -q "$keyword" "$soul_file"; then
            ((found_keywords++))
        fi
    done

    local coverage=$((found_keywords * 100 / total_keywords))
    if [ "$coverage" -ge 100 ]; then
        echo -e "  ${GREEN}✓${NC} 关键词覆盖率: ${coverage}% ($found_keywords/$total_keywords) — 全匹配"
    else
        echo -e "  ${YELLOW}⚠${NC} 关键词覆盖率不足: ${coverage}% ($found_keywords/$total_keywords) — 需要 ${total_keywords}/${total_keywords} 全匹配"
    fi

    echo ""
    if [ "$coverage" -ge 60 ]; then
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
    echo "║     Soul 注入验证 v2.3.0                           ║"
    echo "╚═══════════════════════════════════════════════════╝"
    echo ""

    local total_passed=0
    local total_failed=0

    for profile in "${PROFILE_LIST[@]}"; do
        if check_profile_soul "$profile"; then
            ((total_passed++))
        else
            ((total_failed++))
        fi
    done

    echo "═══════════════════════════════════════════════"
    echo ""
    if [ $total_failed -eq 0 ]; then
        echo -e "${GREEN}✓ 所有 Soul 检查通过${NC}"
        echo ""
        echo "  检查项目："
        echo "  - SOUL.md 文件存在性"
        echo "  - 关键章节（核心思维模式/角色原则/禁止事项）"
        echo "  - 关键词覆盖率"
        echo ""
        exit 0
    else
        echo -e "${YELLOW}⚠  部分 Soul 检查未完全通过${NC}"
        echo ""
        echo "  通过: $total_passed / ${#PROFILE_LIST[@]}"
        echo "  未完全通过: $total_failed / ${#PROFILE_LIST[@]}"
        echo ""
        exit 1
    fi
}

# 执行主函数
main "$@"
