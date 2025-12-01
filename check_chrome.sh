#!/bin/bash

# 检查 Chrome 安装位置的脚本

echo "检查 Chrome 安装位置..."

# 检查常见路径
paths=(
    "/usr/bin/google-chrome"
    "/usr/bin/google-chrome-stable"
    "/usr/bin/chromium-browser"
    "/opt/google/chrome/chrome"
    "/usr/bin/chromium"
)

echo ""
echo "检查常见路径："
for path in "${paths[@]}"; do
    if [ -f "$path" ]; then
        echo "✓ 找到: $path"
        ls -lh "$path"
    else
        echo "✗ 不存在: $path"
    fi
done

echo ""
echo "使用 which 命令查找："
which google-chrome 2>/dev/null && echo "✓ google-chrome: $(which google-chrome)"
which google-chrome-stable 2>/dev/null && echo "✓ google-chrome-stable: $(which google-chrome-stable)"
which chromium-browser 2>/dev/null && echo "✓ chromium-browser: $(which chromium-browser)"

echo ""
echo "检查 Chrome 版本："
google-chrome --version 2>/dev/null || google-chrome-stable --version 2>/dev/null || chromium-browser --version 2>/dev/null || echo "无法获取版本信息"

