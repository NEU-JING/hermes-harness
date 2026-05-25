#!/bin/bash
set -euo pipefail

TARGET="$HOME/.hermes/skills/sdd"
SOURCE="$(dirname "$(readlink -f "$0")")/skills/sdd"

echo "==> Hermes Harness SDD Skills 安装"

# 检测已有安装
if [ -d "$TARGET" ]; then
    echo "⚠️  检测到已有安装: $TARGET"
    echo ""
    echo "   当前已安装的 Skills:"
    ls "$TARGET/"*/SKILL.md 2>/dev/null | sed 's|.*/||;s|/.*||' | sort | while read skill; do
        echo "     - $skill"
    done
    echo ""
    echo "   如需覆盖安装，请先卸载: rm -rf $TARGET"
    echo "   然后重新运行: ./install.sh"
    exit 0
fi

# 创建目标目录
mkdir -p "$(dirname "$TARGET")"

# 安装 Skills
cp -r "$SOURCE" "$TARGET"

# 验证
echo ""
echo "✅ 安装完成。已安装的 Skills:"
ls "$TARGET/"*/SKILL.md 2>/dev/null | sed 's|.*/skills/sdd/||;s|/SKILL.md||' | sort | while read skill; do
    echo "   - $skill"
done

echo ""
echo "下一步: cd /path/to/your-project && 对 Hermes Agent 说 '初始化 SDD'"
