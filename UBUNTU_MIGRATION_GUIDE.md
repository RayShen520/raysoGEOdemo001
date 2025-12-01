# Ubuntu 虚拟机迁移指南

## 📋 迁移步骤总览

将代码从 Windows 迁移到 Ubuntu 虚拟机需要以下步骤：
1. 传输代码文件
2. 安装系统依赖（Chrome、ChromeDriver）
3. 安装 Python 依赖
4. 测试运行

---

## 方法一：使用 VMware 共享文件夹（推荐）

### 1. 在 VMware 中设置共享文件夹

#### Windows 端操作：
1. 关闭 Ubuntu 虚拟机（如果正在运行）
2. 在 VMware 中：**虚拟机** → **设置** → **选项** → **共享文件夹**
3. 选择**总是启用**
4. 点击**添加**，选择你的代码目录：
   - 例如：`D:\Github-RayShen520\demo010`
   - 共享名称：`demo010`（或任意名称）
5. 点击**确定**保存

#### Ubuntu 端操作：
1. 启动 Ubuntu 虚拟机
2. 共享文件夹通常挂载在：`/mnt/hgfs/demo010`
3. 如果看不到，安装 VMware Tools：
   ```bash
   sudo apt update
   sudo apt install open-vm-tools open-vm-tools-desktop -y
   ```
4. 检查共享文件夹：
   ```bash
   ls /mnt/hgfs/
   ```

### 2. 复制代码到 Ubuntu 用户目录

```bash
# 创建项目目录
mkdir -p ~/demo010

# 复制代码（从共享文件夹复制到用户目录）
cp -r /mnt/hgfs/demo010/* ~/demo010/

# 进入项目目录
cd ~/demo010
```

---

## 方法二：使用 Git（如果代码已提交到仓库）

### 1. 在 Windows 上提交代码

```bash
# 在 Windows 的代码目录中
git add .
git commit -m "准备迁移到Ubuntu"
git push
```

### 2. 在 Ubuntu 上克隆代码

```bash
# 安装 Git（如果还没安装）
sudo apt install git -y

# 克隆代码
cd ~
git clone <你的仓库地址> demo010
cd demo010
```

---

## 方法三：直接复制文件（适合小项目）

### 使用 U 盘或网络传输
1. 将代码打包成 zip
2. 通过 U 盘或网络传输到 Ubuntu
3. 解压到 `~/demo010`

---

## 🔧 在 Ubuntu 上安装依赖

### 1. 安装 Python 和 pip

```bash
# 检查 Python 版本（Ubuntu 22.04 通常自带 Python 3.10）
python3 --version

# 安装 pip（如果还没安装）
sudo apt update
sudo apt install python3-pip -y
```

### 2. 安装 Chrome 浏览器

```bash
# 下载并安装 Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y

# 验证安装
google-chrome --version
```

### 3. 安装 ChromeDriver

```bash
# 方法1：使用 apt 安装（推荐）
sudo apt install chromium-chromedriver -y

# 或者方法2：手动下载（如果方法1失败）
# 查看 Chrome 版本
google-chrome --version
# 根据版本下载对应的 ChromeDriver
# 下载地址：https://chromedriver.chromium.org/downloads
```

### 4. 安装 Python 依赖包

```bash
# 进入项目目录
cd ~/demo010

# 安装依赖
pip3 install -r requirements.txt

# 如果遇到代理问题，可以使用国内镜像：
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 🧪 测试运行

### 1. 检查代码文件

```bash
cd ~/demo010
ls -la

# 应该看到：
# - main.py
# - requirements.txt
# - test_xinghuo_ai.py
# - test_batch_generate.py
# - article.json
# 等文件
```

### 2. 测试 AI 功能（不打开浏览器）

```bash
# 测试讯飞星火 AI 连接
python3 test_xinghuo_ai.py
```

### 3. 测试完整流程（需要图形界面）

```bash
# 运行主程序
python3 main.py

# 或者测试批量生成
python3 test_batch_generate.py
```

---

## ⚠️ 注意事项

### 1. 路径差异
- Windows 使用反斜杠 `\`，Ubuntu 使用正斜杠 `/`
- 代码中已使用 `os.path.join()`，应该没问题
- `chrome_profile` 目录会在项目目录下自动创建

### 2. 权限问题
```bash
# 如果遇到权限问题，给脚本添加执行权限
chmod +x ~/demo010/*.py
```

### 3. 图形界面
- 如果 Ubuntu 没有图形界面，需要安装：
  ```bash
  sudo apt install ubuntu-desktop -y
  ```
- 或者使用无头模式（headless）运行 Chrome：
  ```python
  chrome_options.add_argument("--headless")
  ```

### 4. 登录状态
- `chrome_profile` 目录需要重新创建
- 首次运行需要手动登录简书
- 之后会自动保持登录状态

---

## 🚀 快速迁移脚本

创建一个自动化脚本，一键完成迁移：

```bash
# 创建迁移脚本
cat > ~/migrate_to_ubuntu.sh << 'EOF'
#!/bin/bash

echo "开始迁移代码到 Ubuntu..."

# 1. 创建项目目录
mkdir -p ~/demo010
cd ~/demo010

# 2. 检查共享文件夹
if [ -d "/mnt/hgfs/demo010" ]; then
    echo "从共享文件夹复制代码..."
    cp -r /mnt/hgfs/demo010/* ~/demo010/
else
    echo "共享文件夹不存在，请使用 Git 或其他方式传输代码"
    exit 1
fi

# 3. 安装系统依赖
echo "安装系统依赖..."
sudo apt update
sudo apt install -y python3-pip chromium-chromedriver

# 4. 安装 Chrome（如果还没安装）
if ! command -v google-chrome &> /dev/null; then
    echo "安装 Chrome..."
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install ./google-chrome-stable_current_amd64.deb -y
    rm google-chrome-stable_current_amd64.deb
fi

# 5. 安装 Python 依赖
echo "安装 Python 依赖..."
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo "迁移完成！"
echo "进入项目目录：cd ~/demo010"
echo "运行测试：python3 test_xinghuo_ai.py"
EOF

# 添加执行权限
chmod +x ~/migrate_to_ubuntu.sh

# 运行脚本
~/migrate_to_ubuntu.sh
```

---

## 📝 验证清单

迁移完成后，检查以下项目：

- [ ] 代码文件已复制到 `~/demo010`
- [ ] Python 3 已安装（`python3 --version`）
- [ ] pip 已安装（`pip3 --version`）
- [ ] Chrome 已安装（`google-chrome --version`）
- [ ] ChromeDriver 已安装（`chromedriver --version`）
- [ ] Python 依赖已安装（`pip3 list | grep selenium`）
- [ ] 可以运行测试脚本（`python3 test_xinghuo_ai.py`）

---

## 🆘 常见问题

### Q1: 共享文件夹看不到
```bash
# 安装 VMware Tools
sudo apt install open-vm-tools open-vm-tools-desktop -y
# 重启虚拟机
sudo reboot
```

### Q2: ChromeDriver 版本不匹配
```bash
# 查看 Chrome 版本
google-chrome --version

# 下载对应版本的 ChromeDriver
# 访问：https://chromedriver.chromium.org/downloads
```

### Q3: 权限被拒绝
```bash
# 给脚本添加执行权限
chmod +x ~/demo010/*.py
```

### Q4: 无法打开浏览器（无图形界面）
```python
# 在代码中添加无头模式
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
```

---

## ✅ 完成

迁移完成后，你就可以在 Ubuntu 虚拟机中运行代码了！

**下一步：**
1. 在 Cursor 中打开项目：`cd ~/demo010 && cursor .`
2. 运行测试：`python3 test_xinghuo_ai.py`
3. 运行主程序：`python3 main.py`

