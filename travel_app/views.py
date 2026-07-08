from django.shortcuts import render
import json
import os
from pathlib import Path
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

        prompt_parts = [
            "你是一位专业的旅游规划顾问。请根据用户的出行需求，详细规划一份旅游行程方案。",
            "",
            "=== 用户出行需求 ===",
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
            prompt_parts.append(f"- 预算范围：{budget}")

        prompt_parts.extend([
            "",
            "=== 请提供以下方面建议 ===",
            "1. 行程安排 - 按天逐日规划，含每日景点和活动",
            "2. 住宿推荐 - 2~3 个适合预算的酒店",
            "3. 景点推荐 - 必去和备选景点",
            "4. 美食推荐 - 当地特色美食和餐厅",
            "5. 交通建议 - 出行交通方案",
            "6. 预算分配 - 按类别分配",
            "7. 出行小贴士 - 气候、签证、安全等",
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
