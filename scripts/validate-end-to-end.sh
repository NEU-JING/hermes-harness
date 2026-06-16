#!/usr/bin/env bash
#
# End-to-End 产物链验证脚本
# 功能：验证 docs/changes/{change_id}/ 下包含完整产物链
#       prd.md / spec.md / design.md / review-report.md / qa-report.md
#
# 版本：2.3.0

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

# 需要检查的产物文件列表
REQUIRED_ARTIFACTS=("prd.md" "spec.md" "design.md" "review-report.md" "qa-report.md")

# 默认 change_id（从 .sdd-state.json 读取）
DEFAULT_CHANGE_ID=""

# 帮助信息
show_help() {
    cat <<EOF
${BLUE}End-to-End 产物链验证脚本${NC}
版本：2.3.0

用法：$(basename "$0") [选项]

选项：
    -h, --help          显示此帮助信息
    -v, --version       显示版本信息
    -c, --change-id     指定变更ID（默认从 .sdd-state.json 自动读取）

示例：
    # 自动检测当前 change_id
    ./scripts/validate-end-to-end.sh

    # 指定 change_id
    ./scripts/validate-end-to-end.sh -c 001-profile-soul-架构落地与机制验证

    # 在 docs/changes/ 目录下运行
    cd docs/changes/001-profile-soul-架构落地与机制验证
    ../../scripts/validate-end-to-end.sh

所需产物文件：
    - prd.md             产品需求文档
    - spec.md            技术规格说明
    - design.md          架构设计文档
    - review-report.md   代码评审报告
    - qa-report.md       质量保证报告

退出码：
    0 = 全部通过
    1 = 存在失败项
EOF
}

# 显示版本
show_version() {
    echo "validate-end-to-end.sh v2.3.0"
}

# 从 .sdd-state.json 读取 change_id（自动处理 Unicode 转义）
read_change_id_from_state() {
    local changes_dir="${PROJECT_ROOT}/docs/changes"
    local state_file=""

    # 如果当前目录下有 .sdd-state.json，直接使用
    if [ -f ".sdd-state.json" ]; then
        state_file=".sdd-state.json"
    else
        # 查找 docs/changes/ 下第一个活跃（未归档）的 .sdd-state.json
        state_file=$(find "$changes_dir" -maxdepth 2 -name ".sdd-state.json" 2>/dev/null | while read -r sf; do
            if ! grep -q '"archived_at"' "$sf" 2>/dev/null && ! grep -q '"current_state"[[:space:]]*:[[:space:]]*"DONE"' "$sf" 2>/dev/null; then
                echo "$sf"
                break
            fi
        done)
    fi

    if [ -z "$state_file" ]; then
        echo ""
        return
    fi

    # 使用 python3 解析 JSON（正确处理 Unicode 转义）
    if command -v python3 &> /dev/null; then
        python3 -c "
import json, sys
try:
    with open('$state_file', 'r') as f:
        data = json.load(f)
    print(data.get('change_id', ''))
except Exception:
    print('')
" 2>/dev/null
    else
        # 回退：用 grep + sed 提取（可能无法处理 Unicode 转义）
        grep -o '"change_id"[[:space:]]*:[[:space:]]*"[^"]*"' "$state_file" 2>/dev/null | head -1 | sed 's/.*"change_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/'
    fi
}

# 检查单个产物文件
check_artifact() {
    local artifact_name="$1"
    local artifact_path="$2"

    if [ -f "$artifact_path" ]; then
        local size
        size=$(wc -c < "$artifact_path" 2>/dev/null || echo "0")
        if [ "$size" -gt 0 ]; then
            echo -e "  ${GREEN}✓${NC} $artifact_name  存在且非空 (${size} bytes)"
            return 0
        else
            echo -e "  ${YELLOW}⚠${NC} $artifact_name  存在但为空文件"
            return 1
        fi
    else
        echo -e "  ${RED}✗${NC} $artifact_name  不存在"
        return 1
    fi
}

# 检查单个变更目录的产物链
check_change_artifacts() {
    local change_id="$1"
    local change_dir="${PROJECT_ROOT}/docs/changes/${change_id}"

    local passed=0
    local failed=0

    echo -e "${BLUE}检查变更: ${change_id}${NC}"
    echo "────────────────────────────────────────"

    # 检查目录存在
    if [ ! -d "$change_dir" ]; then
        echo -e "  ${RED}✗${NC} 变更目录不存在: $change_dir"
        echo ""
        return 1
    fi

    # 检查 .sdd-state.json 是否存在
    local state_file="${change_dir}/.sdd-state.json"
    if [ -f "$state_file" ]; then
        echo -e "  ${GREEN}✓${NC} .sdd-state.json  存在"

        # 读取并显示当前状态
        local current_state
        current_state=$(grep -o '"current_state"[[:space:]]*:[[:space:]]*"[^"]*"' "$state_file" 2>/dev/null | head -1 | sed 's/.*"current_state"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')

        if [ -n "$current_state" ]; then
            echo -e "  ${BLUE}ℹ${NC} 当前状态: $current_state"
        fi
    else
        echo -e "  ${YELLOW}⚠${NC} .sdd-state.json  不存在（非标准变更目录）"
    fi
    echo ""

    # 检查各个产物文件
    echo -e "${BLUE}产物文件检查:${NC}"
    for artifact in "${REQUIRED_ARTIFACTS[@]}"; do
        if check_artifact "$artifact" "${change_dir}/${artifact}"; then
            ((passed++))
        else
            ((failed++))
        fi
    done

    echo ""
    echo "────────────────────────────────────────"
    echo -e "  通过: ${GREEN}${passed}${NC} / ${#REQUIRED_ARTIFACTS[@]}"
    echo -e "  失败: ${RED}${failed}${NC} / ${#REQUIRED_ARTIFACTS[@]}"
    echo ""

    if [ $failed -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# 主函数
main() {
    local change_id=""

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
            -c|--change-id)
                if [ -z "${2:-}" ]; then
                    echo -e "${RED}错误：-c 需要指定一个 change_id${NC}"
                    exit 1
                fi
                change_id="$2"
                shift 2
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
    echo "║     End-to-End 产物链验证 v2.3.0                   ║"
    echo "╚═══════════════════════════════════════════════════╝"
    echo ""

    # 如果未指定 change_id，尝试自动检测
    if [ -z "$change_id" ]; then
        echo -e "${BLUE}未指定 change_id，尝试从 .sdd-state.json 自动检测...${NC}"
        change_id=$(read_change_id_from_state)

        if [ -z "$change_id" ]; then
            echo -e "${RED}错误：无法自动检测 change_id${NC}"
            echo ""
            echo "  请使用 -c 参数显式指定："
            echo "    $(basename "$0") -c <change_id>"
            echo ""
            echo "  或者进入变更目录后运行："
            echo "    cd docs/changes/<change_id>"
            echo "    ../../scripts/$(basename "$0")"
            echo ""
            exit 1
        fi

        echo -e "${GREEN}  ✓ 检测到 change_id: ${change_id}${NC}"
        echo ""
    fi

    # 执行检查
    if check_change_artifacts "$change_id"; then
        echo -e "${GREEN}✓ 产物链完整！所有必需文件均通过验证${NC}"
        echo ""
        echo "  已检查文件："
        for artifact in "${REQUIRED_ARTIFACTS[@]}"; do
            echo "  - $artifact"
        done
        echo ""
        exit 0
    else
        echo -e "${RED}✗ 产物链不完整！存在缺失或空的产物文件${NC}"
        echo ""
        echo "  缺失文件可能的原因："
        echo "  - 流程尚未完成到该阶段"
        echo "  - 对应阶段的 Worker 未正常产出文件"
        echo "  - 文件名不符合规范"
        echo ""
        echo "  建议："
        echo "  - 检查 .sdd-state.json 中的 current_state 确认流程进度"
        echo "  - 重新运行缺失阶段的任务"
        echo ""
        exit 1
    fi
}

# 执行主函数
main "$@"
