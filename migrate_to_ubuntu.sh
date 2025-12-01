#!/bin/bash

echo "=========================================="
echo "  代码迁移到 Ubuntu 虚拟机 - 自动化脚本"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 检查并创建项目目录
echo -e "${YELLOW}[1/6] 检查项目目录...${NC}"
PROJECT_DIR="$HOME/demo010"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR" || exit 1
echo -e "${GREEN}✓ 项目目录: $PROJECT_DIR${NC}"
echo ""

# 2. 检查共享文件夹并复制代码
echo -e "${YELLOW}[2/6] 检查共享文件夹...${NC}"
SHARED_FOLDER="/mnt/hgfs/demo010"
if [ -d "$SHARED_FOLDER" ]; then
    echo -e "${GREEN}✓ 找到共享文件夹: $SHARED_FOLDER${NC}"
    echo "正在复制代码..."
    cp -r "$SHARED_FOLDER"/* "$PROJECT_DIR/" 2>/dev/null
    echo -e "${GREEN}✓ 代码复制完成${NC}"
else
    echo -e "${RED}✗ 共享文件夹不存在: $SHARED_FOLDER${NC}"
    echo "请先设置 VMware 共享文件夹，或使用 Git 方式迁移"
    echo ""
    echo "设置共享文件夹步骤："
    echo "1. 关闭 Ubuntu 虚拟机"
    echo "2. VMware → 虚拟机 → 设置 → 选项 → 共享文件夹"
    echo "3. 添加共享文件夹，选择 Windows 上的代码目录"
    echo "4. 重新启动虚拟机"
    exit 1
fi
echo ""

# 3. 安装系统依赖
echo -e "${YELLOW}[3/6] 安装系统依赖...${NC}"
sudo apt update > /dev/null 2>&1
sudo apt install -y python3-pip chromium-chromedriver > /dev/null 2>&1
echo -e "${GREEN}✓ Python 和 ChromeDriver 已安装${NC}"
echo ""

# 4. 安装 Chrome（如果还没安装）
echo -e "${YELLOW}[4/6] 检查 Chrome 浏览器...${NC}"
if ! command -v google-chrome &> /dev/null; then
    echo "正在安装 Chrome..."
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install -y ./google-chrome-stable_current_amd64.deb > /dev/null 2>&1
    rm -f google-chrome-stable_current_amd64.deb
    echo -e "${GREEN}✓ Chrome 已安装${NC}"
else
    echo -e "${GREEN}✓ Chrome 已安装（版本: $(google-chrome --version)）${NC}"
fi
echo ""

# 5. 安装 Python 依赖
echo -e "${YELLOW}[5/6] 安装 Python 依赖包...${NC}"
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple > /dev/null 2>&1
    echo -e "${GREEN}✓ Python 依赖已安装${NC}"
else
    echo -e "${RED}✗ 未找到 requirements.txt${NC}"
fi
echo ""

# 6. 验证安装
echo -e "${YELLOW}[6/6] 验证安装...${NC}"
echo "Python 版本: $(python3 --version)"
echo "pip 版本: $(pip3 --version | cut -d' ' -f2)"
if command -v google-chrome &> /dev/null; then
    echo "Chrome 版本: $(google-chrome --version | cut -d' ' -f3)"
fi
if command -v chromedriver &> /dev/null; then
    echo "ChromeDriver 版本: $(chromedriver --version | head -n1 | cut -d' ' -f2)"
fi
echo ""

# 完成
echo "=========================================="
echo -e "${GREEN}✓ 迁移完成！${NC}"
echo "=========================================="
echo ""
echo "下一步操作："
echo "1. 进入项目目录: cd ~/demo010"
echo "2. 在 Cursor 中打开: cursor ."
echo "3. 测试运行: python3 test_xinghuo_ai.py"
echo "4. 运行主程序: python3 main.py"
echo ""

