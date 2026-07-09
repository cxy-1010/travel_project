from django.shortcuts import render
import json
import os
import time
from pathlib import Path
from urllib.parse import quote
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import httpx
from openai import OpenAI


HOTEL_SEARCH_CACHE = {}
HOTEL_SEARCH_CACHE_SECONDS = 15 * 60
FLIGHT_SEARCH_CACHE = {}
FLIGHT_SEARCH_CACHE_SECONDS = 15 * 60


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


def flight_search(request):
    return render(request, 'flight_search.html')


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


def create_deepseek_completion(api_key, prompt, ignore_system_proxy=False, reasoning_effort="low"):
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
        temperature=0.2,
        max_tokens=2200,
        reasoning_effort=reasoning_effort,
        extra_body={"thinking": {"type": "disabled"}}
    )


def create_deepseek_hotel_stream(api_key, prompt, ignore_system_proxy=False):
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
            {"role": "system", "content": "你是酒店搜索助手。必须严格服从目标城市，只输出 NDJSON，每行一个 JSON 对象，不要 markdown，不要解释。"},
            {"role": "user", "content": prompt}
        ],
        stream=True,
        temperature=0.2,
        max_tokens=2200,
        reasoning_effort="low",
        extra_body={"thinking": {"type": "disabled"}}
    )


def create_deepseek_flight_stream(api_key, prompt, ignore_system_proxy=False):
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
            {"role": "system", "content": "你是特价机票搜索助手。只输出 NDJSON，每行一个 JSON 对象，不要 markdown，不要解释。"},
            {"role": "user", "content": prompt}
        ],
        stream=True,
        temperature=0.2,
        max_tokens=2200,
        reasoning_effort="low",
        extra_body={"thinking": {"type": "disabled"}}
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
    cache_key = (city, check_in, check_out, guests, keyword)
    cached = HOTEL_SEARCH_CACHE.get(cache_key)

    prompt = f"""
目标城市只能是：{city}
请为用户快速查找“{city}”本地的 8-10 家酒店候选。
入住：{check_in or '未填写'}，退房：{check_out or '未填写'}，人数：{guests or '未填写'}，关键词：{keyword or '无'}。
要求：
1. 输出 NDJSON，不要 markdown，不要数组。每一行是一个完整 JSON 对象。
2. 每项字段：name, area, price, rating, reviewCount, room, tags, detailUrl, imageQuery。
3. name 或 area 必须能看出属于“{city}”，禁止返回北京、上海、广州、深圳等其他城市酒店。
4. detailUrl 直接使用包含“{city}+酒店名+酒店 官网”的 Bing 搜索网址即可，优先保证快和可打开。
5. imageQuery 写适合搜索酒店图片的关键词，必须包含“{city}”。
6. price 是数字，rating 是 4.1-4.9 数字，reviewCount 是数字，tags 是字符串数组。
7. 如果无法确认真实酒店，也必须围绕“{city}”返回候选，不要使用其他城市示例。
8. 禁止使用“??”“某城市”“目标城市”等占位文字，必须写出真实城市名“{city}”。
9. 不要等待全部想完，先输出最确定的酒店；每写完一行就继续下一行。
"""

    def event_stream():
        def send(payload):
            return "data: " + json.dumps(payload, ensure_ascii=False) + "\n\n"

        if cached and time.time() - cached['time'] < HOTEL_SEARCH_CACHE_SECONDS:
            yield send({"type": "start", "cached": True})
            for hotel in cached['hotels']:
                yield send({"type": "hotel", "hotel": hotel})
            yield send({"type": "done", "count": len(cached['hotels']), "cached": True})
            return

        api_key = get_deepseek_api_key()
        if not api_key:
            yield send({"type": "error", "content": "未配置 DEEPSEEK_API_KEY"})
            return

        hotels = []
        buffer = ''
        yielded_names = set()
        yield send({"type": "start"})
        yield send({"type": "status", "content": "AI 已连接，正在逐个生成酒店。"})

        try:
            try:
                response = create_deepseek_hotel_stream(api_key, prompt)
            except Exception:
                yield send({"type": "status", "content": "正在重试连接。"})
                response = create_deepseek_hotel_stream(api_key, prompt, ignore_system_proxy=True)

            for chunk in response:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content or ''
                if not content:
                    continue
                buffer += content
                lines = buffer.splitlines(keepends=True)
                buffer = ''
                for raw_line in lines:
                    if not raw_line.endswith(('\n', '\r')):
                        buffer += raw_line
                        continue
                    line = raw_line.strip().strip(',')
                    if not line or line in ('[', ']') or line.startswith('```'):
                        continue
                    if line.startswith('data:'):
                        line = line[5:].strip()
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    cleaned = clean_hotel_results([item], city)
                    if not cleaned:
                        continue
                    hotel = cleaned[0]
                    name = hotel.get('name', '')
                    if name in yielded_names:
                        continue
                    yielded_names.add(name)
                    hotels.append(hotel)
                    yield send({"type": "hotel", "hotel": hotel})

            trailing = buffer.strip().strip(',')
            if trailing and trailing not in ('[', ']'):
                try:
                    item = json.loads(trailing)
                    cleaned = clean_hotel_results([item], city)
                    if cleaned and cleaned[0].get('name', '') not in yielded_names:
                        hotels.append(cleaned[0])
                        yield send({"type": "hotel", "hotel": cleaned[0]})
                except json.JSONDecodeError:
                    pass

            if hotels:
                HOTEL_SEARCH_CACHE[cache_key] = {'time': time.time(), 'hotels': hotels}
            yield send({"type": "done", "count": len(hotels)})
        except Exception:
            yield send({"type": "error", "content": "AI 酒店查找失败，请检查网络或 DeepSeek 配置后重试。"})

    resp = StreamingHttpResponse(
        streaming_content=event_stream(),
        content_type='text/event-stream'
    )
    resp['Cache-Control'] = 'no-cache'
    resp['X-Accel-Buffering'] = 'no'
    return resp


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


def clean_flight_results(flights, origin, destination):
    cleaned = []
    fallback_detail_url = 'https://www.bing.com/search?q=' + quote(f'{origin} 到 {destination} 机票 预订')
    for index, item in enumerate(flights):
        if not isinstance(item, dict):
            continue
        airline = str(item.get('airline') or '特价航班').strip()
        code = str(item.get('code') or f'TN{1200 + index * 17}').strip()
        depart_time = str(item.get('departTime') or item.get('departureTime') or '08:30').strip()
        arrive_time = str(item.get('arriveTime') or item.get('arrivalTime') or '10:45').strip()
        from_airport = str(item.get('fromAirport') or f'{origin}机场').strip()
        to_airport = str(item.get('toAirport') or f'{destination}机场').strip()
        try:
            price = int(float(item.get('price') or 699))
        except (TypeError, ValueError):
            price = 699
        try:
            duration = int(float(item.get('duration') or item.get('durationMinutes') or 135))
        except (TypeError, ValueError):
            duration = 135
        direct = item.get('direct')
        if direct is None:
            direct = '中转' not in str(item.get('stops') or item.get('discount') or '')
        tags = item.get('tags')
        if not isinstance(tags, list):
            tags = ['直飞' if direct else '1次中转', '特价']
        detail_url = str(item.get('detailUrl') or '').strip()
        if (
            not detail_url.startswith(('http://', 'https://'))
            or 'ctrip.com/flights/' in detail_url
            or 'flights.ctrip.com/online/list' in detail_url
        ):
            detail_url = fallback_detail_url
        cleaned.append({
            'airline': airline,
            'code': code,
            'fromAirport': from_airport,
            'toAirport': to_airport,
            'departTime': depart_time,
            'arriveTime': arrive_time,
            'duration': duration,
            'direct': bool(direct),
            'price': price,
            'discount': str(item.get('discount') or ('低价直飞' if direct else '中转特惠')).strip(),
            'tags': [str(tag).strip() for tag in tags[:4] if str(tag).strip()],
            'detailUrl': detail_url,
        })
    cleaned.sort(key=lambda flight: flight['price'])
    return cleaned[:20]


@csrf_exempt
def flight_ai_search(request):
    if request.method != 'POST':
        return JsonResponse({'error': '仅支持 POST 请求'}, status=405)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        data = request.POST.dict()

    def _s(v):
        return str(v).strip() if v is not None else ''

    origin = _s(data.get('from')) or '北京'
    destination = _s(data.get('to')) or '上海'
    departure = _s(data.get('departure'))
    return_date = _s(data.get('return'))
    adults = _s(data.get('adults')) or '1'
    children = _s(data.get('children')) or '0'
    cabin = _s(data.get('cabin')) or '经济舱'
    trip_type = _s(data.get('trip_type')) or 'round'
    cache_key = (origin, destination, departure, return_date, adults, children, cabin, trip_type)
    cached = FLIGHT_SEARCH_CACHE.get(cache_key)

    prompt = f"""
请为用户查找特价机票候选，按价格从低到高输出 8-10 个航班。
出发城市：{origin}
到达城市：{destination}
出发日期：{departure or '未填写'}
返回日期：{return_date or '未填写'}
类型：{'单程' if trip_type == 'oneway' else '往返'}
乘客：成人 {adults}，儿童 {children}
舱位：{cabin}

要求：
1. 输出 NDJSON，不要 markdown，不要数组。每一行是一个完整 JSON 对象。
2. 每项字段：airline, code, fromAirport, toAirport, departTime, arriveTime, duration, direct, price, discount, tags, detailUrl。
3. price 必须是数字人民币价格，duration 是分钟数，direct 是 true/false，tags 是字符串数组。
4. detailUrl 必须使用 Bing 搜索网址，搜索词为“{origin} 到 {destination} 机票 预订”，不要输出携程直达 URL。
5. 不要输出解释。先输出最便宜、最确定的航班，每写完一行立刻继续下一行。
"""

    def event_stream():
        def send(payload):
            return "data: " + json.dumps(payload, ensure_ascii=False) + "\n\n"

        if cached and time.time() - cached['time'] < FLIGHT_SEARCH_CACHE_SECONDS:
            yield send({"type": "start", "cached": True})
            for flight in cached['flights']:
                yield send({"type": "flight", "flight": flight})
            yield send({"type": "done", "count": len(cached['flights']), "cached": True})
            return

        api_key = get_deepseek_api_key()
        if not api_key:
            yield send({"type": "error", "content": "未配置 DEEPSEEK_API_KEY"})
            return

        flights = []
        buffer = ''
        yielded_codes = set()
        yield send({"type": "start"})
        yield send({"type": "status", "content": "AI 已连接，正在按价格生成特价机票。"})

        try:
            try:
                response = create_deepseek_flight_stream(api_key, prompt)
            except Exception:
                yield send({"type": "status", "content": "正在重试连接。"})
                response = create_deepseek_flight_stream(api_key, prompt, ignore_system_proxy=True)

            for chunk in response:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content or ''
                if not content:
                    continue
                buffer += content
                lines = buffer.splitlines(keepends=True)
                buffer = ''
                for raw_line in lines:
                    if not raw_line.endswith(('\n', '\r')):
                        buffer += raw_line
                        continue
                    line = raw_line.strip().strip(',')
                    if not line or line in ('[', ']') or line.startswith('```'):
                        continue
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    cleaned = clean_flight_results([item], origin, destination)
                    if not cleaned:
                        continue
                    flight = cleaned[0]
                    code = flight.get('code', '')
                    if code in yielded_codes:
                        continue
                    yielded_codes.add(code)
                    flights.append(flight)
                    flights.sort(key=lambda value: value['price'])
                    yield send({"type": "flight", "flight": flight})

            if flights:
                FLIGHT_SEARCH_CACHE[cache_key] = {'time': time.time(), 'flights': clean_flight_results(flights, origin, destination)}
            yield send({"type": "done", "count": len(flights)})
        except Exception:
            yield send({"type": "error", "content": "AI 机票查找失败，请检查网络或 DeepSeek 配置后重试。"})

    resp = StreamingHttpResponse(
        streaming_content=event_stream(),
        content_type='text/event-stream'
    )
    resp['Cache-Control'] = 'no-cache'
    resp['X-Accel-Buffering'] = 'no'
    return resp


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
