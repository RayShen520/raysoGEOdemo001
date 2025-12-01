# Ubuntu 快速开始指南

## 🚀 一键克隆并设置项目

### 方法一：使用快速设置脚本（推荐）

```bash
# 1. 下载设置脚本（从 GitHub 克隆后使用）
cd ~
git clone https://github.com/RayShen520/raysoGEOdemo001.git
cd raysoGEOdemo001

# 2. 运行设置脚本
chmod +x setup_ubuntu.sh
bash setup_ubuntu.sh
```

### 方法二：手动克隆并安装依赖

```bash
# 1. 克隆代码
cd ~
git clone https://github.com/RayShen520/raysoGEOdemo001.git
cd raysoGEOdemo001

# 2. 安装依赖
bash install_deps.sh
```

### 方法三：分步安装

```bash
# 1. 安装 Git（如果还没安装）
sudo apt install git -y

# 2. 配置 Git（首次使用）
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 3. 克隆代码
cd ~
git clone https://github.com/RayShen520/raysoGEOdemo001.git
cd raysoGEOdemo001

# 4. 安装系统依赖
sudo apt update
sudo apt install -y python3-pip chromium-chromedriver

# 5. 安装 Chrome（如果还没安装）
if ! command -v google-chrome &> /dev/null; then
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install ./google-chrome-stable_current_amd64.deb -y
    rm google-chrome-stable_current_amd64.deb
fi

# 6. 安装 Python 依赖
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## ✅ 验证安装

```bash
# 进入项目目录
cd ~/raysoGEOdemo001

# 检查文件
ls -la

# 验证安装
python3 --version
pip3 --version
google-chrome --version
chromedriver --version
```

---

## 🧪 测试运行

```bash
# 进入项目目录
cd ~/raysoGEOdemo001

# 测试 AI 功能（不打开浏览器）
python3 test_xinghuo_ai.py

# 测试批量生成
python3 test_batch_generate.py

# 运行主程序
python3 main.py
```

---

## 📝 在 Cursor 中打开项目

```bash
# 进入项目目录
cd ~/raysoGEOdemo001

# 在 Cursor 中打开
cursor .
```

---

## 🔄 日常使用：获取最新代码

```bash
# 进入项目目录
cd ~/raysoGEOdemo001

# 拉取最新代码
git pull
```

---

## 🆘 遇到问题？

### 问题1：Git 未安装
```bash
sudo apt install git -y
```

### 问题2：权限被拒绝
```bash
chmod +x setup_ubuntu.sh install_deps.sh
```

### 问题3：ChromeDriver 版本不匹配
```bash
# 查看 Chrome 版本
google-chrome --version

# 根据版本下载对应的 ChromeDriver
# 访问：https://chromedriver.chromium.org/downloads
```

### 问题4：无法打开浏览器（无图形界面）
在代码中添加无头模式（headless）：
```python
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
```

---

## 📚 更多信息

- 详细迁移指南：查看 `GIT_GITHUB_GUIDE.md`
- 项目说明：查看 `README.md`

