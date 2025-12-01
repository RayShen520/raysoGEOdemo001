"""
测试讯飞星火大模型 WebSocket API 调用
用于生成文章标题和正文
"""

import websocket
import json
import base64
import hashlib
import hmac
import time
from urllib.parse import urlencode
import threading
import ssl
from datetime import datetime

# 讯飞星火 API 配置
APPID = "ddd376fc"
APISecret = "NGIyMGIzZTYzYjQyZWNmMmRmOTVlMGFh"
APIKey = "e15459a1a21ad449e5faa74b0e393f2b"

# WebSocket 配置
HOST = "spark-api.xf-yun.com"
PATH = "/v1.1/chat"


def generate_auth_url():
    """
    生成带认证信息的 WebSocket URL
    
    Returns:
        str: 完整的 WebSocket URL
    """
    # 生成RFC 1123格式的日期（GMT时间）
    import locale
    try:
        # 尝试设置locale为英文
        old_locale = locale.setlocale(locale.LC_TIME, 'en_US')
    except:
        pass
    
    # 使用UTC时间生成RFC 1123格式
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    date_str = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # 也生成Unix时间戳（用于调试）
    timestamp = str(int(time.time()))
    
    print(f"RFC 1123日期: {date_str}")
    print(f"Unix时间戳: {timestamp}")
    
    # 构建签名字符串（使用RFC 1123格式的日期）
    signature_origin = f"host: {HOST}\ndate: {date_str}\nGET {PATH} HTTP/1.1"
    
    print(f"签名字符串: {signature_origin}")
    
    # 使用 APISecret 生成签名
    signature_sha = hmac.new(
        APISecret.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    signature = base64.b64encode(signature_sha).decode('utf-8')
    
    print(f"生成的签名: {signature[:50]}...")
    
    # 构建 authorization 字符串
    authorization_origin = (
        f'api_key="{APIKey}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
    
    # 构建 URL 参数（使用RFC 1123格式的日期）
    # 注意：URL参数可能需要URL编码
    params = {
        'authorization': authorization,
        'date': date_str,  # 使用RFC 1123格式
        'host': HOST
    }
    
    # 生成完整的 WebSocket URL
    url = f"wss://{HOST}{PATH}?{urlencode(params)}"
    print(f"生成的URL: {url[:150]}...")
    return url, date_str  # 同时返回日期字符串用于header


def call_xinghuo_ai(topic):
    """
    调用讯飞星火大模型生成文章
    
    Args:
        topic: 文章主题
    
    Returns:
        str: 生成的文章内容
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
            print(f"收到响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # 检查是否有错误
            if 'header' in data:
                code = data['header'].get('code', 0)
                if code != 0:
                    error_occurred = True
                    error_message = f"API错误，错误码: {code}"
                    print(f"❌ {error_message}")
                    ws.close()
                    return
            
            # 提取内容
            if 'payload' in data and 'choices' in data['payload']:
                choices = data['payload']['choices']
                if 'text' in choices and len(choices['text']) > 0:
                    content = choices['text'][0].get('content', '')
                    if content:
                        full_content += content
                        print(f"内容片段: {content[:50]}...")
            
            # 检查是否结束
            if 'header' in data:
                status = data['header'].get('status', 0)
                if status == 2:  # 2 表示结束
                    response_received = True
                    print("✓ 响应接收完成")
                    ws.close()
                    
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {str(e)}")
            error_occurred = True
            error_message = f"JSON解析错误: {str(e)}"
            ws.close()
        except Exception as e:
            print(f"❌ 处理消息时出错: {str(e)}")
            error_occurred = True
            error_message = f"处理消息时出错: {str(e)}"
            ws.close()
    
    def on_error(ws, error):
        """处理错误"""
        nonlocal error_occurred, error_message
        error_occurred = True
        error_message = f"WebSocket错误: {str(error)}"
        print(f"❌ {error_message}")
    
    def on_close(ws, close_status_code, close_msg):
        """连接关闭"""
        print("连接已关闭")
    
    def on_open(ws):
        """连接打开后发送请求"""
        print("✓ WebSocket 连接已建立")
        
        # 构建提示词
        prompt = f"""你是一位优秀的简书作者，请根据以下主题写一篇文章：

主题：{topic}

要求：
1. 标题：简洁有力，能吸引读者点击，不超过20字
2. 正文：
   - 开头要有吸引力
   - 内容要有深度和见解
   - 结构清晰，段落分明
   - 字数：800-1500字
   - 语言流畅，适合简书平台

请以JSON格式返回，格式如下：
{{
  "title": "文章标题",
  "content": "文章正文内容"
}}"""
        
        # 构建请求数据
        data = {
            "header": {
                "app_id": APPID,
                "uid": "user123"  # 用户ID，可以自定义
            },
            "parameter": {
                "chat": {
                    "domain": "lite",  # Spark Lite 使用 "lite"（根据文档）
                    "temperature": 0.7,  # 温度参数，控制随机性
                    "max_tokens": 2048   # 最大输出长度
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
        
        print("正在发送请求...")
        print(f"提示词: {prompt[:100]}...")
        ws.send(json.dumps(data, ensure_ascii=False))
        print("✓ 请求已发送")
    
    # 生成认证 URL
    auth_url, date_str = generate_auth_url()
    print(f"认证URL: {auth_url[:100]}...")
    
    # 创建 WebSocket 连接（添加SSL支持和header）
    # 注意：websocket-client可能不支持自定义header，需要在URL中传递
    ws = websocket.WebSocketApp(
        auth_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    
    # 在新线程中运行 WebSocket（添加SSL选项）
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
            print("❌ 请求超时")
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


def parse_ai_response(content):
    """
    解析AI返回的内容，提取标题和正文
    
    Args:
        content: AI返回的完整内容
    
    Returns:
        dict: {"title": "...", "content": "..."}
    """
    # 尝试解析JSON格式
    try:
        # 查找JSON部分（可能包含在文本中）
        import re
        json_match = re.search(r'\{[^{}]*"title"[^{}]*"content"[^{}]*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)
            if 'title' in result and 'content' in result:
                return {
                    'title': result['title'].strip(),
                    'content': result['content'].strip()
                }
    except:
        pass
    
    # 如果JSON解析失败，尝试智能提取
    # 查找标题（通常在开头，可能包含"标题"关键词）
    lines = content.split('\n')
    title = ""
    content_start = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # 查找标题
        if '标题' in line or i == 0:
            # 提取标题内容
            if '：' in line or ':' in line:
                title = line.split('：')[-1].split(':')[-1].strip()
            else:
                title = line
            content_start = i + 1
            break
    
    # 如果没有找到标题，使用第一行作为标题
    if not title and lines:
        title = lines[0].strip()[:50]  # 限制标题长度
        content_start = 1
    
    # 提取正文（标题之后的所有内容）
    content_text = '\n'.join(lines[content_start:]).strip()
    
    # 如果正文为空，使用全部内容
    if not content_text:
        content_text = content.strip()
    
    return {
        'title': title if title else "AI生成的文章",
        'content': content_text
    }


def test_generate_article(topic="Python自动化"):
    """
    测试生成文章
    
    Args:
        topic: 文章主题
    """
    print("=" * 60)
    print("测试讯飞星火大模型 API")
    print("=" * 60)
    print(f"文章主题: {topic}")
    print()
    
    try:
        # 调用AI生成文章
        print("正在调用AI生成文章...")
        ai_response = call_xinghuo_ai(topic)
        
        print("\n" + "=" * 60)
        print("AI原始响应:")
        print("=" * 60)
        print(ai_response)
        print()
        
        # 解析响应
        print("=" * 60)
        print("解析响应...")
        print("=" * 60)
        article = parse_ai_response(ai_response)
        
        print(f"标题: {article['title']}")
        print(f"正文预览: {article['content'][:200]}...")
        print()
        
        # 保存到文件
        print("=" * 60)
        print("保存到 article.json...")
        print("=" * 60)
        with open('article.json', 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=2)
        print("✓ 已保存到 article.json")
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        print(f"标题: {article['title']}")
        print(f"正文长度: {len(article['content'])} 字符")
        
        return article
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # 测试生成文章
    # 可以修改主题
    topic = "Python自动化编程"
    test_generate_article(topic)

