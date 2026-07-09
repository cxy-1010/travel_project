from django.shortcuts import render
import json
import os
from pathlib import Path
from urllib.parse import quote
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import httpx
from openai import OpenAI


def get_deepseek_api_key():
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if api_key:
        return api_key.strip()

    env_path = Path(__file__).resolve().parent.parent / '.env'
    if not env_path.exists():
        return ''

    for line in env_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        if key.strip().lstrip('\ufeff') == 'DEEPSEEK_API_KEY':
            return value.strip().strip('"').strip("'")
    return ''


def index(request):
    return render(request, 'index.html')


def ai_assistant(request):
    return render(request, 'ai_assistant.html')


def hotel_search(request):
    return render(request, 'hotel_search.html')


def create_deepseek_stream(api_key, prompt, ignore_system_proxy=False):
    http_client = None
    if ignore_system_proxy:
        http_client = httpx.Client(timeout=60.0, trust_env=False)

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
        http_client=http_client,
    )
    return client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content": "你是一位专业的旅游规划顾问，请用中文回复。"},
            {"role": "user", "content": prompt}
        ],
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )


def create_deepseek_completion(api_key, prompt, ignore_system_proxy=False):
    http_client = None
    if ignore_system_proxy:
        http_client = httpx.Client(timeout=60.0, trust_env=False)

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
        http_client=http_client,
    )
    return client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content": "你是酒店搜索助手。必须严格服从目标城市，只返回 JSON 数组，不要输出解释。"},
            {"role": "user", "content": prompt}
        ],
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )


@csrf_exempt
def hotel_ai_search(request):
    if request.method != 'POST':
        return JsonResponse({'error': '仅支持 POST 请求'}, status=405)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        data = request.POST.dict()

    def _s(v):
        return str(v).strip() if v is not None else ''

    city = _s(data.get('city')) or '上海'
    check_in = _s(data.get('check_in'))
    check_out = _s(data.get('check_out'))
    guests = _s(data.get('guests'))
    keyword = _s(data.get('keyword'))

    api_key = get_deepseek_api_key()
    if not api_key:
        return JsonResponse({'error': '未配置 DEEPSEEK_API_KEY'}, status=400)

    prompt = f"""
目标城市只能是：{city}
请为用户查找“{city}”本地的 12-18 家酒店候选。
入住：{check_in or '未填写'}，退房：{check_out or '未填写'}，人数：{guests or '未填写'}，关键词：{keyword or '无'}。
要求：
1. 返回 JSON 数组，不要 markdown。
2. 每项字段：name, area, price, rating, reviewCount, room, tags, reason, detailUrl, imageQuery。
3. name 或 area 必须能看出属于“{city}”，禁止返回北京、上海、广州、深圳等其他城市酒店。
4. detailUrl 必须是可访问的搜索/介绍网址，优先用酒店官网、Google/Bing搜索；不确定官网时用包含“{city}+酒店名”的 Bing 搜索网址。
5. imageQuery 写适合搜索酒店图片的关键词，必须包含“{city}”。
6. price 是数字，rating 是 4.1-4.9 数字，reviewCount 是数字，tags 是字符串数组。
7. 如果无法确认真实酒店，也必须围绕“{city}”返回候选，不要使用其他城市示例。
8. 禁止使用“??”“某城市”“目标城市”等占位文字，必须写出真实城市名“{city}”。
"""

    try:
        try:
            result = create_deepseek_completion(api_key, prompt)
        except Exception:
            result = create_deepseek_completion(api_key, prompt, ignore_system_proxy=True)
        content = result.choices[0].message.content or '[]'
        content = content.strip()
        if content.startswith('```'):
            content = content.strip('`')
            content = content.replace('json', '', 1).strip()
        start = content.find('[')
        end = content.rfind(']')
        if start != -1 and end != -1 and end > start:
            content = content[start:end + 1]
        hotels = json.loads(content)
        if not isinstance(hotels, list):
            hotels = []
        hotels = clean_hotel_results(hotels, city)
        return JsonResponse({'hotels': hotels})
    except Exception as e:
        return JsonResponse({
            'error': 'AI 酒店查找失败',
            'detail': str(e),
        }, status=500)


def clean_hotel_results(hotels, city):
    wrong_city_words = [
        '北京', '上海', '广州', '深圳', '杭州', '成都', '重庆', '西安', '南京', '武汉',
        '天津', '苏州', '厦门', '青岛', '长沙', '郑州', '三亚', '哈尔滨'
    ]
    wrong_city_words = [word for word in wrong_city_words if word not in city]
    cleaned = []
    for item in hotels:
        if not isinstance(item, dict):
            continue
        text = f"{item.get('name', '')} {item.get('area', '')} {item.get('detailUrl', '')}"
        if any(word in text for word in wrong_city_words):
            continue
        name = str(item.get('name') or f'{city}精选酒店').strip()
        area = str(item.get('area') or f'{city}市中心').strip()
        name = name.replace('??', city).replace('某城市', city).replace('目标城市', city)
        area = area.replace('??', city).replace('某城市', city).replace('目标城市', city)
        if city not in name and city not in area:
            area = f'{city} · {area}'
        detail_url = str(item.get('detailUrl') or '').strip()
        detail_url_has_placeholder = any(token in detail_url for token in ('??', '%3F', '%3f', '某城市', '目标城市'))
        if (
            not detail_url.startswith(('http://', 'https://'))
            or any(word in detail_url for word in wrong_city_words)
            or detail_url_has_placeholder
        ):
            detail_url = 'https://www.bing.com/search?q=' + quote(f'{city} {name} 酒店 官网')
        image_query = str(item.get('imageQuery') or name).strip()
        if city not in image_query:
            image_query = f'{city} {image_query}'
        item['name'] = name
        item['area'] = area
        item['detailUrl'] = detail_url
        item['imageQuery'] = image_query
        cleaned.append(item)
    return cleaned[:20]


@csrf_exempt
def search_ai(request):
    """AI 智能搜索：接收前端搜索表单数据，通过 DeepSeek API 流式返回规划结果"""
    try:
        if request.method != 'POST':
            return JsonResponse({'error': '仅支持 POST 请求'}, status=405)

        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, TypeError):
            data = request.POST.dict()

        def _s(v):
            return str(v).strip() if v is not None else ''

        country = _s(data.get('country'))
        city = _s(data.get('city'))
        check_in = _s(data.get('check_in'))
        check_out = _s(data.get('check_out'))
        days = _s(data.get('days'))
        people = _s(data.get('people'))
        budget = _s(data.get('budget'))
        message = _s(data.get('message'))
        previous_plan = _s(data.get('previous_plan'))

        prompt_parts = [
            "你是旅游路线规划助手。请用中文，简洁清楚地规划路线。",
            "",
            "用户需求：",
        ]
        if country:
            prompt_parts.append(f"- 目标国家/地区：{country}")
        if city:
            prompt_parts.append(f"- 目标城市：{city}")
        if check_in:
            prompt_parts.append(f"- 出发日期：{check_in}")
        if check_out:
            prompt_parts.append(f"- 返回日期：{check_out}")
        if days:
            prompt_parts.append(f"- 出行天数：{days}")
        if people:
            prompt_parts.append(f"- 出行人数：{people}")
        if budget:
            prompt_parts.append(f"- 预算：{budget}")
        if previous_plan:
            prompt_parts.extend(["", "上一版方案：", previous_plan[:4000]])
        if message:
            prompt_parts.extend(["", "用户修改要求：", message])

        prompt_parts.extend([
            "",
            "输出格式：",
            "1. 先给 1 段总览。",
            "2. 按“第1天 / 第2天...”列行程。",
            "3. 每个景点后加一个可访问的介绍网址，格式必须是：[景点介绍](https://...)。",
            "4. 最后给住宿区域、交通和预算提醒。",
            "5. 如果用户要求修改路线，请直接输出修改后的新版方案，不要解释太多。",
        ])

        prompt = "\n".join(prompt_parts)

        def event_stream():
            api_key = get_deepseek_api_key()
            if not api_key:
                yield "data: " + json.dumps({"type": "error", "content": "未配置 DEEPSEEK_API_KEY，请在项目根目录 .env 中填写"}) + "\n\n"
                return

            try:
                try:
                    response = create_deepseek_stream(api_key, prompt)
                except Exception as first_error:
                    response = create_deepseek_stream(api_key, prompt, ignore_system_proxy=True)

                yield "data: " + json.dumps({"type": "start"}) + "\n\n"

                for chunk in response:
                    if not chunk.choices:
                        continue
                    delta = chunk.choices[0].delta
                    reasoning = getattr(delta, 'reasoning_content', None) or ''
                    if reasoning:
                        yield "data: " + json.dumps({"type": "reasoning", "content": reasoning}) + "\n\n"
                    content = delta.content or ''
                    if content:
                        yield "data: " + json.dumps({"type": "content", "content": content}) + "\n\n"

                yield "data: " + json.dumps({"type": "done"}) + "\n\n"

            except Exception as e:
                hint = (
                    "AI 调用失败：无法连接 DeepSeek。\n"
                    "这通常不是 API key 错误，而是当前设备的网络/代理/VPN 无法完成 HTTPS 连接。\n"
                    "请检查：1. 浏览器能否访问 https://api.deepseek.com；"
                    "2. 系统代理或 VPN 是否允许 Python 访问；"
                    "3. 如使用 Clash/代理软件，请开启 TUN 或为 Python 配置正确代理。\n"
                    f"原始错误：{e}"
                )
                yield "data: " + json.dumps({"type": "error", "content": hint}) + "\n\n"

        resp = StreamingHttpResponse(
            streaming_content=event_stream(),
            content_type='text/event-stream'
        )
        resp['Cache-Control'] = 'no-cache'
        resp['X-Accel-Buffering'] = 'no'
        return resp

    except Exception as e:
        import traceback
        return JsonResponse({
            'error': '服务器内部错误',
            'detail': str(e),
            'traceback': traceback.format_exc()
        }, status=500)
