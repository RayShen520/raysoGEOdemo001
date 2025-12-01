#!/bin/bash

# Ubuntu 中文输入法安装脚本
# 使用 ibus-libpinyin（拼音输入法）

echo "=========================================="
echo "  安装中文输入法（ibus-libpinyin）"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. 更新软件包列表
echo -e "${YELLOW}[1/4] 更新软件包列表...${NC}"
sudo apt update
echo -e "${GREEN}✓ 更新完成${NC}"
echo ""

# 2. 安装中文输入法
echo -e "${YELLOW}[2/4] 安装 ibus-libpinyin...${NC}"
sudo apt install -y ibus-libpinyin ibus-libpinyin-db-open-phrase
echo -e "${GREEN}✓ 输入法已安装${NC}"
echo ""

# 3. 安装语言支持（如果还没安装）
echo -e "${YELLOW}[3/4] 安装中文语言支持...${NC}"
sudo apt install -y language-pack-zh-hans language-pack-zh-hans-base
echo -e "${GREEN}✓ 语言支持已安装${NC}"
echo ""

# 4. 配置输入法
echo -e "${YELLOW}[4/4] 配置输入法...${NC}"

# 设置环境变量（添加到 .bashrc）
if ! grep -q "export GTK_IM_MODULE=ibus" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# 中文输入法配置" >> ~/.bashrc
    echo "export GTK_IM_MODULE=ibus" >> ~/.bashrc
    echo "export QT_IM_MODULE=ibus" >> ~/.bashrc
    echo "export XMODIFIERS=@im=ibus" >> ~/.bashrc
    echo -e "${GREEN}✓ 环境变量已配置${NC}"
else
    echo -e "${YELLOW}环境变量已存在，跳过${NC}"
fi

# 启动 ibus
ibus-daemon -drx

echo ""
echo "=========================================="
echo -e "${GREEN}✓ 安装完成！${NC}"
echo "=========================================="
echo ""
echo "下一步操作："
echo "1. 重新启动 Ubuntu（推荐）或重新登录"
echo "2. 或者运行以下命令立即生效："
echo "   source ~/.bashrc"
echo ""
echo "配置输入法："
echo "1. 打开 设置 → 区域和语言 → 输入源"
echo "2. 点击 + 号添加输入源"
echo "3. 搜索 'Chinese' 或 '中文'"
echo "4. 选择 'Chinese (Intelligent Pinyin)' 或 '中文 (智能拼音)'"
echo "5. 添加后，使用 Super+Space（Windows键+空格）切换输入法"
echo ""
echo "或者使用命令行配置："
echo "  ibus-setup"
echo ""

