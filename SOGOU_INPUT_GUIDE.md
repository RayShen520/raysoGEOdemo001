# Ubuntu 搜狗输入法安装配置指南

## 🎯 为什么选择搜狗输入法？

- ✅ **功能强大**：词库丰富，输入准确
- ✅ **支持云输入**：联网时更智能
- ✅ **快捷键支持**：`Super + Space` 切换
- ✅ **界面友好**：与 Windows 版本类似

---

## 🚀 快速安装

### 方法一：使用脚本（推荐）

```bash
cd ~/raysoGEOdemo001
git pull  # 获取最新脚本

chmod +x install_sogou_input.sh
bash install_sogou_input.sh
```

### 方法二：手动安装

```bash
# 1. 更新软件包
sudo apt update

# 2. 安装 fcitx 输入法框架
sudo apt install -y fcitx fcitx-config-gtk fcitx-table-all

# 3. 安装中文语言支持
sudo apt install -y language-pack-zh-hans language-pack-zh-hans-base

# 4. 下载搜狗输入法
cd /tmp
wget https://pinyin.sogou.com/linux/download.php?f=linux&bit=64 -O sogoupinyin.deb

# 5. 安装搜狗输入法
sudo apt install -y ./sogoupinyin.deb

# 6. 配置环境变量
echo 'export GTK_IM_MODULE=fcitx' >> ~/.bashrc
echo 'export QT_IM_MODULE=fcitx' >> ~/.bashrc
echo 'export XMODIFIERS=@im=fcitx' >> ~/.bashrc

# 7. 启动 fcitx
fcitx -d
```

---

## ⚙️ 配置输入法

### 方法一：图形界面配置（推荐）

1. **重新登录或重启**
   ```bash
   sudo reboot
   # 或
   # 注销后重新登录
   ```

2. **打开输入法配置**
   - 点击右上角输入法图标（键盘图标）
   - 选择 **配置** 或 **Configure**
   - 或运行命令：`fcitx-config-gtk3`

3. **添加搜狗输入法**
   - 在配置窗口中，点击 **输入法** (Input Method) 标签
   - 点击左下角的 **+** 号
   - **取消勾选** "只显示当前语言" (Only Show Current Language)
   - 在搜索框中输入 "Sogou" 或 "搜狗"
   - 选择 **Sogou Pinyin** (搜狗拼音)
   - 点击 **确定** (OK) 添加

4. **调整输入法顺序**
   - 在输入法列表中，可以拖动调整顺序
   - 建议将 "Sogou Pinyin" 放在前面

### 方法二：命令行配置

```bash
# 打开配置界面
fcitx-config-gtk3
```

然后按照上面的步骤添加搜狗输入法。

---

## ⌨️ 使用输入法

### 切换输入法

- **Super + Space**（Windows键 + 空格）✅ **支持**
- **Ctrl + Space**（Ctrl + 空格）
- **点击右上角输入法图标**切换

### 输入中文

1. 切换到搜狗输入法（按 `Super + Space`）
2. 输入拼音，例如：`nihao` → 你好
3. 使用数字键选择候选词
4. 按空格确认第一个候选词

### 输入法设置

- 右键点击输入法图标 → **配置**
- 可以设置：
  - 皮肤主题
  - 输入习惯
  - 词库管理
  - 云输入设置

---

## 🔧 常见问题

### Q1: 安装后无法切换输入法

**解决方案：**

```bash
# 1. 检查 fcitx 是否运行
ps aux | grep fcitx

# 2. 如果没有运行，启动它
fcitx -d

# 3. 检查环境变量
echo $GTK_IM_MODULE
# 应该显示：fcitx

# 4. 如果不对，重新加载
source ~/.bashrc

# 5. 重新登录或重启
```

### Q2: 输入法图标不显示

**解决方案：**

```bash
# 1. 安装 fcitx 指示器
sudo apt install -y fcitx-module-dbus fcitx-frontend-gtk3

# 2. 重启 fcitx
killall fcitx
fcitx -d

# 3. 如果还是不显示，检查系统托盘设置
# 设置 → 外观 → 系统托盘图标
```

### Q3: 在 Cursor 中无法输入中文

**解决方案：**

1. 确保 fcitx 正在运行：
   ```bash
   fcitx -d
   ```

2. 重启 Cursor：
   ```bash
   # 关闭 Cursor，然后重新打开
   cursor .
   ```

3. 在 Cursor 中按 `Super + Space` 切换输入法

4. 如果还是不行，检查 Cursor 的输入法设置：
   - Cursor → 设置 → 搜索 "input"
   - 确保输入法相关设置正确

### Q4: 下载搜狗输入法失败

**解决方案：**

1. **手动下载**：
   - 访问：https://pinyin.sogou.com/linux/
   - 下载对应版本的 .deb 文件
   - 运行：`sudo apt install ./sogoupinyin_*.deb`

2. **使用备用下载地址**：
   ```bash
   cd /tmp
   wget https://ime.sogouimecdn.com/202112241713/3c5c8c5e3c5c8c5e3c5c8c5e3c5c8c5e/sogoupinyin_2.4.0.3469_amd64.deb
   sudo apt install ./sogoupinyin_2.4.0.3469_amd64.deb
   ```

### Q5: 安装时提示依赖错误

**解决方案：**

```bash
# 修复依赖
sudo apt --fix-broken install

# 重新安装
sudo apt install -y ./sogoupinyin_*.deb
```

### Q6: 想卸载搜狗输入法

**解决方案：**

```bash
# 卸载搜狗输入法
sudo apt remove sogoupinyin

# 如果还想卸载 fcitx（可选）
sudo apt remove fcitx fcitx-config-gtk
```

---

## 🔄 使配置生效

安装完成后，**必须重新登录或重启**：

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

# 启动 fcitx
fcitx -d
```

---

## 📝 验证安装

安装完成后，验证：

```bash
# 1. 检查 fcitx 是否运行
ps aux | grep fcitx

# 2. 检查环境变量
echo $GTK_IM_MODULE
# 应该显示：fcitx

# 3. 检查搜狗输入法是否安装
fcitx-config-gtk3
# 在输入法列表中应该能看到 "Sogou Pinyin"
```

---

## ✅ 完成检查清单

- [ ] 已安装 fcitx 框架
- [ ] 已安装搜狗输入法
- [ ] 已配置环境变量
- [ ] 已重新登录或重启
- [ ] 已添加搜狗输入法到输入法列表
- [ ] 可以使用 `Super + Space` 切换输入法
- [ ] 可以在文本编辑器中输入中文
- [ ] 可以在 Cursor 中输入中文

---

## 🎉 完成！

配置完成后，你就可以使用搜狗输入法了！

**测试：**
1. 打开任意文本编辑器（或 Cursor）
2. 按 `Super + Space` 切换到搜狗输入法
3. 输入拼音测试，例如：`nihao` → 你好

**快捷键：**
- `Super + Space`：切换输入法 ✅
- `Ctrl + Space`：切换输入法
- `Shift`：中英文切换

---

## 📚 更多信息

- 搜狗输入法官网：https://pinyin.sogou.com/linux/
- fcitx 官方文档：https://fcitx-im.org/wiki/

