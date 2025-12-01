#!/bin/bash

# Ubuntu 快速设置脚本
# 从 GitHub 克隆项目并安装所有依赖

echo "=========================================="
echo "  从 GitHub 克隆并设置 demo010 项目"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 配置
GITHUB_USER="RayShen520"     # GitHub 用户名
REPO_NAME="raysoGEOdemo001"  # 仓库名

echo -e "${YELLOW}提示：请先修改脚本中的 GITHUB_USER 和 REPO_NAME${NC}"
echo ""

# 检查是否已修改配置
if [ "$GITHUB_USER" = "YOUR_USERNAME" ]; then
    echo -e "${RED}错误：请先修改脚本中的 GITHUB_USER 和 REPO_NAME${NC}"
    echo ""
    echo "编辑脚本："
    echo "  nano ~/setup_ubuntu.sh"
    echo ""
    echo "或者直接运行命令："
    echo "  cd ~"
    echo "  git clone https://github.com/YOUR_USERNAME/demo010.git"
    echo "  cd demo010"
    echo "  bash install_deps.sh"
    exit 1
fi

# 1. 检查 Git
echo -e "${YELLOW}[1/5] 检查 Git...${NC}"
if ! command -v git &> /dev/null; then
    echo "安装 Git..."
    sudo apt update
    sudo apt install -y git
fi
echo -e "${GREEN}✓ Git 已安装${NC}"
echo ""

# 2. 配置 Git（如果还没配置）
echo -e "${YELLOW}[2/5] 检查 Git 配置...${NC}"
if [ -z "$(git config --global user.name)" ]; then
    echo "请配置 Git 用户名和邮箱："
    read -p "Git 用户名: " git_name
    read -p "Git 邮箱: " git_email
    git config --global user.name "$git_name"
    git config --global user.email "$git_email"
fi
echo -e "${GREEN}✓ Git 已配置${NC}"
echo ""

# 3. 克隆代码
echo -e "${YELLOW}[3/5] 克隆代码...${NC}"
cd ~
if [ -d "$REPO_NAME" ]; then
    echo -e "${YELLOW}目录已存在，跳过克隆${NC}"
    cd "$REPO_NAME"
    git pull
else
    echo "正在从 GitHub 克隆..."
    git clone "https://github.com/$GITHUB_USER/$REPO_NAME.git"
    cd "$REPO_NAME"
fi
echo -e "${GREEN}✓ 代码已克隆到 ~/$REPO_NAME${NC}"
echo ""

# 4. 安装系统依赖
echo -e "${YELLOW}[4/5] 安装系统依赖...${NC}"
sudo apt update
sudo apt install -y python3-pip chromium-chromedriver
echo -e "${GREEN}✓ 系统依赖已安装${NC}"
echo ""

# 5. 安装 Chrome
echo -e "${YELLOW}[5/5] 检查 Chrome...${NC}"
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

# 6. 安装 Python 依赖
echo -e "${YELLOW}[6/6] 安装 Python 依赖...${NC}"
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo -e "${GREEN}✓ Python 依赖已安装${NC}"
else
    echo -e "${RED}✗ 未找到 requirements.txt${NC}"
fi
echo ""

# 完成
echo "=========================================="
echo -e "${GREEN}✓ 设置完成！${NC}"
echo "=========================================="
echo ""
echo "下一步操作："
echo "1. 进入项目目录: cd ~/$REPO_NAME"
echo "2. 在 Cursor 中打开: cursor ."
echo "3. 测试运行: python3 test_xinghuo_ai.py"
echo "4. 运行主程序: python3 main.py"
echo ""

