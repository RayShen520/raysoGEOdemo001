"""
简书文章AI生成与自动发布工具
支持AI生成标题和文章，并自动发布到简书
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import random
import json
import argparse
import websocket
import base64
import hashlib
import hmac
import threading
import ssl
import re
from urllib.parse import urlencode
from datetime import datetime, timezone
try:
    import pyautogui
    PYAutoGUI_AVAILABLE = True
except ImportError:
    PYAutoGUI_AVAILABLE = False
    print("警告: pyautogui 未安装，将使用 ActionChains（可能看不到鼠标移动）")
    print("安装命令: pip install pyautogui")

# ========== 讯飞星火 API 配置 ==========
XINGHUO_APPID = "ddd376fc"
XINGHUO_APISecret = "NGIyMGIzZTYzYjQyZWNmMmRmOTVlMGFh"
XINGHUO_APIKey = "e15459a1a21ad449e5faa74b0e393f2b"
XINGHUO_HOST = "spark-api.xf-yun.com"
XINGHUO_PATH = "/v1.1/chat"


# ========== 讯飞星火 AI 调用函数 ==========

def generate_auth_url():
    """
    生成带认证信息的 WebSocket URL
    
    Returns:
        tuple: (完整的 WebSocket URL, 日期字符串)
    """
    # 生成RFC 1123格式的日期（GMT时间）
    now = datetime.now(timezone.utc)
    date_str = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # 构建签名字符串（使用RFC 1123格式的日期）
    signature_origin = f"host: {XINGHUO_HOST}\ndate: {date_str}\nGET {XINGHUO_PATH} HTTP/1.1"
    
    # 使用 APISecret 生成签名
    signature_sha = hmac.new(
        XINGHUO_APISecret.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    signature = base64.b64encode(signature_sha).decode('utf-8')
    
    # 构建 authorization 字符串
    authorization_origin = (
        f'api_key="{XINGHUO_APIKey}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
    
    # 构建 URL 参数（使用RFC 1123格式的日期）
    params = {
        'authorization': authorization,
        'date': date_str,
        'host': XINGHUO_HOST
    }
    
    # 生成完整的 WebSocket URL
    url = f"wss://{XINGHUO_HOST}{XINGHUO_PATH}?{urlencode(params)}"
    return url, date_str


def call_xinghuo_api(prompt, domain="lite"):
    """
    调用讯飞星火大模型API
    
    Args:
        prompt: 提示词
        domain: 模型版本，默认"lite"
    
    Returns:
        str: AI返回的完整内容
    """
    # 存储完整响应
    full_content = ""
    response_received = False
    error_occurred = False
    error_message = ""
    
    def on_message(ws, message):
        """处理接收到的消息"""
        nonlocal full_content, response_received, error_occurred, error_message
        
        try:
            data = json.loads(message)
            
            # 检查是否有错误
            if 'header' in data:
                code = data['header'].get('code', 0)
                if code != 0:
                    error_occurred = True
                    error_message = f"API错误，错误码: {code}, 消息: {data['header'].get('message', '')}"
                    ws.close()
                    return
            
            # 提取内容
            if 'payload' in data and 'choices' in data['payload']:
                choices = data['payload']['choices']
                if 'text' in choices and len(choices['text']) > 0:
                    content = choices['text'][0].get('content', '')
                    if content:
                        full_content += content
            
            # 检查是否结束
            if 'header' in data:
                status = data['header'].get('status', 0)
                if status == 2:  # 2 表示结束
                    response_received = True
                    ws.close()
                    
        except json.JSONDecodeError as e:
            error_occurred = True
            error_message = f"JSON解析错误: {str(e)}"
            ws.close()
        except Exception as e:
            error_occurred = True
            error_message = f"处理消息时出错: {str(e)}"
            ws.close()
    
    def on_error(ws, error):
        """处理错误"""
        nonlocal error_occurred, error_message
        error_occurred = True
        error_message = f"WebSocket错误: {str(error)}"
    
    def on_close(ws, close_status_code, close_msg):
        """连接关闭"""
        pass
    
    def on_open(ws):
        """连接打开后发送请求"""
        # 构建请求数据
        data = {
            "header": {
                "app_id": XINGHUO_APPID,
                "uid": "user123"
            },
            "parameter": {
                "chat": {
                    "domain": domain,
                    "temperature": 0.7,
                    "max_tokens": 2048
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            }
        }
        
        ws.send(json.dumps(data, ensure_ascii=False))
    
    # 生成认证 URL
    auth_url, date_str = generate_auth_url()
    
    # 创建 WebSocket 连接
    ws = websocket.WebSocketApp(
        auth_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    
    # 在新线程中运行 WebSocket
    def run_ws():
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    
    wst = threading.Thread(target=run_ws)
    wst.daemon = True
    wst.start()
    
    # 等待响应（最多等待60秒）
    timeout = 60
    start_time = time.time()
    while not response_received and not error_occurred:
        if time.time() - start_time > timeout:
            error_occurred = True
            error_message = "请求超时"
            ws.close()
            break
        time.sleep(0.1)
    
    # 等待线程结束
    wst.join(timeout=5)
    
    if error_occurred:
        raise Exception(error_message)
    
    if not full_content:
        raise Exception("未收到有效响应")
    
    return full_content


def generate_title_prompt(core_keyword, target_keywords, title_count):
    """
    生成标题生成专用提示词
    
    Args:
        core_keyword: 核心关键词
        target_keywords: 目标转化关键词列表
        title_count: 生成标题数量
    
    Returns:
        str: 标题生成提示词
    """
    target_keywords_str = "；".join(target_keywords)
    
    prompt = f"""你的角色：一名深谙传播学、心理学，精通爆款文章标题创作的自媒体写手。你尤其擅长运用各种技巧，将营销目的巧妙地隐藏在具有极强吸引力的标题中，避免生硬推广感。

你的核心任务：根据我提供的"核心关键词"和"目标转化关键词"，生成指定数量的、高质量的文章标题。

变量信息：
- 核心关键词：{core_keyword}
- 目标转化关键词：{target_keywords_str}
- 生成标题数量：{title_count}

创作要求与细则：

核心策略：隐藏营销，制造吸引力

绝对不要在标题中直接出现"我们的品牌"或明显的品牌名称。

核心任务是包装"目标转化关键词"，使其成为读者无法抗拒的"信息钩子"，让他们产生"必须点开看看到底是什么"的冲动。

必须运用的标题技巧（需融合使用）：
- 强调式：熟练运用"震惊、警惕、注意、千万、突然、终于、揭秘、重磅"等强调词，制造紧迫感和稀缺性。
- 制造反差：使用"然而、却、但是、反而、原来"等转折词，构建认知冲突，颠覆常规思维。
- 巧用数字：必须将目标关键词中的数字（如"70%复购率"）作为核心卖点突出显示，数字带来具体感和可信度。
- 制造悬念：标题前半部分抛出惊人结果或现象，后半部分留下一个"为什么"或"怎么做"的悬念，引导点击。

输出格式与风格：
- 只输出最终生成的标题列表，无需任何解释。
- 每个标题必须控制在30字以内。
- 风格需贴近自媒体爆文，直接、有力、抓人眼球。
- 每个标题单独一行，使用数字编号（1. 2. 3. ...）

重要：严格限制生成数量
- 必须严格按照"生成标题数量：{title_count}"的要求，只生成{title_count}个标题。
- 绝对不要生成超过指定数量的标题。
- 如果要求生成1个标题，就只生成1个标题；如果要求生成10个标题，就只生成10个标题。

范例参考：
核心关键词：GEO优化服务
目标转化关键词：70%复购率；让品牌被AI最先推荐
生成标题示例：1. 震惊！70%复购率的GEO优化服务，竟让企业主动放弃传统推广"""
    
    return prompt


def generate_article_prompt(title, core_keyword, target_keywords):
    """
    生成文章生成专用提示词
    
    Args:
        title: 文章标题
        core_keyword: 核心关键词
        target_keywords: 目标转化关键词列表
    
    Returns:
        str: 文章生成提示词
    """
    target_keywords_str = "；".join(target_keywords)
    
    prompt = f"""你的角色：一名深耕行业的资深内容策略师与创作专家。你精通行业趋势分析，善于将营销目标转化为高价值、高可读性的深度文章，让读者在获取信息的同时，自然建立对特定关键词与品牌的认知与信任。

我的需求：请你根据我提供的【标题】、【核心关键词】和【目标转化关键词】，创作一篇符合自媒体传播规律的深度行业文章。

变量信息：
- 文章标题：{title}
- 核心关键词：{core_keyword}
- 目标转化关键词：{target_keywords_str}

创作要求与细则：

内容原创性与深度：文章需提供独特的行业洞察或实用指南，避免内容拼凑。保持客观中立的口吻，但观点需鲜明有力。

关键词融合策略：
- 必须在全文（包括标题、引言、正文、总结）中自然、均匀地分布核心关键词与目标转化关键词。
- 避免机械堆砌，需使用关键词的变体和长尾形式，确保阅读流畅。
- 核心品牌词需作为行业典型案例，在正文中至少出现2-3次，以建立品牌认知。

文章结构规范：
- 采用"标题 → 引言 → 分点论述（2-4个小标题） → 总结"的黄金结构。
- 使用有力的小标题分段，增强逻辑性与可读性。

合规与风格：
- 严禁出现任何联系方式、直接促销用语或"我们"等第一人称推广口吻。
- 语言风格需正式、专业且流畅，贴近行业分析或深度指南。
- 如需使用案例数据，请进行模糊化处理（例如："以业内知名企业为例"、"部分头部厂商的数据显示"）。

输出规格：
- 文章字数：600-800字。
- 输出格式：直接输出完整的文章正文，无需任何前置解释。"""
    
    return prompt


def parse_titles(response_text):
    """
    解析AI返回的标题列表
    
    Args:
        response_text: AI返回的文本
    
    Returns:
        list: 标题列表
    """
    titles = []
    lines = response_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 移除编号（如 "1. "、"1、"等）
        line = re.sub(r'^\d+[\.、]\s*', '', line)
        line = line.strip()
        
        # 移除可能的引号
        line = line.strip('"\'')
        
        if line and len(line) <= 50:  # 标题长度限制
            titles.append(line)
    
    return titles


def generate_titles(core_keyword, target_keywords, title_count):
    """
    生成标题列表
    
    Args:
        core_keyword: 核心关键词
        target_keywords: 目标转化关键词列表
        title_count: 生成标题数量
    
    Returns:
        list: 标题列表
    """
    # 生成标题提示词
    prompt = generate_title_prompt(core_keyword, target_keywords, title_count)
    
    # 调用AI生成标题
    response = call_xinghuo_api(prompt)
    
    # 解析标题
    titles = parse_titles(response)
    
    # 限制数量（只取前N个）
    if len(titles) > title_count:
        print(f"⚠ 注意：AI生成了 {len(titles)} 个标题，将只使用前 {title_count} 个")
        titles = titles[:title_count]
    elif len(titles) < title_count:
        print(f"⚠ 注意：AI只生成了 {len(titles)} 个标题，少于要求的 {title_count} 个")
    
    return titles


def generate_article(title, core_keyword, target_keywords):
    """
    为指定标题生成文章
    
    Args:
        title: 文章标题
        core_keyword: 核心关键词
        target_keywords: 目标转化关键词列表
    
    Returns:
        str: 文章内容
    """
    # 生成文章提示词
    prompt = generate_article_prompt(title, core_keyword, target_keywords)
    
    # 调用AI生成文章
    article_content = call_xinghuo_api(prompt)
    
    # 返回内容
    return article_content.strip()


def get_user_input():
    """
    获取用户输入：核心关键词、目标转化关键词、生成标题数量
    
    Returns:
        tuple: (core_keyword, target_keywords, title_count)
    """
    # 输入核心关键词
    print("=" * 60)
    print("【第一步】请输入文章生成参数")
    print("=" * 60)
    core_keyword = input("请输入核心关键词（例如：水壶源头工厂）: ").strip()
    if not core_keyword:
        raise ValueError("核心关键词不能为空！")
    print(f"✓ 核心关键词: {core_keyword}")
    print()
    
    # 输入目标转化关键词
    print("=" * 60)
    print("【第二步】填写目标转化关键词")
    print("=" * 60)
    print("提示：可以输入多个关键词，用逗号或分号分隔（例如：70%复购率,好评率达,一键GEO优化）")
    target_keywords_input = input("请输入目标转化关键词: ").strip()
    if not target_keywords_input:
        raise ValueError("目标转化关键词不能为空！")
    
    # 解析目标转化关键词（支持逗号、分号、换行分隔）
    target_keywords = []
    for separator in [',', '；', ';', '\n']:
        if separator in target_keywords_input:
            target_keywords = [kw.strip() for kw in target_keywords_input.split(separator) if kw.strip()]
            break
    
    # 如果没有分隔符，整个输入作为一个关键词
    if not target_keywords:
        target_keywords = [target_keywords_input]
    
    print(f"✓ 目标转化关键词: {', '.join(target_keywords)}")
    print()
    
    # 输入生成标题数量
    print("=" * 60)
    print("【第三步】填写生成标题数量")
    print("=" * 60)
    while True:
        title_count_input = input("请输入生成标题数量（建议5-20个，默认10个）: ").strip()
        if not title_count_input:
            title_count = 10
            break
        try:
            title_count = int(title_count_input)
            if title_count <= 0:
                print("❌ 标题数量必须大于0，请重新输入")
                continue
            if title_count > 50:
                print("⚠ 警告：标题数量较多，生成时间会较长，建议不超过50个")
                confirm = input("是否继续？(y/n): ").strip().lower()
                if confirm != 'y':
                    continue
            break
        except ValueError:
            print("❌ 请输入有效的数字")
            continue
    
    print(f"✓ 生成标题数量: {title_count}")
    print()
    
    return core_keyword, target_keywords, title_count


def save_article_config(title, content):
    """
    保存文章到 article.json
    
    Args:
        title: 文章标题
        content: 文章内容
    """
    config = {
        "title": title,
        "content": content
    }
    
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "article.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def load_article_config(config_path=None):
    """
    加载文章配置文件
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认路径 article.json
    
    Returns:
        dict: 包含 title 和 content 的字典，如果加载失败返回默认值
    """
    # 默认配置
    default_config = {
        "title": "我终于会写代码了",
        "content": "感谢强大而伟大的AI，让我从电脑小白，变成会代码的小白"
    }
    
    # 如果没有指定路径，使用默认路径
    if config_path is None:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(project_dir, "article.json")
    
    # 转换为绝对路径
    config_path = os.path.abspath(config_path)
    
    # 检查文件是否存在
    if not os.path.exists(config_path):
        print(f"⚠ 配置文件不存在: {config_path}")
        print("将使用默认配置")
        
        # 创建示例配置文件
        example_path = config_path.replace(".json", ".example.json")
        if not os.path.exists(example_path):
            try:
                with open(example_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=2)
                print(f"✓ 已创建示例配置文件: {example_path}")
                print("你可以复制示例文件为 article.json 并编辑内容")
            except Exception as e:
                print(f"创建示例文件时出错: {str(e)}")
        
        return default_config
    
    # 读取配置文件
    try:
        print(f"正在读取配置文件: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 验证必需字段
        if 'title' not in config:
            print("⚠ 配置文件中缺少 'title' 字段，使用默认标题")
            config['title'] = default_config['title']
        
        if 'content' not in config:
            print("⚠ 配置文件中缺少 'content' 字段，使用默认正文")
            config['content'] = default_config['content']
        
        # 处理 content 字段（可能是字符串或数组）
        if isinstance(config['content'], list):
            # 如果是数组，用换行符连接
            config['content'] = '\n'.join(config['content'])
        elif not isinstance(config['content'], str):
            # 如果不是字符串，转换为字符串
            config['content'] = str(config['content'])
        
        # 去除首尾空白
        config['title'] = config['title'].strip()
        config['content'] = config['content'].strip()
        
        # 验证内容不为空
        if not config['title']:
            print("⚠ 标题为空，使用默认标题")
            config['title'] = default_config['title']
        
        if not config['content']:
            print("⚠ 正文为空，使用默认正文")
            config['content'] = default_config['content']
        
        print(f"✓ 成功加载配置")
        print(f"  标题: {config['title']}")
        print(f"  正文预览: {config['content'][:50]}...")
        
        return config
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式错误: {str(e)}")
        print(f"   文件位置: {config_path}")
        print("   请检查 JSON 格式是否正确")
        print("   将使用默认配置")
        return default_config
        
    except Exception as e:
        print(f"❌ 读取配置文件时出错: {str(e)}")
        print("   将使用默认配置")
        return default_config


def safe_click_element(driver, element, description="元素"):
    """
    安全地点击元素，模拟人类操作（移动真实的系统鼠标、随机延迟）
    使用 pyautogui 控制真实的系统鼠标，可以看到鼠标移动
    
    Args:
        driver: WebDriver 实例
        element: 要点击的元素
        description: 元素描述，用于日志输出
    """
    try:
        print(f"正在定位 {description}...")
        
        # 滚动到元素位置，确保元素可见
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(random.uniform(0.5, 0.8))  # 等待滚动完成
        
        # 获取元素在浏览器窗口中的位置和大小
        location = element.location
        size = element.size
        element_center_x = location['x'] + size['width'] / 2
        element_center_y = location['y'] + size['height'] / 2
        
        # 获取浏览器窗口在屏幕上的位置
        window_position = driver.get_window_position()
        window_size = driver.get_window_size()
        
        # 计算元素在屏幕上的绝对坐标
        # 需要考虑浏览器边框和标题栏（Chrome标题栏大约30-40像素）
        chrome_title_bar_height = 80  # Chrome标题栏和标签栏的高度
        screen_x = window_position['x'] + element_center_x
        screen_y = window_position['y'] + chrome_title_bar_height + element_center_y
        
        print(f"元素在浏览器中的位置: x={element_center_x}, y={element_center_y}")
        print(f"浏览器窗口位置: x={window_position['x']}, y={window_position['y']}")
        print(f"元素在屏幕上的绝对坐标: x={screen_x}, y={screen_y}")
        
        if PYAutoGUI_AVAILABLE:
            # 使用 pyautogui 控制真实的系统鼠标
            print("使用 pyautogui 控制真实鼠标移动...")
            
            # 获取当前鼠标位置
            current_x, current_y = pyautogui.position()
            print(f"当前鼠标位置: x={current_x}, y={current_y}")
            
            # 第一步：移动到元素左上角附近（模拟人类不会直接精确移动）
            offset_x1 = random.randint(-40, -20)
            offset_y1 = random.randint(-40, -20)
            target_x1 = screen_x + offset_x1
            target_y1 = screen_y + offset_y1
            print(f"步骤1: 移动到元素附近 ({target_x1}, {target_y1})...")
            pyautogui.moveTo(target_x1, target_y1, duration=random.uniform(0.3, 0.5))
            time.sleep(random.uniform(0.2, 0.4))
            
            # 第二步：移动到元素右上角附近
            offset_x2 = random.randint(20, 40)
            offset_y2 = random.randint(-30, -15)
            target_x2 = screen_x + offset_x2
            target_y2 = screen_y + offset_y2
            print(f"步骤2: 移动到元素另一侧 ({target_x2}, {target_y2})...")
            pyautogui.moveTo(target_x2, target_y2, duration=random.uniform(0.3, 0.5))
            time.sleep(random.uniform(0.2, 0.4))
            
            # 第三步：移动到元素中心附近
            offset_x3 = random.randint(-10, 10)
            offset_y3 = random.randint(-10, 10)
            target_x3 = screen_x + offset_x3
            target_y3 = screen_y + offset_y3
            print(f"步骤3: 移动到元素中心附近 ({target_x3}, {target_y3})...")
            pyautogui.moveTo(target_x3, target_y3, duration=random.uniform(0.2, 0.4))
            time.sleep(random.uniform(0.2, 0.3))
            
            # 第四步：精确移动到元素中心
            print(f"步骤4: 精确移动到元素中心 ({screen_x}, {screen_y})...")
            pyautogui.moveTo(screen_x, screen_y, duration=random.uniform(0.2, 0.3))
            time.sleep(random.uniform(0.2, 0.4))  # 模拟人类反应时间
            
            # 第五步：执行点击
            print(f"步骤5: 正在点击 {description}...")
            pyautogui.click()
            
            print(f"✓ 成功点击 {description}")
            time.sleep(random.uniform(0.5, 1.0))  # 点击后随机等待
            
        else:
            # 如果没有 pyautogui，使用 ActionChains（可能看不到鼠标移动）
            print("使用 ActionChains（可能看不到鼠标移动）...")
            actions = ActionChains(driver)
            
            # 移动到元素附近
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-20, 20)
            actions.move_to_element_with_offset(element, offset_x, offset_y)
            actions.perform()
            time.sleep(random.uniform(0.3, 0.5))
            
            # 精确移动到元素中心
            actions = ActionChains(driver)
            actions.move_to_element(element)
            actions.perform()
            time.sleep(random.uniform(0.2, 0.4))
            
            # 执行点击
            actions = ActionChains(driver)
            actions.click()
            actions.perform()
            
            print(f"✓ 成功点击 {description}")
            time.sleep(random.uniform(0.5, 1.0))
        
    except Exception as e:
        print(f"点击 {description} 时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def click_publish_button(driver):
    """
    点击"发布文章"按钮
    
    Args:
        driver: WebDriver 实例
    """
    try:
        print("\n" + "=" * 50)
        print("开始点击'发布文章'按钮")
        print("=" * 50)
        
        # 等待页面完全加载
        print("等待发布按钮出现...")
        time.sleep(random.uniform(1.5, 2.5))
        
        # 定位"发布文章"按钮，使用多种方式确保稳定性
        wait = WebDriverWait(driver, 20)
        
        # 优先使用 data-action="publicize" 定位
        try:
            print("尝试通过 data-action='publicize' 定位按钮...")
            element = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-action='publicize']"))
            )
            print("成功定位到按钮（通过 data-action）")
        except:
            # 备选方案1：通过文本"发布文章"定位
            try:
                print("尝试通过文本 '发布文章' 定位按钮...")
                element = wait.until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "发布文章"))
                )
                print("成功定位到按钮（通过文本）")
            except:
                # 备选方案2：通过部分文本定位
                try:
                    print("尝试通过部分文本 '发布' 定位按钮...")
                    element = wait.until(
                        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "发布"))
                    )
                    print("成功定位到按钮（通过部分文本）")
                except:
                    # 备选方案3：通过图标 fa-mail-forward 定位
                    print("尝试通过图标 'fa-mail-forward' 定位按钮...")
                    element = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//a[.//i[contains(@class, 'fa-mail-forward')]]"))
                    )
                    print("成功定位到按钮（通过图标）")
        
        # 使用安全的方式点击
        safe_click_element(driver, element, "发布文章按钮")
        
        # 等待页面响应
        time.sleep(random.uniform(1.5, 2.5))
        print("✓ 成功点击'发布文章'按钮！")
        
        # 验证发布是否成功
        verify_publish_success(driver)
        
    except Exception as e:
        print(f"点击'发布文章'按钮时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


def verify_publish_success(driver):
    """
    验证文章是否发布成功
    
    Args:
        driver: WebDriver 实例
    """
    try:
        print("\n" + "=" * 50)
        print("验证发布是否成功...")
        print("=" * 50)
        
        # 等待成功提示出现（可能需要一些时间）
        wait = WebDriverWait(driver, 15)
        
        # 尝试定位"发布成功，点击查看文章"链接
        try:
            print("等待发布成功提示出现...")
            # 通过文本"发布成功，点击查看文章"定位
            success_link = wait.until(
                EC.presence_of_element_located((By.LINK_TEXT, "发布成功，点击查看文章"))
            )
            print("✓ 找到发布成功提示！")
            
            # 也可以通过 class="_2ajaT" 定位
            try:
                success_link_by_class = driver.find_element(By.CSS_SELECTOR, "a._2ajaT")
                print("✓ 通过 class '_2ajaT' 也找到了成功提示")
                
                # 获取链接文本和URL
                link_text = success_link_by_class.text
                link_url = success_link_by_class.get_attribute('href')
                print(f"成功提示文本: {link_text}")
                print(f"文章链接: {link_url}")
                
                print("\n" + "🎉" * 25)
                print("🎉 文章发布成功！🎉")
                print("🎉" * 25)
                return True
            except:
                pass
            
            # 如果通过class找不到，使用文本定位的结果
            link_text = success_link.text
            link_url = success_link.get_attribute('href')
            print(f"成功提示文本: {link_text}")
            print(f"文章链接: {link_url}")
            
            print("\n" + "🎉" * 25)
            print("🎉 文章发布成功！🎉")
            print("🎉" * 25)
            return True
            
        except:
            # 备选方案：通过 class="_2ajaT" 定位
            try:
                print("尝试通过 class '_2ajaT' 定位成功提示...")
                success_link = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a._2ajaT"))
                )
                print("✓ 通过 class '_2ajaT' 找到发布成功提示！")
                
                link_text = success_link.text
                link_url = success_link.get_attribute('href')
                print(f"成功提示文本: {link_text}")
                print(f"文章链接: {link_url}")
                
                print("\n" + "🎉" * 25)
                print("🎉 文章发布成功！🎉")
                print("🎉" * 25)
                return True
            except:
                # 备选方案：通过部分文本"发布成功"定位
                try:
                    print("尝试通过部分文本 '发布成功' 定位成功提示...")
                    success_link = wait.until(
                        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "发布成功"))
                    )
                    print("✓ 通过部分文本找到发布成功提示！")
                    
                    link_text = success_link.text
                    link_url = success_link.get_attribute('href')
                    print(f"成功提示文本: {link_text}")
                    print(f"文章链接: {link_url}")
                    
                    print("\n" + "🎉" * 25)
                    print("🎉 文章发布成功！🎉")
                    print("🎉" * 25)
                    return True
                except:
                    print("⚠ 未找到发布成功提示，可能还在处理中...")
                    print("请手动检查浏览器窗口确认发布状态")
                    return False
        
    except Exception as e:
        print(f"验证发布状态时发生错误: {str(e)}")
        print("请手动检查浏览器窗口确认发布状态")
        return False


def input_article_content(driver, content="感谢强大而伟大的AI，让我从电脑小白，变成会代码的小白"):
    """
    在正文编辑区域输入内容
    
    Args:
        driver: WebDriver 实例
        content: 要填入的正文内容，默认为"感谢强大而伟大的AI，让我从电脑小白，变成会代码的小白"
    """
    try:
        print("\n" + "=" * 50)
        print("开始输入文章正文")
        print("=" * 50)
        
        # 等待页面完全加载
        print("等待正文编辑区域出现...")
        time.sleep(random.uniform(1.5, 2.5))
        
        # 定位正文编辑区域，使用多种方式确保稳定性
        wait = WebDriverWait(driver, 20)
        
        # 优先使用 contenteditable="true" 和 class="kalamu-area" 定位
        try:
            print("尝试通过 contenteditable 和 class 'kalamu-area' 定位编辑区域...")
            content_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'].kalamu-area"))
            )
            print("成功定位到编辑区域（通过 contenteditable 和 class）")
        except:
            # 备选方案1：只通过 class="kalamu-area" 定位
            try:
                print("尝试通过 class 'kalamu-area' 定位编辑区域...")
                content_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".kalamu-area"))
                )
                print("成功定位到编辑区域（通过 class）")
            except:
                # 备选方案2：只通过 contenteditable="true" 定位
                print("尝试通过 contenteditable='true' 定位编辑区域...")
                content_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
                )
                print("成功定位到编辑区域（通过 contenteditable）")
        
        # 滚动到编辑区域位置，确保可见
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", content_element)
        time.sleep(random.uniform(0.3, 0.5))
        
        # 点击编辑区域，确保获得焦点
        print("点击编辑区域，获得焦点...")
        safe_click_element(driver, content_element, "正文编辑区域")
        time.sleep(random.uniform(0.3, 0.5))
        
        # 清空编辑区域（如果有内容）
        print("清空编辑区域...")
        # 对于contenteditable元素，使用JavaScript清空
        driver.execute_script("arguments[0].innerHTML = '';", content_element)
        time.sleep(random.uniform(0.2, 0.4))
        
        # 再次点击确保焦点
        content_element.click()
        time.sleep(random.uniform(0.2, 0.3))
        
        # 模拟人类输入：逐字符输入，添加随机延迟
        print(f"开始输入正文内容...")
        for char in content:
            content_element.send_keys(char)
            # 随机延迟，模拟人类打字速度（50-150毫秒每个字符）
            time.sleep(random.uniform(0.05, 0.15))
        
        # 输入完成后，稍等片刻
        time.sleep(random.uniform(0.5, 0.8))
        
        # 验证输入是否成功（对于contenteditable，检查textContent或innerText）
        try:
            content_text = content_element.text or content_element.get_attribute('textContent')
            if content_text and content in content_text:
                print(f"✓ 成功输入正文内容")
                print(f"内容预览: {content_text[:50]}...")
            else:
                print(f"⚠ 输入的内容可能不完整，当前内容: {content_text[:50] if content_text else '空'}")
                # 如果输入不完整，尝试使用JavaScript直接设置
                driver.execute_script("arguments[0].innerHTML = '<p>' + arguments[1] + '</p>';", content_element, content)
                time.sleep(0.3)
                print(f"✓ 使用JavaScript重新输入完成")
        except Exception as e:
            print(f"验证内容时出错: {str(e)}，但输入操作已完成")
        
    except Exception as e:
        print(f"输入正文时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


def input_article_title(driver, title="我终于会写代码了"):
    """
    在标题输入框中填入标题
    
    Args:
        driver: WebDriver 实例
        title: 要填入的标题文本，默认为"我终于会写代码了"
    """
    try:
        print("\n" + "=" * 50)
        print(f"开始输入文章标题: {title}")
        print("=" * 50)
        
        # 等待页面完全加载
        print("等待标题输入框出现...")
        time.sleep(random.uniform(1.5, 2.5))
        
        # 定位标题输入框，使用多种方式确保稳定性
        wait = WebDriverWait(driver, 20)
        
        # 优先使用 class="_24i7u" 定位
        try:
            print("尝试通过 class '_24i7u' 定位输入框...")
            input_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input._24i7u"))
            )
            print("成功定位到输入框（通过 class）")
        except:
            # 备选方案：通过 input type="text" 和 class 组合定位
            try:
                print("尝试通过 input[type='text'] 和 class 定位输入框...")
                input_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='text' and contains(@class, '_24i7u')]"))
                )
                print("成功定位到输入框（通过 XPath）")
            except:
                # 最后尝试：只通过 type="text" 定位（可能不够精确）
                print("尝试通过 input[type='text'] 定位输入框...")
                input_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
                )
                print("成功定位到输入框（通过 type）")
        
        # 滚动到输入框位置，确保可见
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", input_element)
        time.sleep(random.uniform(0.3, 0.5))
        
        # 点击输入框，确保获得焦点
        print("点击输入框，获得焦点...")
        safe_click_element(driver, input_element, "标题输入框")
        time.sleep(random.uniform(0.3, 0.5))
        
        # 清空输入框（如果有内容）
        print("清空输入框...")
        input_element.clear()
        time.sleep(random.uniform(0.2, 0.4))
        
        # 模拟人类输入：逐字符输入，添加随机延迟
        print(f"开始输入标题: {title}")
        for char in title:
            input_element.send_keys(char)
            # 随机延迟，模拟人类打字速度（50-150毫秒每个字符）
            time.sleep(random.uniform(0.05, 0.15))
        
        # 输入完成后，稍等片刻
        time.sleep(random.uniform(0.3, 0.5))
        
        # 验证输入是否成功
        input_value = input_element.get_attribute('value')
        if input_value == title:
            print(f"✓ 成功输入标题: {input_value}")
        else:
            print(f"⚠ 输入的内容可能不完整，当前值: {input_value}")
            # 如果输入不完整，尝试重新输入
            input_element.clear()
            time.sleep(0.2)
            input_element.send_keys(title)
            time.sleep(0.3)
            print(f"✓ 重新输入完成")
        
    except Exception as e:
        print(f"输入标题时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


def click_new_article_button(driver, title=None, content=None):
    """
    点击"新建文章"按钮，并输入标题和正文
    
    Args:
        driver: WebDriver 实例
        title: 文章标题，如果为None则使用默认值
        content: 文章正文，如果为None则使用默认值
    """
    try:
        print("\n" + "=" * 50)
        print("开始点击'新建文章'按钮")
        print("=" * 50)
        
        # 等待页面完全加载
        print("等待页面加载完成...")
        time.sleep(random.uniform(2.0, 3.0))
        
        # 定位"新建文章"按钮，使用多种方式确保稳定性
        wait = WebDriverWait(driver, 20)
        
        # 优先使用 class="_1GsW5" 定位
        try:
            print("尝试通过 class '_1GsW5' 定位按钮...")
            element = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "._1GsW5"))
            )
            print("成功定位到按钮（通过 class）")
        except:
            # 备选方案1：通过文本"新建文章"定位
            try:
                print("尝试通过文本 '新建文章' 定位按钮...")
                # 使用XPath查找包含"新建文章"文本的元素
                element = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '新建文章')]"))
                )
                print("成功定位到按钮（通过文本）")
            except:
                # 备选方案2：通过包含fa-plus-circle图标的div定位
                print("尝试通过图标 'fa-plus-circle' 定位按钮...")
                element = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, '_1GsW5')]//i[contains(@class, 'fa-plus-circle')]/parent::div"))
                )
                print("成功定位到按钮（通过图标）")
        
        # 使用安全的方式点击
        safe_click_element(driver, element, "新建文章按钮")
        
        # 等待页面响应
        time.sleep(random.uniform(1.0, 2.0))
        print("✓ 成功点击'新建文章'按钮！")
        
        # 点击"新建文章"后，输入标题
        input_article_title(driver, title=title)
        
        # 输入标题后，输入正文
        input_article_content(driver, content=content)
        
        # 输入正文后，点击发布文章
        click_publish_button(driver)
        
    except Exception as e:
        print(f"点击'新建文章'按钮时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


def click_write_button(driver, title=None, content=None):
    """
    点击简书的"写文章"按钮
    
    Args:
        driver: WebDriver 实例
        title: 文章标题，如果为None则使用默认值
        content: 文章正文，如果为None则使用默认值
    """
    try:
        print("=" * 50)
        print("开始点击'写文章'按钮")
        print("=" * 50)
        
        # 等待页面加载完成
        time.sleep(random.uniform(1.0, 2.0))
        
        # 定位"写文章"按钮，使用多种方式确保稳定性
        wait = WebDriverWait(driver, 15)
        
        # 优先使用 class="write-btn" 定位
        try:
            print("尝试通过 class 'write-btn' 定位按钮...")
            element = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".write-btn"))
            )
            print("成功定位到按钮（通过 class）")
        except:
            # 备选方案1：通过 href 定位
            try:
                print("尝试通过 href '/writer#/' 定位按钮...")
                element = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@href='/writer#/']"))
                )
                print("成功定位到按钮（通过 href）")
            except:
                # 备选方案2：通过文本"写文章"定位
                print("尝试通过文本 '写文章' 定位按钮...")
                element = wait.until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "写文章"))
                )
                print("成功定位到按钮（通过文本）")
        
        # 记录当前窗口句柄（标签页）
        original_window = driver.current_window_handle
        print(f"当前窗口句柄: {original_window}")
        
        # 记录点击前的窗口数量
        windows_before = driver.window_handles
        print(f"点击前窗口数量: {len(windows_before)}")
        
        # 使用安全的方式点击
        safe_click_element(driver, element, "写文章按钮")
        
        # 等待新标签页打开
        time.sleep(random.uniform(1.0, 2.0))
        
        # 检查是否有新标签页打开
        windows_after = driver.window_handles
        print(f"点击后窗口数量: {len(windows_after)}")
        
        if len(windows_after) > len(windows_before):
            # 有新标签页打开，切换到新标签页
            print("检测到新标签页，正在切换...")
            for window in windows_after:
                if window not in windows_before:
                    driver.switch_to.window(window)
                    print(f"已切换到新标签页: {window}")
                    break
            
            # 等待新页面加载
            time.sleep(random.uniform(1.0, 2.0))
            
            # 检查新标签页的URL
            try:
                current_url = driver.current_url
                print(f"新标签页URL: {current_url}")
                
                if current_url and ("/writer" in current_url or "writer" in current_url):
                    print("✓ 成功打开写文章页面！")
                    # 页面加载完成后，点击"新建文章"按钮
                    click_new_article_button(driver, title=title, content=content)
                else:
                    print(f"⚠ 新标签页URL: {current_url}，可能不是写文章页面，但新标签页已打开")
                    # 即使URL不确定，也尝试点击"新建文章"按钮
                    print("尝试点击'新建文章'按钮...")
                    click_new_article_button(driver, title=title, content=content)
            except Exception as e:
                print(f"获取新标签页URL时出错: {str(e)}，但新标签页应该已打开")
                # 即使出错，也尝试点击"新建文章"按钮
                print("尝试点击'新建文章'按钮...")
                click_new_article_button(driver, title=title, content=content)
        else:
            # 没有新标签页，检查当前页面是否跳转
            try:
                current_url = driver.current_url
                print(f"点击后当前URL: {current_url}")
                
                if current_url and ("/writer" in current_url or "writer" in current_url):
                    print("✓ 成功跳转到写文章页面！")
                    # 页面加载完成后，点击"新建文章"按钮
                    click_new_article_button(driver, title=title, content=content)
                else:
                    print("⚠ 可能未跳转到写文章页面，请检查浏览器窗口")
                    # 即使URL不确定，也尝试点击"新建文章"按钮
                    print("尝试点击'新建文章'按钮...")
                    click_new_article_button(driver, title=title, content=content)
            except Exception as e:
                print(f"获取URL时出错: {str(e)}，但点击操作已完成")
                # 即使出错，也尝试点击"新建文章"按钮
                print("尝试点击'新建文章'按钮...")
                click_new_article_button(driver, title=title, content=content)
        
    except Exception as e:
        print(f"点击'写文章'按钮时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


def open_website(url: str = "https://www.baidu.com", use_profile: bool = True, title=None, content=None):
    """
    打开指定的网页
    
    Args:
        url: 要打开的网页地址，默认为百度
        use_profile: 是否使用用户数据目录保存登录状态，默认为True
        title: 文章标题，如果为None则使用默认值
        content: 文章正文，如果为None则使用默认值
    """
    driver = None
    try:
        # 配置 Chrome 选项
        chrome_options = Options()
        
        # 如果启用用户数据目录，设置固定的配置文件路径
        if use_profile:
            # 获取项目根目录
            project_dir = os.path.dirname(os.path.abspath(__file__))
            # 创建用户数据目录路径（在项目目录下）
            user_data_dir = os.path.join(project_dir, "chrome_profile")
            # 转换为绝对路径（Windows需要）
            user_data_dir = os.path.abspath(user_data_dir)
            
            # 添加用户数据目录参数
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            print(f"使用用户数据目录: {user_data_dir}")
            print("提示：首次运行需要手动登录，之后会自动保持登录状态")
        
        # 可选：隐藏自动化特征（让网站更难检测到是自动化工具）
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 查找 Chrome 的实际安装位置（优先使用 which 命令）
        import shutil
        chrome_binary = None
        
        # 首先尝试 which 命令（最可靠）
        for cmd in ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"]:
            chrome_binary = shutil.which(cmd)
            if chrome_binary:
                break
        
        # 如果 which 找不到，尝试常见路径（但必须验证存在）
        if not chrome_binary:
            chrome_binary_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium-browser",
                "/opt/google/chrome/google-chrome",  # 注意：是 google-chrome 不是 chrome
                "/usr/bin/chromium"
            ]
            
            for path in chrome_binary_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    chrome_binary = path
                    break
        
        if chrome_binary:
            # 如果是符号链接，获取实际路径
            if os.path.islink(chrome_binary):
                chrome_binary = os.path.realpath(chrome_binary)
            # 再次检查路径是否存在且可执行
            if os.path.exists(chrome_binary) and os.access(chrome_binary, os.X_OK):
                chrome_options.binary_location = chrome_binary
                print(f"找到 Chrome: {chrome_binary}")
            else:
                print(f"警告: Chrome 路径 {chrome_binary} 不存在或不可执行，尝试使用默认路径...")
                chrome_binary = None
        
        if not chrome_binary:
            print("警告: 未找到 Chrome，尝试使用默认路径...")
        
        # 尝试使用 webdriver-manager 自动下载并配置 ChromeDriver
        print("正在初始化 Chrome 浏览器...")
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("使用 webdriver-manager 初始化成功")
        except (ImportError, Exception) as e:
            # 如果 webdriver-manager 不可用或下载失败，使用系统 PATH 中的 chromedriver
            if isinstance(e, ImportError):
                print("webdriver-manager 不可用，尝试使用系统 PATH 中的 ChromeDriver...")
            else:
                print(f"webdriver-manager 下载失败 ({str(e)[:50]}...)，尝试使用系统 PATH 中的 ChromeDriver...")
            driver = webdriver.Chrome(options=chrome_options)
            print("使用系统 ChromeDriver 初始化成功")
        
        # 最大化浏览器窗口，确保可见
        print("最大化浏览器窗口...")
        driver.maximize_window()
        
        # 设置隐式等待
        driver.implicitly_wait(10)
        
        # 打开网页
        print(f"正在打开网页: {url}")
        driver.get(url)
        
        # 等待页面加载完成
        print("等待页面加载...")
        time.sleep(2)  # 等待2秒确保页面完全加载
        
        # 获取页面标题
        page_title = driver.title
        print(f"页面标题: {page_title}")
        print(f"当前URL: {driver.current_url}")
        print("浏览器窗口应该已经打开，请查看！")
        
        # 如果是简书网站，自动点击"写文章"按钮
        if "jianshu.com" in url:
            print("\n检测到简书网站，准备点击'写文章'按钮...")
            click_write_button(driver, title=title, content=content)
        
        # 保持浏览器打开（可以根据需要调整）
        input("\n按 Enter 键关闭浏览器...")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保关闭浏览器
        if driver:
            try:
                driver.quit()
                print("浏览器已关闭")
            except:
                pass


if __name__ == "__main__":
    print("=" * 60)
    print("简书文章AI生成与自动发布工具")
    print("=" * 60)
    print()
    
    try:
        # ========== 第一步：获取用户输入 ==========
        core_keyword, target_keywords, title_count = get_user_input()
        
        # ========== 第二步：生成标题列表 ==========
        print("=" * 60)
        print("【第二步】正在生成标题...")
        print("=" * 60)
        try:
            titles = generate_titles(core_keyword, target_keywords, title_count)
            print(f"✓ 成功生成 {len(titles)} 个标题")
            print("\n生成的标题列表：")
            for i, title in enumerate(titles, 1):
                print(f"  {i}. {title}")
            print()
        except Exception as e:
            print(f"❌ 生成标题失败: {str(e)}")
            import traceback
            traceback.print_exc()
            input("\n按 Enter 键退出...")
            exit(1)
        
        # ========== 第三步：选择标题（默认第一个） ==========
        print("=" * 60)
        print("【第三步】选择要发布的标题")
        print("=" * 60)
        selected_title = titles[0]  # 默认选择第一个
        print(f"✓ 已选择标题: {selected_title}")
        print()
        
        # ========== 第四步：生成文章 ==========
        print("=" * 60)
        print("【第四步】正在生成文章...")
        print("=" * 60)
        try:
            article_content = generate_article(selected_title, core_keyword, target_keywords)
            print(f"✓ 文章生成完成（{len(article_content)} 字符）")
            print()
        except Exception as e:
            print(f"❌ 生成文章失败: {str(e)}")
            import traceback
            traceback.print_exc()
            input("\n按 Enter 键退出...")
            exit(1)
        
        # ========== 第五步：保存到配置文件 ==========
        print("=" * 60)
        print("【第五步】保存文章配置")
        print("=" * 60)
        save_article_config(selected_title, article_content)
        print("✓ 文章已保存到 article.json")
        print()
        
        # ========== 第六步：自动发布 ==========
        print("=" * 60)
        print("【第六步】开始自动发布")
        print("=" * 60)
        print("准备打开简书并发布文章...")
        print()
        
        # 调用现有的发布流程
        open_website(
            url="https://www.jianshu.com/",
            title=selected_title,
            content=article_content
        )
        
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
        exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 键退出...")
        exit(1)

