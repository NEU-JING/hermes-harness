#!/usr/bin/env bash
#
# Hermes SDD Profile 初始化脚本
# 版本：2.3.0
# 功能：一键创建 6 个 SDD Profile 并安装对应的 Skill
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

# Profile 定义
declare -A PROFILE_SKILLS=(
    ["sdd-po"]="po-agent|sdd-orchestrator"
    ["sdd-ba"]="ba-agent|sdd-orchestrator"
    ["sdd-architect"]="architect-agent|sdd-orchestrator"
    ["sdd-coder"]="coder-agent|sdd-orchestrator"
    ["sdd-reviewer"]="reviewer-agent|sdd-orchestrator"
    ["sdd-qa"]="qa-agent|sdd-orchestrator"
)

PROFILE_LIST=("sdd-po" "sdd-ba" "sdd-architect" "sdd-coder" "sdd-reviewer" "sdd-qa")

# 帮助信息
show_help() {
    cat <<EOF
${BLUE}Hermes SDD Profile 初始化脚本${NC}
版本：2.3.0

用法：$(basename "$0") [选项]

选项：
    -h, --help          显示此帮助信息
    -l, --list          列出已存在的 SDD Profile
    -f, --force         强制重新创建（删除现有 Profile 后重建）
    -v, --version       显示版本信息

环境变量：
    HERMES_HOME         自定义 Hermes 配置目录（默认：~/.hermes）

示例：
    # 标准初始化
    ./scripts/init-profiles.sh

    # 强制重新初始化
    ./scripts/init-profiles.sh --force

    # 自定义 Hermes 目录
    HERMES_HOME=/custom/path ./scripts/init-profiles.sh

前置要求：
    - Hermes Agent v2.1.0 或更高版本
    - ~/.hermes/ 目录的读写权限
    - 已克隆 hermes-harness 仓库
EOF
}

# 显示版本
show_version() {
    echo "init-profiles.sh v2.3.0"
}

# 列出 SDD Profile
list_profiles() {
    echo -e "${BLUE}已存在的 SDD Profile:${NC}"
    echo "─────────────────────────"

    local found=0
    for profile in "${PROFILE_LIST[@]}"; do
        if hermes profile list 2>/dev/null | grep -q "^  $profile"; then
            echo -e "  ${GREEN}✓${NC} $profile"
            found=1
        else
            echo -e "  ${RED}✗${NC} $profile (不存在)"
        fi
    done

    if [ $found -eq 0 ]; then
        echo -e "${YELLOW}  未找到任何 SDD Profile${NC}"
    fi
    echo ""
}

# 检查 Hermes 版本
check_hermes_version() {
    echo -e "${BLUE}检查 Hermes 版本...${NC}"

    if ! command -v hermes &> /dev/null; then
        echo -e "${RED}错误：未找到 hermes 命令，请先安装 Hermes Agent${NC}"
        exit 1
    fi

    local version
    version=$(hermes --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)

    if [ -z "$version" ]; then
        echo -e "${YELLOW}警告：无法检测 Hermes 版本，继续执行...${NC}"
        return
    fi

    # 简单的版本比较，要求 >= 2.1.0
    local major minor patch
    major=$(echo "$version" | cut -d. -f1)
    minor=$(echo "$version" | cut -d. -f2)
    patch=$(echo "$version" | cut -d. -f3)

    if [ "$major" -lt 2 ] || ([ "$major" -eq 2 ] && [ "$minor" -lt 1 ]); then
        echo -e "${RED}错误：Hermes 版本过低（当前: $version）${NC}"
        echo -e "${RED}       本框架要求 v2.1.0 或更高版本${NC}"
        exit 1
    fi

    echo -e "${GREEN}  ✓ Hermes 版本: $version${NC}"
}

# 检测 Hermes Home
detect_hermes_home() {
    HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
    echo -e "${BLUE}Hermes 配置目录: $HERMES_HOME${NC}"

    if [ ! -d "$HERMES_HOME" ]; then
        echo -e "${YELLOW}警告：$HERMES_HOME 目录不存在，将尝试创建${NC}"
        mkdir -p "$HERMES_HOME"
    fi

    # 检查写权限
    if ! touch "$HERMES_HOME/.write_test" 2>/dev/null; then
        echo -e "${RED}错误：$HERMES_HOME 目录无写权限${NC}"
        exit 1
    fi
    rm -f "$HERMES_HOME/.write_test"
    echo -e "${GREEN}  ✓ 权限检查通过${NC}"
}

# 创建单个 Profile
create_profile() {
    local profile_name="$1"
    local skill_name="${PROFILE_SKILLS[$profile_name]}"

    echo ""
    echo -e "${BLUE}处理 Profile: $profile_name${NC}"
    echo "────────────────────────────────────────"

    # 检查是否已存在
    if hermes profile list 2>/dev/null | grep -q "^  $profile_name"; then
        if [ "$FORCE_RECREATE" = "true" ]; then
            echo -e "${YELLOW}  强制重建：删除现有 Profile...${NC}"
            # 注意：hermes profile delete 命令可能不存在，这里只是尝试
            rm -rf "$HERMES_HOME/profiles/$profile_name"
        else
            echo -e "${GREEN}  ✓ Profile 已存在，跳过创建${NC}"
            return 0
        fi
    fi

    # 创建 Profile
    echo -e "  创建 Profile..."
    if hermes profile create "$profile_name" 2>&1 | grep -qE "(created|success|已创建)"; then
        echo -e "${GREEN}  ✓ Profile 创建成功${NC}"
    else
        echo -e "${YELLOW}  提示：Profile 可能已创建或命令输出格式变化，继续验证...${NC}"
    fi

    # 验证 Profile 目录存在
    local profile_dir="$HERMES_HOME/profiles/$profile_name"
    if [ -d "$profile_dir" ]; then
        echo -e "${GREEN}  ✓ 目录验证通过${NC}"
    else
        echo -e "${RED}  ✗ 目录验证失败：$profile_dir 不存在${NC}"
        return 1
    fi

    # 安装多个 Skill（只装角色需要的，保持专业化）
    echo -e "  安装角色特定 Skills..."
    local skill_count=0
    IFS='|' read -ra SKILL_ARRAY <<< "$skill_list"
    for skill_name in "${SKILL_ARRAY[@]}"; do
        local skill_source="$PROJECT_ROOT/skills/sdd/$skill_name"
        local skill_target="$profile_dir/skills/$skill_name"

        if [ -d "$skill_source" ]; then
            mkdir -p "$(dirname "$skill_target")"
            if ln -sf "$skill_source" "$skill_target" 2>/dev/null; then
                echo -e "    ${GREEN}✓${NC} $skill_name 已链接"
                ((skill_count++))
            else
                if cp -r "$skill_source" "$skill_target" 2>/dev/null; then
                    echo -e "    ${GREEN}✓${NC} $skill_name 已复制"
                    ((skill_count++))
                else
                    echo -e "    ${YELLOW}⚠ $skill_name 配置失败${NC}"
                fi
            fi
        else
            echo -e "    ${YELLOW}⚠ Skill 源码不存在：$skill_source${NC}"
        fi
    done
    echo -e "${GREEN}  ✓ 已安装 $skill_count 个角色 Skills${NC}"

    # config.yaml 由 Hermes 自动生成，不需要手动写入
    # （仅包含模型配置，不含任何项目路径绑定）

    echo -e "${GREEN}  ✓ $profile_name 初始化完成${NC}"
}

# 主函数
main() {
    # 参数解析
    FORCE_RECREATE="false"
    LIST_ONLY="false"

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
            -l|--list)
                LIST_ONLY="true"
                shift
                ;;
            -f|--force)
                FORCE_RECREATE="true"
                shift
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
    echo "║     Hermes SDD Profile 初始化脚本 v2.3.0          ║"
    echo "╚═══════════════════════════════════════════════════╝"
    echo ""

    # 仅列出模式
    if [ "$LIST_ONLY" = "true" ]; then
        list_profiles
        exit 0
    fi

    # 前置检查
    check_hermes_version
    echo ""
    detect_hermes_home
    echo ""

    # 强制模式警告
    if [ "$FORCE_RECREATE" = "true" ]; then
        echo -e "${RED}⚠  警告：强制模式已启用，将删除现有 Profile 后重建！${NC}"
        read -p "  确认继续？(y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "已取消"
            exit 0
        fi
    fi

    # 开始计时
    local start_time
    start_time=$(date +%s)

    # 创建所有 Profile
    echo ""
    echo -e "${BLUE}开始创建 SDD Profile...${NC}"
    echo "═══════════════════════════════════════════════"

    local success_count=0
    for profile in "${PROFILE_LIST[@]}"; do
        if create_profile "$profile"; then
            ((success_count++))
        fi
    done

    # 完成
    echo ""
    echo "═══════════════════════════════════════════════"
    echo ""
    echo -e "${GREEN}✓ 初始化完成！${NC}"
    echo ""
    echo "  成功创建/更新：$success_count / ${#PROFILE_LIST[@]} 个 Profile"
    echo ""

    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))
    echo "  总耗时：${duration} 秒"
    echo ""

    echo "  下一步："
    echo "    1. 验证 Profile 列表：hermes profile list"
    echo "    2. 启动 SDD 流程：hermes chat -q \"用 SDD 流程开发 xxx\""
    echo "    3. 查看架构文档：cat docs/current/architecture.md"
    echo ""
}

# 执行主函数
main "$@"
