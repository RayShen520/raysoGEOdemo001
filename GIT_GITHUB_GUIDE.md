# Git + GitHub 迁移指南

## 📋 完整流程

使用 Git 和 GitHub 将代码从 Windows 迁移到 Ubuntu 虚拟机。

---

## 第一步：在 Windows 上初始化 Git 并推送到 GitHub

### 1. 初始化 Git 仓库

在 Windows 的代码目录中运行：

```bash
# 进入项目目录
cd D:\Github-RayShen520\demo010

# 初始化 Git 仓库
git init

# 添加所有文件（.gitignore 会自动排除不需要的文件）
git add .

# 创建第一次提交
git commit -m "初始提交：简书AI自动发布工具"
```

### 2. 在 GitHub 上创建仓库

1. 登录 GitHub：https://github.com
2. 点击右上角 **+** → **New repository**
3. 填写信息：
   - Repository name: `demo010`（或你喜欢的名称）
   - Description: `简书AI自动发布工具`
   - 选择 **Public** 或 **Private**
   - **不要**勾选 "Initialize this repository with a README"（因为本地已有代码）
4. 点击 **Create repository**

### 3. 连接本地仓库到 GitHub

GitHub 创建仓库后会显示命令，类似这样：

```bash
# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/demo010.git

# 或者使用 SSH（如果已配置 SSH key）
# git remote add origin git@github.com:YOUR_USERNAME/demo010.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

**完整示例：**
```bash
# 假设你的 GitHub 用户名是 rayshen520
git remote add origin https://github.com/rayshen520/demo010.git
git branch -M main
git push -u origin main
```

### 4. 验证推送成功

访问你的 GitHub 仓库页面，应该能看到所有代码文件。

---

## 第二步：在 Ubuntu 上克隆代码

### 1. 安装 Git（如果还没安装）

```bash
sudo apt update
sudo apt install git -y

# 验证安装
git --version
```

### 2. 配置 Git（首次使用）

```bash
# 设置用户名和邮箱（替换为你的信息）
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 验证配置
git config --list
```

### 3. 克隆代码

```bash
# 进入用户目录
cd ~

# 克隆仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git clone https://github.com/YOUR_USERNAME/demo010.git

# 或者使用 SSH（如果已配置 SSH key）
# git clone git@github.com:YOUR_USERNAME/demo010.git

# 进入项目目录
cd demo010
```

**完整示例：**
```bash
cd ~
git clone https://github.com/rayshen520/demo010.git
cd demo010
```

### 4. 安装依赖

```bash
# 确保在项目目录中
cd ~/demo010

# 安装系统依赖
sudo apt update
sudo apt install -y python3-pip chromium-chromedriver

# 安装 Chrome（如果还没安装）
if ! command -v google-chrome &> /dev/null; then
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install ./google-chrome-stable_current_amd64.deb -y
    rm google-chrome-stable_current_amd64.deb
fi

# 安装 Python 依赖
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 第三步：日常使用流程

### 在 Windows 上修改代码后

```bash
# 在 Windows 的代码目录中
cd D:\Github-RayShen520\demo010

# 查看修改
git status

# 添加修改的文件
git add .

# 提交修改
git commit -m "描述你的修改"

# 推送到 GitHub
git push
```

### 在 Ubuntu 上获取最新代码

```bash
# 在 Ubuntu 的项目目录中
cd ~/demo010

# 拉取最新代码
git pull
```

### 在 Ubuntu 上修改代码后

```bash
# 在 Ubuntu 的项目目录中
cd ~/demo010

# 查看修改
git status

# 添加修改的文件
git add .

# 提交修改
git commit -m "描述你的修改"

# 推送到 GitHub
git push
```

### 在 Windows 上获取 Ubuntu 的修改

```bash
# 在 Windows 的代码目录中
cd D:\Github-RayShen520\demo010

# 拉取最新代码
git pull
```

---

## 🔐 GitHub 认证方式

### 方式一：HTTPS + Personal Access Token（推荐新手）

1. 在 GitHub 上生成 Token：
   - 点击右上角头像 → **Settings**
   - 左侧菜单 → **Developer settings**
   - **Personal access tokens** → **Tokens (classic)**
   - 点击 **Generate new token (classic)**
   - 填写名称，选择权限（至少勾选 `repo`）
   - 点击 **Generate token**
   - **复制 Token**（只显示一次，务必保存）

2. 使用 Token：
   ```bash
   # 推送时，用户名输入你的 GitHub 用户名
   # 密码输入刚才生成的 Token（不是 GitHub 密码）
   git push
   ```

### 方式二：SSH Key（推荐长期使用）

#### 在 Ubuntu 上生成 SSH Key：

```bash
# 生成 SSH Key（替换为你的邮箱）
ssh-keygen -t ed25519 -C "your.email@example.com"

# 按 Enter 使用默认路径
# 可以设置密码（可选，更安全）

# 查看公钥
cat ~/.ssh/id_ed25519.pub
```

#### 在 GitHub 上添加 SSH Key：

1. 复制刚才显示的公钥内容
2. 登录 GitHub → **Settings** → **SSH and GPG keys**
3. 点击 **New SSH key**
4. Title: 填写名称（如 "Ubuntu VM"）
5. Key: 粘贴公钥内容
6. 点击 **Add SSH key**

#### 测试 SSH 连接：

```bash
ssh -T git@github.com
# 应该看到：Hi YOUR_USERNAME! You've successfully authenticated...
```

#### 使用 SSH 克隆：

```bash
# 使用 SSH URL 克隆
git clone git@github.com:YOUR_USERNAME/demo010.git
```

---

## 📝 常用 Git 命令

### 查看状态和日志

```bash
# 查看当前状态
git status

# 查看提交历史
git log

# 查看简洁的提交历史
git log --oneline

# 查看文件差异
git diff
```

### 撤销操作

```bash
# 撤销工作区的修改（未 add）
git checkout -- <文件名>

# 撤销已 add 但未 commit 的文件
git reset HEAD <文件名>

# 修改最后一次提交信息
git commit --amend -m "新的提交信息"
```

### 分支操作

```bash
# 查看分支
git branch

# 创建新分支
git branch <分支名>

# 切换分支
git checkout <分支名>

# 创建并切换分支
git checkout -b <分支名>

# 合并分支
git merge <分支名>
```

---

## ⚠️ 注意事项

### 1. 不要提交敏感信息

以下文件已在 `.gitignore` 中，不会被提交：
- `chrome_profile/` - 包含登录信息
- `__pycache__/` - Python 缓存
- `*.log` - 日志文件

### 2. 配置文件处理

- `article.json` - 如果包含测试数据，可以考虑不提交
- `article.example.json` - 示例文件，可以提交
- API 密钥在代码中 - 如果代码是公开仓库，建议使用环境变量

### 3. 提交前检查

```bash
# 提交前先查看会提交哪些文件
git status

# 确认无误后再提交
git add .
git commit -m "描述"
git push
```

---

## 🚀 快速开始脚本（Ubuntu）

创建一个一键设置脚本：

```bash
cat > ~/setup_demo010.sh << 'EOF'
#!/bin/bash

echo "=========================================="
echo "  从 GitHub 克隆并设置项目"
echo "=========================================="

# 替换为你的 GitHub 用户名和仓库名
GITHUB_USER="YOUR_USERNAME"
REPO_NAME="demo010"

echo "正在克隆仓库..."
cd ~
git clone https://github.com/$GITHUB_USER/$REPO_NAME.git
cd $REPO_NAME

echo "安装系统依赖..."
sudo apt update
sudo apt install -y python3-pip chromium-chromedriver

echo "安装 Chrome..."
if ! command -v google-chrome &> /dev/null; then
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install ./google-chrome-stable_current_amd64.deb -y
    rm google-chrome-stable_current_amd64.deb
fi

echo "安装 Python 依赖..."
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo "=========================================="
echo "✓ 设置完成！"
echo "=========================================="
echo "进入项目目录: cd ~/$REPO_NAME"
echo "在 Cursor 中打开: cursor ."
echo "测试运行: python3 test_xinghuo_ai.py"
EOF

chmod +x ~/setup_demo010.sh
```

---

## ✅ 完成检查清单

### Windows 端：
- [ ] Git 已安装
- [ ] 项目已初始化 Git
- [ ] 已创建 `.gitignore` 文件
- [ ] 已创建 GitHub 仓库
- [ ] 已推送代码到 GitHub
- [ ] 可以在 GitHub 上看到代码

### Ubuntu 端：
- [ ] Git 已安装
- [ ] 已配置 Git 用户名和邮箱
- [ ] 已克隆代码到 `~/demo010`
- [ ] 已安装系统依赖（Python、Chrome、ChromeDriver）
- [ ] 已安装 Python 依赖包
- [ ] 可以运行测试脚本

---

## 🆘 常见问题

### Q1: 推送时要求输入用户名和密码
**A:** 使用 Personal Access Token 作为密码，或配置 SSH Key。

### Q2: 提示 "Permission denied"
**A:** 检查 GitHub 用户名和仓库名是否正确，或检查 SSH Key 配置。

### Q3: 如何更新代码？
**A:** 
- Windows 修改后：`git add . && git commit -m "描述" && git push`
- Ubuntu 获取：`git pull`

### Q4: 冲突了怎么办？
**A:** 
```bash
# 查看冲突文件
git status

# 手动解决冲突后
git add .
git commit -m "解决冲突"
git push
```

---

## 🎉 完成！

现在你可以在 Windows 和 Ubuntu 之间同步代码了！

**推荐工作流程：**
1. 在 Windows 上开发（使用 Cursor）
2. 提交并推送到 GitHub
3. 在 Ubuntu 上拉取并测试
4. 如有问题，在 Ubuntu 上修复并推送
5. 在 Windows 上拉取最新代码

