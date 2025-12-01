"""
批量生成标题和文章测试
实现瑞幻GEO优化流程：核心关键词 → 目标转化关键词 → 生成标题 → 生成文章
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
from datetime import datetime, timezone

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
        tuple: (完整的 WebSocket URL, 日期字符串)
    """
    # 生成RFC 1123格式的日期（GMT时间）
    now = datetime.now(timezone.utc)
    date_str = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # 构建签名字符串（使用RFC 1123格式的日期）
    signature_origin = f"host: {HOST}\ndate: {date_str}\nGET {PATH} HTTP/1.1"
    
    # 使用 APISecret 生成签名
    signature_sha = hmac.new(
        APISecret.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    signature = base64.b64encode(signature_sha).decode('utf-8')
    
    # 构建 authorization 字符串
    authorization_origin = (
        f'api_key="{APIKey}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
    
    # 构建 URL 参数（使用RFC 1123格式的日期）
    params = {
        'authorization': authorization,
        'date': date_str,
        'host': HOST
    }
    
    # 生成完整的 WebSocket URL
    url = f"wss://{HOST}{PATH}?{urlencode(params)}"
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
                "app_id": APPID,
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
        import re
        line = re.sub(r'^\d+[\.、]\s*', '', line)
        line = line.strip()
        
        # 移除可能的引号
        line = line.strip('"\'')
        
        if line and len(line) <= 50:  # 标题长度限制
            titles.append(line)
    
    return titles


# ========== 文章质量评分函数 ==========

def rule_based_score(article_title, article_content, core_keyword, target_keywords):
    """
    基于规则的快速评分
    
    Args:
        article_title: 文章标题
        article_content: 文章内容
        core_keyword: 核心关键词
        target_keywords: 目标转化关键词列表
    
    Returns:
        dict: 评分结果
    """
    scores = {}
    details = {}
    
    # 1. 字数评分（20分）
    word_count = len(article_content)
    if 600 <= word_count <= 800:
        word_score = 20
    elif 500 <= word_count < 600 or 800 < word_count <= 900:
        word_score = 15
    elif 400 <= word_count < 500 or 900 < word_count <= 1000:
        word_score = 10
    else:
        word_score = 5
    scores['word_count'] = word_score
    details['word_count'] = {
        'score': word_score,
        'value': word_count,
        'target': '600-800字'
    }
    
    # 2. 关键词融合度（30分）
    # 核心关键词出现次数（10分）
    core_count = article_content.count(core_keyword)
    if core_count >= 3:
        core_score = 10
    elif core_count == 2:
        core_score = 7
    elif core_count == 1:
        core_score = 4
    else:
        core_score = 0
    scores['core_keyword'] = core_score
    
    # 目标转化关键词出现次数（10分）
    target_score = 0
    target_found = []
    for kw in target_keywords:
        if kw in article_content:
            target_found.append(kw)
            target_score += 2  # 每个关键词2分，最多10分
    target_score = min(target_score, 10)
    scores['target_keywords'] = target_score
    
    # 关键词分布均匀度（10分）- 简单检查：关键词是否在文章前半部分和后半部分都有出现
    content_half = len(article_content) // 2
    first_half = article_content[:content_half]
    second_half = article_content[content_half:]
    
    distribution_score = 0
    if core_keyword in first_half and core_keyword in second_half:
        distribution_score += 5
    if any(kw in first_half for kw in target_keywords) and any(kw in second_half for kw in target_keywords):
        distribution_score += 5
    scores['keyword_distribution'] = distribution_score
    
    keyword_total = core_score + target_score + distribution_score
    details['keyword_integration'] = {
        'score': keyword_total,
        'core_keyword_count': core_count,
        'target_keywords_found': target_found,
        'distribution_score': distribution_score
    }
    
    # 3. 结构完整性（20分）
    structure_score = 0
    structure_details = {}
    
    # 检查标题（5分）
    if article_title and len(article_title) > 0:
        structure_score += 5
        structure_details['has_title'] = True
    else:
        structure_details['has_title'] = False
    
    # 检查引言（5分）- 检查开头是否有引言特征
    first_paragraph = article_content.split('\n')[0] if article_content else ""
    if len(first_paragraph) > 50:  # 第一段较长，可能是引言
        structure_score += 5
        structure_details['has_intro'] = True
    else:
        structure_details['has_intro'] = False
    
    # 检查小标题（5分）- 查找可能的标题标记
    subtitle_markers = ['一、', '二、', '三、', '四、', '1.', '2.', '3.', '4.', '首先', '其次', '最后', '第一', '第二']
    subtitle_count = sum(1 for marker in subtitle_markers if marker in article_content)
    if subtitle_count >= 2:
        structure_score += 5
        structure_details['has_subtitles'] = True
        structure_details['subtitle_count'] = subtitle_count
    else:
        structure_score += max(0, subtitle_count * 2)  # 有小标题但不够
        structure_details['has_subtitles'] = subtitle_count > 0
        structure_details['subtitle_count'] = subtitle_count
    
    # 检查总结（5分）- 检查结尾是否有总结特征
    last_paragraph = article_content.split('\n')[-1] if article_content else ""
    summary_keywords = ['总结', '综上所述', '总之', '因此', '所以', '由此可见']
    if any(kw in last_paragraph for kw in summary_keywords) or len(last_paragraph) > 30:
        structure_score += 5
        structure_details['has_summary'] = True
    else:
        structure_details['has_summary'] = False
    
    scores['structure'] = structure_score
    details['structure'] = structure_details
    
    # 4. 可读性（20分）
    readability_score = 0
    
    # 段落数量（5分）
    paragraphs = [p.strip() for p in article_content.split('\n') if p.strip()]
    paragraph_count = len(paragraphs)
    if 3 <= paragraph_count <= 6:
        readability_score += 5
    elif paragraph_count == 2 or paragraph_count == 7:
        readability_score += 3
    else:
        readability_score += 1
    
    # 平均段落长度（5分）
    if paragraph_count > 0:
        avg_para_length = sum(len(p) for p in paragraphs) / paragraph_count
        if 100 <= avg_para_length <= 200:
            readability_score += 5
        elif 80 <= avg_para_length < 100 or 200 < avg_para_length <= 250:
            readability_score += 3
        else:
            readability_score += 1
    
    # 标点符号使用（5分）- 检查是否有适当的标点
    punctuation_count = sum(article_content.count(p) for p in ['。', '，', '！', '？', '；'])
    if punctuation_count >= paragraph_count * 2:  # 每段至少2个标点
        readability_score += 5
    elif punctuation_count >= paragraph_count:
        readability_score += 3
    else:
        readability_score += 1
    
    # 句子长度多样性（5分）- 简单检查：是否有长短句
    sentences = article_content.replace('。', '。\n').split('\n')
    sentence_lengths = [len(s) for s in sentences if s.strip()]
    if sentence_lengths:
        length_variance = max(sentence_lengths) - min(sentence_lengths) if len(sentence_lengths) > 1 else 0
        if length_variance > 20:  # 句子长度有差异
            readability_score += 5
        elif length_variance > 10:
            readability_score += 3
        else:
            readability_score += 1
    
    scores['readability'] = readability_score
    details['readability'] = {
        'paragraph_count': paragraph_count,
        'punctuation_count': punctuation_count
    }
    
    # 5. 合规性（10分）
    compliance_score = 10
    compliance_issues = []
    
    # 检查联系方式
    contact_patterns = ['电话', '手机', '微信', 'QQ', '邮箱', '@', 'www.', 'http']
    if any(pattern in article_content for pattern in contact_patterns):
        compliance_score -= 3
        compliance_issues.append('可能包含联系方式')
    
    # 检查第一人称推广
    promotion_words = ['我们', '我们的', '本公司', '本品牌']
    if any(word in article_content for word in promotion_words):
        compliance_score -= 3
        compliance_issues.append('包含第一人称推广用语')
    
    # 检查直接促销
    sales_words = ['立即购买', '限时优惠', '点击购买', '立即下单']
    if any(word in article_content for word in sales_words):
        compliance_score -= 4
        compliance_issues.append('包含直接促销用语')
    
    compliance_score = max(0, compliance_score)  # 确保不为负
    scores['compliance'] = compliance_score
    details['compliance'] = {
        'score': compliance_score,
        'issues': compliance_issues
    }
    
    # 计算总分
    total_score = sum(scores.values())
    
    return {
        'rule_score': total_score,
        'scores': scores,
        'details': details,
        'max_score': 100
    }


def ai_based_score(article_title, article_content, core_keyword, target_keywords):
    """
    基于AI的深度评分
    
    Args:
        article_title: 文章标题
        article_content: 文章内容
        core_keyword: 核心关键词
        target_keywords: 目标转化关键词列表
    
    Returns:
        dict: AI评分结果
    """
    target_keywords_str = "；".join(target_keywords)
    
    prompt = f"""你是一位专业的内容质量评估专家。请对以下文章进行多维度质量评分。

文章标题：{article_title}
文章内容：
{article_content}

核心关键词：{core_keyword}
目标转化关键词：{target_keywords_str}

请从以下维度进行评分（每个维度0-100分）：
1. 内容质量：原创性、深度、逻辑性、观点鲜明度
2. 关键词融合：核心关键词和目标转化关键词是否自然融合
3. 结构完整性：标题、引言、正文、总结是否完整
4. 可读性：语言流畅度、段落结构、表达清晰度
5. 合规性：是否符合自媒体平台规范，无推广用语

请以JSON格式返回评分结果，格式如下：
{{
  "scores": {{
    "content_quality": 85,
    "keyword_integration": 90,
    "structure": 80,
    "readability": 88,
    "compliance": 95
  }},
  "overall_score": 87.6,
  "strengths": ["关键词融合自然", "结构清晰"],
  "weaknesses": ["字数略少", "缺少案例"],
  "suggestions": ["可以增加具体案例", "可以丰富结尾部分"]
}}

只返回JSON，不要其他解释。"""
    
    try:
        response = call_xinghuo_api(prompt)
        
        # 尝试解析JSON
        import re
        json_match = re.search(r'\{[^{}]*"scores"[^{}]*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)
            return {
                'ai_score': result.get('overall_score', 0),
                'scores': result.get('scores', {}),
                'strengths': result.get('strengths', []),
                'weaknesses': result.get('weaknesses', []),
                'suggestions': result.get('suggestions', [])
            }
        else:
            # 如果无法解析JSON，返回默认值
            return {
                'ai_score': 0,
                'scores': {},
                'strengths': [],
                'weaknesses': ['AI评分解析失败'],
                'suggestions': []
            }
    except Exception as e:
        return {
            'ai_score': 0,
            'scores': {},
            'strengths': [],
            'weaknesses': [f'AI评分失败: {str(e)}'],
            'suggestions': []
        }


def evaluate_article_quality(article_title, article_content, core_keyword, target_keywords, threshold=70):
    """
    综合评估文章质量（规则评分 + AI评分）
    
    Args:
        article_title: 文章标题
        article_content: 文章内容
        core_keyword: 核心关键词
        target_keywords: 目标转化关键词列表
        threshold: 规则评分阈值，低于此值才进行AI评分（默认70）
    
    Returns:
        dict: 完整评分结果
    """
    # 先进行规则评分（快速）
    rule_result = rule_based_score(article_title, article_content, core_keyword, target_keywords)
    rule_score = rule_result['rule_score']
    
    ai_result = None
    overall_score = rule_score
    
    # 如果规则评分低于阈值，进行AI深度评分
    if rule_score < threshold:
        print(f"  规则评分 {rule_score} 分低于阈值 {threshold}，进行AI深度评分...")
        ai_result = ai_based_score(article_title, article_content, core_keyword, target_keywords)
        ai_score = ai_result.get('ai_score', 0)
        
        # 综合评分：规则评分40% + AI评分60%
        overall_score = rule_score * 0.4 + ai_score * 0.6
    else:
        print(f"  规则评分 {rule_score} 分达到阈值，跳过AI评分")
    
    # 确定质量等级
    if overall_score >= 90:
        grade = "优秀"
    elif overall_score >= 80:
        grade = "良好"
    elif overall_score >= 70:
        grade = "一般"
    else:
        grade = "需改进"
    
    return {
        'overall_score': round(overall_score, 1),
        'rule_score': rule_score,
        'ai_score': ai_result['ai_score'] if ai_result else None,
        'grade': grade,
        'rule_details': rule_result,
        'ai_details': ai_result
    }


def display_score_result(score_result):
    """
    显示评分结果
    
    Args:
        score_result: 评分结果字典
    """
    overall_score = score_result['overall_score']
    rule_score = score_result['rule_score']
    ai_score = score_result.get('ai_score')
    grade = score_result['grade']
    
    print("\n" + "━" * 60)
    print("【文章质量评分】")
    print("━" * 60)
    print(f"综合评分：{overall_score}分  [{grade}]")
    print()
    
    print("详细评分：")
    rule_details = score_result['rule_details']
    scores = rule_details['scores']
    
    # 显示规则评分
    print(f"  字数符合度：     {scores.get('word_count', 0):2d}分  ", end="")
    word_count = rule_details['details'].get('word_count', {}).get('value', 0)
    print(f"(当前: {word_count}字)")
    
    print(f"  关键词融合：     {scores.get('core_keyword', 0) + scores.get('target_keywords', 0) + scores.get('keyword_distribution', 0):2d}分")
    print(f"  结构完整性：     {scores.get('structure', 0):2d}分")
    print(f"  可读性：         {scores.get('readability', 0):2d}分")
    print(f"  合规性：         {scores.get('compliance', 0):2d}分")
    print()
    
    # 显示AI评分（如果有）
    if ai_score is not None:
        print(f"  AI深度评分：     {ai_score:.1f}分")
        ai_details = score_result.get('ai_details', {})
        if ai_details.get('strengths'):
            print("\n  优点：")
            for strength in ai_details['strengths']:
                print(f"    ✓ {strength}")
        if ai_details.get('weaknesses'):
            print("\n  不足：")
            for weakness in ai_details['weaknesses']:
                print(f"    • {weakness}")
        if ai_details.get('suggestions'):
            print("\n  改进建议：")
            for suggestion in ai_details['suggestions']:
                print(f"    → {suggestion}")
    
    print("━" * 60)


def test_batch_generate():
    """
    测试批量生成标题和文章
    """
    print("=" * 60)
    print("批量生成标题和文章测试")
    print("=" * 60)
    print()
    
    # 第一步：填写核心关键词
    print("=" * 60)
    print("第一步：填写核心关键词")
    print("=" * 60)
    core_keyword = input("请输入核心关键词（例如：水壶源头工厂）: ").strip()
    if not core_keyword:
        print("❌ 核心关键词不能为空！")
        return
    print(f"✓ 核心关键词: {core_keyword}")
    print()
    
    # 第二步：填写目标转化关键词
    print("=" * 60)
    print("第二步：填写目标转化关键词")
    print("=" * 60)
    print("提示：可以输入多个关键词，用逗号或分号分隔（例如：70%复购率,好评率达,一键GEO优化）")
    target_keywords_input = input("请输入目标转化关键词: ").strip()
    if not target_keywords_input:
        print("❌ 目标转化关键词不能为空！")
        return
    
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
    
    # 第三步：填写生成标题数量
    print("=" * 60)
    print("第三步：填写生成标题数量")
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
    
    # 第四步：生成标题提示词
    print("=" * 60)
    print("第四步：生成标题生成专用提示词")
    print("=" * 60)
    title_prompt = generate_title_prompt(core_keyword, target_keywords, title_count)
    print("提示词已生成（预览前200字）:")
    print(title_prompt[:200] + "...")
    print()
    
    # 第五步：调用AI生成标题
    print("=" * 60)
    print("第五步：调用AI生成标题")
    print("=" * 60)
    try:
        print("正在生成标题，请稍候...")
        titles_response = call_xinghuo_api(title_prompt)
        print("✓ 标题生成完成")
        print()
        
        # 解析标题
        titles = parse_titles(titles_response)
        
        # 限制标题数量，只取前 title_count 个
        if len(titles) > title_count:
            print(f"⚠ 注意：AI生成了 {len(titles)} 个标题，将只使用前 {title_count} 个")
            titles = titles[:title_count]
        elif len(titles) < title_count:
            print(f"⚠ 注意：AI只生成了 {len(titles)} 个标题，少于要求的 {title_count} 个")
        
        print(f"生成标题数量: {len(titles)}")
        print("生成的标题:")
        for i, title in enumerate(titles, 1):
            print(f"  {i}. {title}")
        print()
        
        if not titles:
            print("❌ 未能解析出标题，原始响应:")
            print(titles_response)
            return
        
    except Exception as e:
        print(f"❌ 生成标题失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # 第六步：为每个标题生成文章提示词并生成文章
    print("=" * 60)
    print("第六步：生成文章生成专用提示词并生成文章")
    print("=" * 60)
    
    articles = []
    
    for i, title in enumerate(titles, 1):
        print(f"\n处理标题 {i}/{len(titles)}: {title}")
        
        try:
            # 生成文章提示词
            article_prompt = generate_article_prompt(title, core_keyword, target_keywords)
            
            # 调用AI生成文章
            print("  正在生成文章...")
            article_content = call_xinghuo_api(article_prompt)
            article_content = article_content.strip()
            
            # 评估文章质量
            print("  正在评估文章质量...")
            score_result = evaluate_article_quality(title, article_content, core_keyword, target_keywords, threshold=70)
            
            # 显示评分结果
            display_score_result(score_result)
            
            # 保存文章（包含评分）
            articles.append({
                "title": title,
                "content": article_content,
                "word_count": len(article_content),
                "quality_score": {
                    "overall_score": score_result['overall_score'],
                    "rule_score": score_result['rule_score'],
                    "ai_score": score_result.get('ai_score'),
                    "grade": score_result['grade']
                }
            })
            
            print(f"  ✓ 文章生成完成（{len(article_content)} 字符，质量评分：{score_result['overall_score']}分）")
            
            # 避免频率限制，添加延迟（QPS=2，所以至少间隔0.5秒）
            if i < len(titles):
                time.sleep(1)  # 等待1秒再生成下一篇
                
        except Exception as e:
            print(f"  ❌ 生成文章失败: {str(e)}")
            # 继续处理下一个标题
            continue
    
    # 第七步：保存结果
    print("\n" + "=" * 60)
    print("第七步：保存结果")
    print("=" * 60)
    
    result = {
        "core_keyword": core_keyword,
        "target_keywords": target_keywords,
        "title_count": title_count,
        "generated_titles": titles,
        "articles": articles,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 保存到JSON文件
    output_file = "batch_generate_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 结果已保存到: {output_file}")
    print(f"  生成标题数: {len(titles)}")
    print(f"  生成文章数: {len(articles)}")
    
    # 显示摘要
    print("\n" + "=" * 60)
    print("生成结果摘要")
    print("=" * 60)
    for i, article in enumerate(articles, 1):
        print(f"\n文章 {i}:")
        print(f"  标题: {article['title']}")
        print(f"  字数: {article['word_count']} 字符")
        if 'quality_score' in article:
            score = article['quality_score']
            print(f"  质量评分: {score['overall_score']}分 [{score['grade']}]")
        print(f"  正文预览: {article['content'][:100]}...")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_batch_generate()

