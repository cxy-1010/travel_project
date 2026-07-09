from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
import json
import os
import time
from pathlib import Path
from urllib.parse import quote
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import httpx
from openai import OpenAI

from .forms import LoginForm, ProfileForm, RegisterForm
from .models import UserProfile


HOTEL_SEARCH_CACHE = {}
HOTEL_SEARCH_CACHE_SECONDS = 15 * 60
FLIGHT_SEARCH_CACHE = {}
FLIGHT_SEARCH_CACHE_SECONDS = 15 * 60


TRAVEL_PACKAGES = [
    {
        'name': '希腊圣托里尼火山海景 6 日',
        'price': '¥8,999 起',
        'image_url': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=900&q=80',
        'fallback_image': 'images/packages/p1.jpg',
        'duration': '6 天 5 晚',
        'hotel': '悬崖海景酒店',
        'transport': '接送机 + 岛内用车',
        'meal': '特色晚餐 + 酒庄体验',
        'rating': 5,
        'reviews': 2680,
    },
    {
        'name': '日本京都古都文化 5 日',
        'price': '¥6,499 起',
        'image_url': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=900&q=80',
        'fallback_image': 'images/packages/p2.jpg',
        'duration': '5 天 4 晚',
        'hotel': '市中心精选酒店',
        'transport': '关西机场接送',
        'meal': '茶道 + 和风料理',
        'rating': 5,
        'reviews': 2146,
    },
    {
        'name': '巴厘岛海岸与乌布疗愈 6 日',
        'price': '¥7,299 起',
        'image_url': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=900&q=80',
        'fallback_image': 'images/packages/p3.jpg',
        'duration': '6 天 5 晚',
        'hotel': '泳池度假酒店',
        'transport': '专车环岛游',
        'meal': '海景下午茶 + 当地餐',
        'rating': 5,
        'reviews': 3098,
    },
    {
        'name': '瑞士少女峰全景列车 7 日',
        'price': '¥16,800 起',
        'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=900&q=80',
        'fallback_image': 'images/packages/p4.jpg',
        'duration': '7 天 6 晚',
        'hotel': '湖区精品酒店',
        'transport': '瑞士铁路通票',
        'meal': '山景早餐 + 奶酪火锅',
        'rating': 5,
        'reviews': 1864,
    },
    {
        'name': '巴黎艺术与塞纳河漫游 5 日',
        'price': '¥9,699 起',
        'image_url': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=900&q=80',
        'fallback_image': 'images/packages/p5.jpg',
        'duration': '5 天 4 晚',
        'hotel': '左岸或歌剧院商圈',
        'transport': '市区交通卡',
        'meal': '法式甜点 + 塞纳河晚餐',
        'rating': 5,
        'reviews': 2410,
    },
    {
        'name': '马尔代夫双人岛屿假期 6 日',
        'price': '¥14,999 起',
        'image_url': 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?auto=format&fit=crop&w=900&q=80',
        'fallback_image': 'images/packages/p6.jpg',
        'duration': '6 天 4 晚',
        'hotel': '沙屋/水屋可选',
        'transport': '快艇或水飞接驳',
        'meal': '早晚餐 + 浮潜体验',
        'rating': 5,
        'reviews': 3342,
    },
]


HOT_DESTINATIONS = [
    {
        'name': '中国',
        'image_url': 'https://unsplash.com/photos/nbEW8E9Qv9Y/download?force=true&w=1200',
        'fallback_image': 'images/gallary/g1.jpg',
        'routes': 28,
        'spots': 18,
        'column_class': 'col-md-6',
    },
    {
        'name': '委内瑞拉',
        'image_url': 'https://static.wixstatic.com/media/6233c4_b8a116b3ca224ba0b7f2296b8eb937de~mv2.jpg/v1/fill/w_980,h_653,al_c,q_85,enc_avif,quality_auto/6233c4_b8a116b3ca224ba0b7f2296b8eb937de~mv2.jpg',
        'fallback_image': 'images/gallary/g2.jpg',
        'routes': 12,
        'spots': 9,
        'column_class': 'col-md-6',
    },
    {
        'name': '巴西',
        'image_url': 'https://images.unsplash.com/photo-1483729558449-99ef09a8c325?auto=format&fit=crop&w=900&q=80',
        'fallback_image': 'images/gallary/g3.jpg',
        'routes': 25,
        'spots': 14,
        'column_class': 'col-md-4',
    },
    {
        'name': '澳大利亚',
        'image_url': 'https://unsplash.com/photos/ZcAO4WHha84/download?force=true&w=1200',
        'fallback_image': 'images/gallary/g4.jpg',
        'routes': 18,
        'spots': 11,
        'column_class': 'col-md-4',
    },
    {
        'name': '荷兰',
        'image_url': 'https://unsplash.com/photos/_3QAUzIvqj0/download?force=true&w=1200',
        'fallback_image': 'images/gallary/g5.jpg',
        'routes': 14,
        'spots': 12,
        'column_class': 'col-md-4',
    },
    {
        'name': '土耳其',
        'image_url': 'https://unsplash.com/photos/7ng3ISrlg1I/download?force=true&w=1200',
        'fallback_image': 'images/gallary/g6.jpg',
        'routes': 16,
        'spots': 8,
        'column_class': 'col-md-8',
    },
]


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
    return render(
        request,
        'index.html',
        {
            'travel_packages': TRAVEL_PACKAGES,
            'hot_destinations': HOT_DESTINATIONS,
        },
    )


def destination_packages(request, destination):
    destination_name = destination.strip()
    selected_destination = next(
        (item for item in HOT_DESTINATIONS if item['name'] == destination_name),
        None,
    )
    if selected_destination is None:
        selected_destination = {
            'name': destination_name,
            'image_url': 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1400&q=80',
            'fallback_image': 'images/home/banner.jpg',
            'routes': 8,
            'spots': 6,
        }

    packages = build_destination_packages(selected_destination['name'])
    return render(
        request,
        'destination_packages.html',
        {
            'destination': selected_destination,
            'packages': packages,
        },
    )


def build_destination_packages(destination_name):
    destination_package_map = {
        '中国': [
            {
                'name': '北京古都与长城 5 日',
                'price': '¥3,999 起',
                'image_url': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?auto=format&fit=crop&w=900&q=80',
                'duration': '5 天 4 晚',
                'highlights': ['故宫深度讲解', '慕田峪长城', '胡同文化体验'],
                'hotel': '四星精选酒店',
                'transport': '市区专车接驳',
            },
            {
                'name': '云南昆明大理丽江 7 日',
                'price': '¥5,699 起',
                'image_url': 'https://images.unsplash.com/photo-1528181304800-259b08848526?auto=format&fit=crop&w=900&q=80',
                'duration': '7 天 6 晚',
                'highlights': ['洱海旅拍', '丽江古城', '玉龙雪山'],
                'hotel': '古城客栈 + 度假酒店',
                'transport': '当地用车 + 城际交通',
            },
            {
                'name': '桂林阳朔山水 4 日',
                'price': '¥2,899 起',
                'image_url': 'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=900&q=80',
                'duration': '4 天 3 晚',
                'highlights': ['漓江竹筏', '阳朔西街', '喀斯特峰林'],
                'hotel': '山景精品酒店',
                'transport': '桂林接送站',
            },
        ],
        '委内瑞拉': [
            {
                'name': '天使瀑布与卡奈玛探险 6 日',
                'price': '¥18,800 起',
                'image_url': 'https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=900&q=80',
                'duration': '6 天 5 晚',
                'highlights': ['天使瀑布观景', '卡奈玛泻湖', '雨林轻徒步'],
                'hotel': '生态营地 + 城市酒店',
                'transport': '内陆航班 + 当地船只',
            },
            {
                'name': '罗赖马山徒步 8 日',
                'price': '¥21,600 起',
                'image_url': 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=80',
                'duration': '8 天 7 晚',
                'highlights': ['桌山徒步', '高原奇景', '专业向导陪同'],
                'hotel': '露营 + 城市酒店',
                'transport': '越野车接驳',
            },
            {
                'name': '加勒比海岸轻奢假期 5 日',
                'price': '¥12,900 起',
                'image_url': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=900&q=80',
                'duration': '5 天 4 晚',
                'highlights': ['海岛浮潜', '落日晚餐', '海岸小镇漫游'],
                'hotel': '海滨度假酒店',
                'transport': '机场接送 + 岛内用车',
            },
        ],
        '巴西': [
            {
                'name': '里约热内卢城市经典 5 日',
                'price': '¥10,999 起',
                'image_url': 'https://images.unsplash.com/photo-1483729558449-99ef09a8c325?auto=format&fit=crop&w=900&q=80',
                'duration': '5 天 4 晚',
                'highlights': ['基督像', '面包山缆车', '科帕卡巴纳海滩'],
                'hotel': '海滩商圈酒店',
                'transport': '市区专车',
            },
            {
                'name': '伊瓜苏瀑布奇观 4 日',
                'price': '¥8,699 起',
                'image_url': 'https://images.unsplash.com/photo-1520960683738-55ab77f2bc0d?auto=format&fit=crop&w=900&q=80',
                'duration': '4 天 3 晚',
                'highlights': ['瀑布双侧观景', '鸟园', '雨林步道'],
                'hotel': '瀑布区精选酒店',
                'transport': '机场接送 + 景区交通',
            },
            {
                'name': '亚马逊雨林生态 6 日',
                'price': '¥14,500 起',
                'image_url': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=900&q=80',
                'duration': '6 天 5 晚',
                'highlights': ['雨林游船', '夜观生态', '当地社区访问'],
                'hotel': '雨林 Lodge',
                'transport': '内陆航班 + 船只',
            },
        ],
        '澳大利亚': [
            {
                'name': '悉尼海港与蓝山 5 日',
                'price': '¥9,999 起',
                'image_url': 'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?auto=format&fit=crop&w=900&q=80',
                'duration': '5 天 4 晚',
                'highlights': ['悉尼歌剧院', '海港游船', '蓝山国家公园'],
                'hotel': '市中心四星酒店',
                'transport': '机场接送 + 蓝山一日车',
            },
            {
                'name': '大堡礁潜水假期 6 日',
                'price': '¥13,800 起',
                'image_url': 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=900&q=80',
                'duration': '6 天 5 晚',
                'highlights': ['大堡礁出海', '浮潜体验', '凯恩斯雨林'],
                'hotel': '海滨度假酒店',
                'transport': '出海船票 + 接送',
            },
            {
                'name': '墨尔本大洋路 5 日',
                'price': '¥8,799 起',
                'image_url': 'https://images.unsplash.com/photo-1516941064643-74aacd84843c?auto=format&fit=crop&w=900&q=80',
                'duration': '5 天 4 晚',
                'highlights': ['大洋路', '十二门徒', '企鹅归巢'],
                'hotel': '墨尔本市区酒店',
                'transport': '当地一日游用车',
            },
        ],
        '荷兰': [
            {
                'name': '阿姆斯特丹运河与博物馆 4 日',
                'price': '¥7,299 起',
                'image_url': 'https://images.unsplash.com/photo-1512470876302-972faa2aa9a4?auto=format&fit=crop&w=900&q=80',
                'duration': '4 天 3 晚',
                'highlights': ['运河游船', '梵高博物馆', '老城漫步'],
                'hotel': '运河区精品酒店',
                'transport': '城市交通卡',
            },
            {
                'name': '荷兰花田与风车 5 日',
                'price': '¥8,199 起',
                'image_url': 'https://images.unsplash.com/photo-1494783367193-149034c05e8f?auto=format&fit=crop&w=900&q=80',
                'duration': '5 天 4 晚',
                'highlights': ['库肯霍夫花园', '赞瑟斯汉斯风车村', '奶酪市集'],
                'hotel': '阿姆斯特丹精选酒店',
                'transport': '花田专车一日游',
            },
            {
                'name': '荷比小镇慢旅行 6 日',
                'price': '¥9,600 起',
                'image_url': 'https://images.unsplash.com/photo-1473959383416-8518a661bd9c?auto=format&fit=crop&w=900&q=80',
                'duration': '6 天 5 晚',
                'highlights': ['羊角村', '布鲁日', '鹿特丹建筑'],
                'hotel': '小镇精品住宿',
                'transport': '城际火车 + 当地接驳',
            },
        ],
        '土耳其': [
            {
                'name': '伊斯坦布尔与卡帕多奇亚 7 日',
                'price': '¥11,800 起',
                'image_url': 'https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?auto=format&fit=crop&w=900&q=80',
                'duration': '7 天 6 晚',
                'highlights': ['蓝色清真寺', '热气球体验', '地下城探访'],
                'hotel': '洞穴酒店 + 城市酒店',
                'transport': '内陆航班 + 当地用车',
            },
            {
                'name': '土耳其爱琴海岸 6 日',
                'price': '¥10,500 起',
                'image_url': 'https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=900&q=80',
                'duration': '6 天 5 晚',
                'highlights': ['以弗所古城', '棉花堡', '爱琴海小镇'],
                'hotel': '海岸度假酒店',
                'transport': '城市间专车',
            },
            {
                'name': '土耳其美食与市集 5 日',
                'price': '¥8,900 起',
                'image_url': 'https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b?auto=format&fit=crop&w=900&q=80',
                'duration': '5 天 4 晚',
                'highlights': ['大巴扎', '博斯普鲁斯海峡', '土耳其料理课'],
                'hotel': '老城精品酒店',
                'transport': '市区交通 + 接送机',
            },
        ],
    }
    return destination_package_map.get(destination_name, [
        {
            'name': f'{destination_name}精选深度游 5 日',
            'price': '¥6,999 起',
            'image_url': 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=80',
            'duration': '5 天 4 晚',
            'highlights': ['经典地标', '当地文化体验', '舒适自由时间'],
            'hotel': '精选舒适酒店',
            'transport': '当地接送服务',
        },
    ])


def ai_assistant(request):
    return render(request, 'ai_assistant.html')


def hotel_search(request):
    return render(request, 'hotel_search.html')


def flight_search(request):
    return render(request, 'flight_search.html')


class UserLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f'欢迎回来，{form.get_user().username}！')
        return super().form_valid(form)


def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功，已为您自动登录。')
            return redirect('index')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, '您已安全退出登录。')
    return redirect(reverse_lazy('index'))


@login_required
def profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'avatar_url': '',
            'preferred_currency': 'CNY',
            'bio': '',
        },
    )

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user_profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '个人信息已更新。')
            return redirect('profile')
    else:
        form = ProfileForm(instance=user_profile, user=request.user)

    return render(request, 'profile.html', {'form': form, 'profile': user_profile})


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
