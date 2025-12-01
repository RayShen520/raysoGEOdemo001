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
# 确保只安装 fcitx4，避免与 fcitx5 冲突
sudo apt install -y fcitx fcitx-config-gtk fcitx-table-all 2>&1 | grep -v "Conflicts" || {
    echo -e "${YELLOW}检测到依赖冲突，尝试修复...${NC}"
    # 如果系统有 fcitx5，先卸载
    sudo apt remove -y fcitx5* 2>/dev/null || true
    # 重新安装 fcitx4
    sudo apt install -y fcitx fcitx-config-gtk fcitx-table-all
}
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

# 检查是否已下载
if [ ! -f "$SOGOU_DEB" ]; then
    echo "正在尝试下载搜狗输入法..."
    
    # 方法1：直接下载链接（需要手动获取最新链接）
    # 方法2：提示用户手动下载
    echo -e "${YELLOW}自动下载失败，需要手动下载搜狗输入法${NC}"
    echo ""
    echo "请按以下步骤操作："
    echo "1. 在浏览器中访问：https://pinyin.sogou.com/linux/"
    echo "2. 下载对应版本的 .deb 文件（选择 64位版本）"
    echo "3. 将下载的文件保存到 /tmp/ 目录，命名为 sogoupinyin_*.deb"
    echo "4. 或者直接运行以下命令安装（如果文件在 Downloads 目录）："
    echo "   sudo apt install ~/Downloads/sogoupinyin_*.deb"
    echo ""
    read -p "如果已经下载完成，请按 Enter 继续，否则按 Ctrl+C 退出下载后再运行此脚本..."
    
    # 检查是否有搜狗输入法文件
    if ls /tmp/sogoupinyin_*.deb 1> /dev/null 2>&1 || ls ~/Downloads/sogoupinyin_*.deb 1> /dev/null 2>&1; then
        echo -e "${GREEN}✓ 找到搜狗输入法安装包${NC}"
        # 复制到 /tmp
        if ls ~/Downloads/sogoupinyin_*.deb 1> /dev/null 2>&1; then
            cp ~/Downloads/sogoupinyin_*.deb /tmp/
            SOGOU_DEB=$(basename ~/Downloads/sogoupinyin_*.deb)
        else
            SOGOU_DEB=$(ls /tmp/sogoupinyin_*.deb | head -n1 | xargs basename)
        fi
    else
        echo -e "${RED}✗ 未找到搜狗输入法安装包${NC}"
        echo "请先下载搜狗输入法，然后重新运行此脚本"
        exit 1
    fi
fi
echo -e "${GREEN}✓ 搜狗输入法安装包已准备${NC}"
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

