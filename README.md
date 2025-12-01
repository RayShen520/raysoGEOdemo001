# 简书文章自动发布工具

使用 Selenium 实现简书文章的自动发布，支持通过 JSON 配置文件自定义标题和正文。

## 功能特点

- ✅ 自动打开简书网站
- ✅ 自动点击"写文章"按钮
- ✅ 自动创建新文章
- ✅ 自动输入标题和正文
- ✅ 自动发布文章
- ✅ 自动验证发布成功
- ✅ 记住登录状态（使用用户数据目录）
- ✅ 模拟人类操作（随机延迟、自然鼠标移动）
- ✅ 支持 JSON 配置文件

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 方式1：使用默认配置文件

1. 复制示例配置文件：
   ```bash
   copy article.example.json article.json
   ```

2. 编辑 `article.json`，填写你的标题和正文：
   ```json
   {
     "title": "我的文章标题",
     "content": "我的文章正文内容"
   }
   ```

3. 运行程序：
   ```bash
   python main.py
   ```

### 方式2：使用指定的配置文件

```bash
python main.py --config my_article.json
```

### 方式3：查看帮助

```bash
python main.py --help
```

## 配置文件格式

### 基础格式

```json
{
  "title": "文章标题",
  "content": "文章正文内容"
}
```

### 多段落文章（使用数组）

```json
{
  "title": "文章标题",
  "content": [
    "第一段内容",
    "",
    "第二段内容",
    "",
    "第三段内容"
  ]
}
```

程序会自动将数组用换行符连接。

## 工作流程

1. 程序读取配置文件（`article.json`）
2. 打开 Chrome 浏览器
3. 访问简书网站
4. 自动点击"写文章"按钮
5. 自动点击"新建文章"按钮
6. 自动输入标题和正文（从配置文件读取）
7. 自动点击"发布文章"按钮
8. 自动验证发布是否成功

## 注意事项

1. **首次运行**：需要手动登录简书账号，之后会自动记住登录状态
2. **配置文件**：如果 `article.json` 不存在，程序会使用默认值，并创建 `article.example.json` 示例文件
3. **登录状态**：登录信息保存在 `chrome_profile` 文件夹中，不要删除此文件夹
4. **配置文件编码**：请使用 UTF-8 编码保存配置文件，以支持中文

## 文件说明

- `main.py` - 主程序
- `article.json` - 配置文件（需要自己创建）
- `article.example.json` - 示例配置文件
- `chrome_profile/` - Chrome 用户数据目录（保存登录状态）
- `requirements.txt` - Python 依赖包列表

