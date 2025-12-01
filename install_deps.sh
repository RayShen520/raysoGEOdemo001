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

# 尝试多个镜像源
MIRRORS=(
    "https://pypi.org/simple"                    # 官方源
    "https://mirrors.aliyun.com/pypi/simple"     # 阿里云
    "https://pypi.tuna.tsinghua.edu.cn/simple"   # 清华
    "https://pypi.douban.com/simple"              # 豆瓣
)

INSTALLED=0
for mirror in "${MIRRORS[@]}"; do
    echo "尝试使用镜像源: $mirror"
    if pip3 install -r requirements.txt -i "$mirror" --trusted-host "$(echo $mirror | sed 's|https\?://||' | cut -d'/' -f1)" 2>/dev/null; then
        echo -e "${GREEN}✓ Python 依赖已安装（使用镜像源: $mirror）${NC}"
        INSTALLED=1
        break
    else
        echo "镜像源 $mirror 失败，尝试下一个..."
    fi
done

if [ $INSTALLED -eq 0 ]; then
    echo -e "${YELLOW}所有镜像源都失败，尝试使用默认源...${NC}"
    pip3 install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Python 依赖已安装（使用默认源）${NC}"
    else
        echo -e "${RED}✗ Python 依赖安装失败，请检查网络连接${NC}"
        exit 1
    fi
fi
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

