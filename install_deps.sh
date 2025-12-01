#!/bin/bash

# 仅安装依赖的脚本（不克隆代码）
# 适用于代码已经存在的情况

echo "=========================================="
echo "  安装项目依赖"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查是否在项目目录中
if [ ! -f "requirements.txt" ]; then
    echo "错误：请在项目目录中运行此脚本"
    echo "例如：cd ~/demo010 && bash install_deps.sh"
    exit 1
fi

# 1. 安装系统依赖
echo -e "${YELLOW}[1/3] 安装系统依赖...${NC}"
sudo apt update
sudo apt install -y python3-pip chromium-chromedriver
echo -e "${GREEN}✓ 系统依赖已安装${NC}"
echo ""

# 2. 安装 Chrome
echo -e "${YELLOW}[2/3] 检查 Chrome...${NC}"
if ! command -v google-chrome &> /dev/null; then
    echo "正在安装 Chrome..."
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install -y ./google-chrome-stable_current_amd64.deb
    rm -f google-chrome-stable_current_amd64.deb
    echo -e "${GREEN}✓ Chrome 已安装${NC}"
else
    echo -e "${GREEN}✓ Chrome 已安装（版本: $(google-chrome --version | cut -d' ' -f3)）${NC}"
fi
echo ""

# 3. 安装 Python 依赖
echo -e "${YELLOW}[3/3] 安装 Python 依赖...${NC}"
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
echo -e "${GREEN}✓ Python 依赖已安装${NC}"
echo ""

# 完成
echo "=========================================="
echo -e "${GREEN}✓ 依赖安装完成！${NC}"
echo "=========================================="
echo ""
echo "验证安装："
echo "  Python: $(python3 --version)"
echo "  pip: $(pip3 --version | cut -d' ' -f2)"
if command -v google-chrome &> /dev/null; then
    echo "  Chrome: $(google-chrome --version | cut -d' ' -f3)"
fi
if command -v chromedriver &> /dev/null; then
    echo "  ChromeDriver: $(chromedriver --version | head -n1 | cut -d' ' -f2)"
fi
echo ""

