# Ubuntu 中文输入法配置指南

## 🎯 快速安装

### 方法一：使用脚本（推荐）

```bash
cd ~/raysoGEOdemo001
git pull  # 获取最新脚本

chmod +x install_chinese_input.sh
bash install_chinese_input.sh
```

### 方法二：手动安装

```bash
# 1. 更新软件包
sudo apt update

# 2. 安装中文输入法
sudo apt install -y ibus-libpinyin ibus-libpinyin-db-open-phrase

# 3. 安装中文语言支持
sudo apt install -y language-pack-zh-hans language-pack-zh-hans-base

# 4. 启动 ibus
ibus-daemon -drx
```

---

## ⚙️ 配置输入法

### 方法一：图形界面配置（推荐）

1. **打开设置**
   - 点击右上角系统菜单
   - 选择 **设置** (Settings)
   - 或按 `Super` 键（Windows键）搜索 "设置"

2. **添加输入源**
   - 在设置中找到 **区域和语言** (Region & Language)
   - 点击 **输入源** (Input Sources) 或 **管理已安装的语言** (Manage Installed Languages)
   - 点击 **+** 号添加输入源
   - 搜索 "Chinese" 或 "中文"
   - 选择 **Chinese (Intelligent Pinyin)** 或 **中文 (智能拼音)**
   - 点击 **添加** (Add)

3. **切换输入法**
   - 使用快捷键：`Super + Space`（Windows键 + 空格）
   - 或点击右上角输入法图标切换

### 方法二：命令行配置

```bash
# 打开 ibus 设置界面
ibus-setup
```

在设置界面中：
1. 点击 **输入法** (Input Method) 标签
2. 点击 **添加** (Add)
3. 选择 **中文** → **智能拼音** (Intelligent Pinyin)
4. 点击 **添加** (Add)

---

## 🔄 使配置生效

安装完成后，需要：

### 方法一：重新启动（推荐）

```bash
sudo reboot
```

### 方法二：重新登录

1. 点击右上角用户菜单
2. 选择 **注销** (Log Out)
3. 重新登录

### 方法三：立即生效（临时）

```bash
# 重新加载环境变量
source ~/.bashrc

# 启动 ibus
ibus-daemon -drx
```

---

## ⌨️ 使用输入法

### 切换输入法

- **快捷键**：`Super + Space`（Windows键 + 空格）
- **或点击**：右上角输入法图标

### 输入中文

1. 切换到中文输入法（智能拼音）
2. 输入拼音，例如：`zhongwen` → 中文
3. 使用数字键选择候选词
4. 按空格确认

---

## 🔧 常见问题

### Q1: 安装后无法切换输入法

**解决方案：**
```bash
# 检查 ibus 是否运行
ps aux | grep ibus

# 如果没有运行，启动它
ibus-daemon -drx

# 重新登录或重启
```

### Q2: 输入法图标不显示

**解决方案：**
```bash
# 安装输入法指示器
sudo apt install -y ibus-gtk ibus-gtk3 ibus-gtk4

# 重启 ibus
killall ibus-daemon
ibus-daemon -drx
```

### Q3: 在终端中无法输入中文

**解决方案：**
```bash
# 确保环境变量已设置
export GTK_IM_MODULE=ibus
export QT_IM_MODULE=ibus
export XMODIFIERS=@im=ibus

# 添加到 ~/.bashrc（永久生效）
echo 'export GTK_IM_MODULE=ibus' >> ~/.bashrc
echo 'export QT_IM_MODULE=ibus' >> ~/.bashrc
echo 'export XMODIFIERS=@im=ibus' >> ~/.bashrc

# 重新加载
source ~/.bashrc
```

### Q4: 在 Cursor 中无法输入中文

**解决方案：**
1. 确保已安装输入法并配置
2. 重启 Cursor
3. 在 Cursor 中按 `Super + Space` 切换输入法

### Q5: 想使用其他输入法

**其他输入法选项：**

1. **搜狗输入法（推荐，功能强大）**
   ```bash
   # 下载搜狗输入法
   wget https://pinyin.sogou.com/linux/download.php?f=linux&bit=64 -O sogou.deb
   sudo apt install ./sogou.deb
   ```

2. **fcitx 输入法框架**
   ```bash
   sudo apt install -y fcitx fcitx-pinyin fcitx-module-cloudpinyin
   ```

---

## 📝 验证安装

安装完成后，验证：

```bash
# 检查 ibus 是否运行
ps aux | grep ibus

# 检查输入法是否安装
ibus list-engine | grep pinyin

# 应该看到：pinyin
```

---

## ✅ 完成检查清单

- [ ] 已安装 ibus-libpinyin
- [ ] 已添加中文输入源
- [ ] 可以使用 `Super + Space` 切换输入法
- [ ] 可以在文本编辑器中输入中文
- [ ] 可以在 Cursor 中输入中文
- [ ] 可以在终端中输入中文（如果需要）

---

## 🎉 完成！

配置完成后，你就可以在 Ubuntu 中输入中文了！

**测试：**
1. 打开任意文本编辑器
2. 按 `Super + Space` 切换到中文输入法
3. 输入拼音测试，例如：`nihao` → 你好

