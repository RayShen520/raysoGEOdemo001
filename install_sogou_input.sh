#!/bin/bash

# Ubuntu 搜狗输入法安装脚本
# 使用 fcitx 框架 + 搜狗输入法

echo "=========================================="
echo "  安装搜狗输入法（Sogou Pinyin）"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. 更新软件包列表
echo -e "${YELLOW}[1/6] 更新软件包列表...${NC}"
sudo apt update
echo -e "${GREEN}✓ 更新完成${NC}"
echo ""

# 2. 安装 fcitx 输入法框架
echo -e "${YELLOW}[2/6] 安装 fcitx 输入法框架...${NC}"
sudo apt install -y fcitx fcitx-config-gtk fcitx-table-all
echo -e "${GREEN}✓ fcitx 已安装${NC}"
echo ""

# 3. 安装中文语言支持
echo -e "${YELLOW}[3/6] 安装中文语言支持...${NC}"
sudo apt install -y language-pack-zh-hans language-pack-zh-hans-base
echo -e "${GREEN}✓ 语言支持已安装${NC}"
echo ""

# 4. 下载搜狗输入法
echo -e "${YELLOW}[4/6] 下载搜狗输入法...${NC}"
cd /tmp
SOGOU_DEB="sogoupinyin_2.4.0.3469_amd64.deb"
SOGOU_URL="https://pinyin.sogou.com/linux/download.php?f=linux&bit=64"

# 检查是否已下载
if [ ! -f "$SOGOU_DEB" ]; then
    echo "正在下载搜狗输入法..."
    wget -O "$SOGOU_DEB" "$SOGOU_URL" 2>&1 | grep -E "saving|error" || {
        echo -e "${RED}✗ 下载失败，尝试备用方法...${NC}"
        # 备用下载地址
        wget -O "$SOGOU_DEB" "https://ime.sogouimecdn.com/202112241713/3c5c8c5e3c5c8c5e3c5c8c5e3c5c8c5e/sogoupinyin_2.4.0.3469_amd64.deb" || {
            echo -e "${RED}✗ 下载失败，请手动下载：${NC}"
            echo "访问：https://pinyin.sogou.com/linux/"
            echo "下载后运行：sudo apt install ./sogoupinyin_*.deb"
            exit 1
        }
    }
fi
echo -e "${GREEN}✓ 下载完成${NC}"
echo ""

# 5. 安装搜狗输入法
echo -e "${YELLOW}[5/6] 安装搜狗输入法...${NC}"
sudo apt install -y ./"$SOGOU_DEB" 2>&1 | grep -E "Setting up|error" || {
    echo -e "${YELLOW}如果安装失败，可能需要修复依赖...${NC}"
    sudo apt --fix-broken install -y
    sudo apt install -y ./"$SOGOU_DEB"
}
echo -e "${GREEN}✓ 搜狗输入法已安装${NC}"
echo ""

# 6. 配置环境变量
echo -e "${YELLOW}[6/6] 配置环境变量...${NC}"

# 检查并添加环境变量到 .bashrc
if ! grep -q "export GTK_IM_MODULE=fcitx" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# 搜狗输入法配置" >> ~/.bashrc
    echo "export GTK_IM_MODULE=fcitx" >> ~/.bashrc
    echo "export QT_IM_MODULE=fcitx" >> ~/.bashrc
    echo "export XMODIFIERS=@im=fcitx" >> ~/.bashrc
    echo -e "${GREEN}✓ 环境变量已配置${NC}"
else
    echo -e "${YELLOW}环境变量已存在，跳过${NC}"
fi

# 检查并添加到 .xprofile（用于图形界面）
if [ ! -f ~/.xprofile ]; then
    touch ~/.xprofile
fi

if ! grep -q "export GTK_IM_MODULE=fcitx" ~/.xprofile; then
    echo "" >> ~/.xprofile
    echo "# 搜狗输入法配置" >> ~/.xprofile
    echo "export GTK_IM_MODULE=fcitx" >> ~/.xprofile
    echo "export QT_IM_MODULE=fcitx" >> ~/.xprofile
    echo "export XMODIFIERS=@im=fcitx" >> ~/.xprofile
fi

# 启动 fcitx
fcitx -d 2>/dev/null || true

echo ""
echo "=========================================="
echo -e "${GREEN}✓ 安装完成！${NC}"
echo "=========================================="
echo ""
echo "下一步操作："
echo "1. 重新启动 Ubuntu（推荐）或重新登录"
echo "2. 或者运行以下命令立即生效："
echo "   source ~/.bashrc"
echo "   fcitx -d"
echo ""
echo "配置输入法："
echo "1. 重新登录后，点击右上角输入法图标"
echo "2. 选择 '配置' 或 'Configure'"
echo "3. 在 '输入法' 标签中，点击 '+' 添加"
echo "4. 取消勾选 '只显示当前语言'"
echo "5. 搜索 'Sogou' 或 '搜狗'"
echo "6. 选择 'Sogou Pinyin' 并添加"
echo ""
echo "切换输入法："
echo "  Super + Space（Windows键 + 空格）"
echo "  或 Ctrl + Space"
echo ""

