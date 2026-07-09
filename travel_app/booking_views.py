import json
import random
from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .forms import LoginForm, ProfileForm, RegisterForm, TravelBookingForm
from .models import EmailVerificationCode, TravelBooking, TravelPackage, UserProfile


TRAVEL_PACKAGES = [
    {
        'id': 'santorini-volcano-sea',
        'name': '希腊圣托里尼火山海景 6 日',
        'destination': '希腊',
        'price': '¥8,999 起',
        'image_url': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=900&q=80',
        'fallback_image': 'images/packages/p1.jpg',
        'duration': '6 天 5 晚',
        'hotel': '悬崖海景酒店',
        'transport': '接送机 + 岛内用车',
        'meal': '特色晚餐 + 酒庄体验',
        'rating': 5,
        'reviews': 2680,
        'highlights': ['火山海景', '悬崖酒店', '爱琴海日落'],
    },
    {
        'id': 'kyoto-culture',
        'name': '日本京都古都文化 5 日',
        'destination': '日本',
        'price': '¥6,499 起',
        'image_url': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=900&q=80',
        'fallback_image': 'images/packages/p2.jpg',
        'duration': '5 天 4 晚',
        'hotel': '市中心精选酒店',
        'transport': '关西机场接送',
        'meal': '茶道 + 和风料理',
        'rating': 5,
        'reviews': 2146,
        'highlights': ['清水寺', '伏见稻荷', '和风体验'],
    },
    {
        'id': 'bali-ubud-coast',
        'name': '巴厘岛海岸与乌布疗愈 6 日',
        'destination': '巴厘岛',
        'price': '¥7,299 起',
        'image_url': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=900&q=80',
        'fallback_image': 'images/packages/p3.jpg',
        'duration': '6 天 5 晚',
        'hotel': '泳池度假酒店',
        'transport': '专车环岛游',
        'meal': '海景下午茶 + 当地餐',
        'rating': 5,
        'reviews': 3098,
        'highlights': ['海岸落日', '乌布稻田', '度假酒店'],
    },
    {
        'id': 'swiss-alps-train',
        'name': '瑞士少女峰全景列车 7 日',
        'destination': '瑞士',
        'price': '¥16,800 起',
        'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=900&q=80',
        'fallback_image': 'images/packages/p4.jpg',
        'duration': '7 天 6 晚',
        'hotel': '湖区精品酒店',
        'transport': '瑞士铁路通票',
        'meal': '山景早餐 + 奶酪火锅',
        'rating': 5,
        'reviews': 1864,
        'highlights': ['少女峰', '全景列车', '湖区住宿'],
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
        'name': '日本',
        'image_url': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=900&q=80',
        'fallback_image': 'images/gallary/g2.jpg',
        'routes': 12,
        'spots': 9,
        'column_class': 'col-md-6',
    },
    {
        'name': '澳大利亚',
        'image_url': 'https://unsplash.com/photos/ZcAO4WHha84/download?force=true&w=1200',
        'fallback_image': 'images/gallary/g4.jpg',
        'routes': 18,
        'spots': 11,
        'column_class': 'col-md-4',
    },
]


def package_to_dict(package):
    if isinstance(package, TravelPackage):
        return package.to_card_dict()
    return package


def get_featured_packages(limit=6):
    packages = list(
        TravelPackage.objects.filter(is_active=True, is_featured=True).order_by('display_order', 'id')
    )
    if packages:
        return [package.to_card_dict() for package in packages[:limit]]
    return TRAVEL_PACKAGES[:limit]


def get_home_package(package_id):
    package = TravelPackage.objects.filter(slug=package_id, is_active=True).first()
    if package:
        return package.to_card_dict()
    return next((package for package in TRAVEL_PACKAGES if package['id'] == package_id), None)


def packages_page(request):
    return render(request, 'destination_packages.html', {
        'destination': {
            'name': '精选套餐',
            'image_url': 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1400&q=80',
            'fallback_image': 'images/home/banner.jpg',
            'routes': len(get_featured_packages(12)),
            'spots': 8,
        },
        'packages': get_featured_packages(12),
    })


@login_required
def book_package(request, package_id):
    package = get_home_package(package_id)
    if package is None:
        messages.error(request, '未找到该旅游套餐，请重新选择。')
        return redirect('packages')

    if request.method == 'POST':
        form = TravelBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.package_id = package['id']
            booking.package_name = package['name']
            booking.destination = package.get('destination') or package['name'].split(' ')[0]
            booking.price = package['price']
            booking.duration = package['duration']
            booking.hotel = package.get('hotel', '')
            booking.transport = package.get('transport', '')
            booking.meal = package.get('meal', '')
            booking.image_url = package.get('image_url', '')
            booking.status = 'confirmed'
            booking.save()
            messages.success(request, '预订成功，已保存到您的个人中心。')
            return redirect('my_bookings')
    else:
        initial_phone = ''
        if hasattr(request.user, 'profile'):
            initial_phone = request.user.profile.phone
        form = TravelBookingForm(initial={'travelers': 1, 'contact_phone': initial_phone})

    return render(request, 'book_package.html', {'package': package, 'form': form})


@login_required
def my_bookings(request):
    bookings = TravelBooking.objects.filter(user=request.user)
    return render(request, 'my_bookings.html', {'bookings': bookings})


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(TravelBooking, pk=booking_id, user=request.user)
    return render(request, 'booking_detail.html', {'booking': booking})


def destination_packages(request, destination):
    destination_name = destination.strip()
    packages = [
        package.to_card_dict()
        for package in TravelPackage.objects.filter(is_active=True, destination=destination_name)[:12]
    ]
    if not packages:
        packages = build_destination_packages(destination_name)
    return render(request, 'destination_packages.html', {
        'destination': {
            'name': destination_name,
            'image_url': 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1400&q=80',
            'fallback_image': 'images/home/banner.jpg',
            'routes': len(packages),
            'spots': 6,
        },
        'packages': packages,
    })


def build_destination_packages(destination_name):
    base = {
        '中国': [
            ('北京古都与长城 5 日', '¥3,999 起', '5 天 4 晚', '四星精选酒店'),
            ('云南昆明大理丽江 7 日', '¥5,699 起', '7 天 6 晚', '古城客栈 + 度假酒店'),
            ('桂林阳朔山水 4 日', '¥2,899 起', '4 天 3 晚', '山景精品酒店'),
        ],
        '日本': [
            ('东京浅草上野自由行 5 日', '¥6,299 起', '5 天 4 晚', '市中心精选酒店'),
            ('京都古都文化 5 日', '¥6,499 起', '5 天 4 晚', '町屋体验酒店'),
        ],
    }.get(destination_name, [
        (f'{destination_name}精选深度游 5 日', '¥6,999 起', '5 天 4 晚', '精选舒适酒店')
    ])
    packages = []
    for index, (name, price, duration, hotel) in enumerate(base):
        packages.append({
            'id': f'{quote(destination_name)}-{index}',
            'name': name,
            'destination': destination_name,
            'price': price,
            'image_url': 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=80',
            'fallback_image': f'images/packages/p{index % 6 + 1}.jpg',
            'duration': duration,
            'hotel': hotel,
            'transport': '当地接送服务',
            'meal': '当地特色餐',
            'rating': 5,
            'reviews': 600 + index * 138,
            'highlights': ['经典地标', '当地文化体验', '舒适自由时间'],
        })
    return packages


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
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功，已为您自动登录。')
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


@csrf_exempt
def send_email_code(request):
    if request.method != 'POST':
        return JsonResponse({'error': '仅支持 POST 请求'}, status=405)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        data = request.POST.dict()

    email = str(data.get('email') or '').strip().lower()
    if not email:
        return JsonResponse({'error': '请先填写邮箱地址'}, status=400)
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'error': '邮箱地址格式不正确'}, status=400)
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({'error': '这个邮箱已经被注册，请直接登录'}, status=400)
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        return JsonResponse({'error': '邮件服务未配置，本地演示可以留空验证码直接注册'}, status=500)

    latest = EmailVerificationCode.objects.filter(email=email, purpose='register').order_by('-created_at').first()
    if latest and (timezone.now() - latest.created_at).total_seconds() < 60:
        return JsonResponse({'error': '验证码发送太频繁，请 60 秒后再试'}, status=429)

    code = f'{random.randint(0, 999999):06d}'
    verification = EmailVerificationCode.objects.create(
        email=email,
        code=code,
        purpose='register',
        expires_at=EmailVerificationCode.default_expires_at(),
    )

    try:
        send_mail(
            subject='TourNest 注册邮箱验证码',
            message=f'您的 TourNest 注册验证码是：{code}。验证码 10 分钟内有效，请勿泄露给他人。',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception:
        verification.delete()
        return JsonResponse({'error': '验证码发送失败，本地演示可以留空验证码直接注册'}, status=500)

    return JsonResponse({'message': '验证码已发送，请查收邮箱', 'expires_in': 600})


def user_logout_page(request):
    logout(request)
    messages.success(request, '您已安全退出登录。')
    return redirect(reverse_lazy('home'))


@login_required
def profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'avatar_url': '', 'preferred_currency': 'CNY', 'bio': ''},
    )

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user_profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '个人信息已更新。')
            return redirect('profile')
    else:
        form = ProfileForm(instance=user_profile, user=request.user)

    bookings = TravelBooking.objects.filter(user=request.user)[:4]
    return render(request, 'profile.html', {'form': form, 'profile': user_profile, 'bookings': bookings})


def _sse(payload):
    return 'data: ' + json.dumps(payload, ensure_ascii=False) + '\n\n'


@csrf_exempt
def hotel_ai_search(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        data = request.POST.dict()
    city = str(data.get('city') or '上海').strip()

    hotels = [
        {'name': f'{city}核心区舒适酒店', 'area': f'{city}市中心', 'price': 468, 'rating': 4.7, 'reviewCount': 1280, 'room': '高级大床房', 'tags': ['交通方便', '高评分'], 'detailUrl': 'https://www.bing.com/search?q=' + quote(f'{city} 核心区舒适酒店 官网'), 'imageQuery': f'{city} 酒店'},
        {'name': f'{city}景点附近精品住宿', 'area': f'{city}景区附近', 'price': 628, 'rating': 4.8, 'reviewCount': 930, 'room': '景观双床房', 'tags': ['近景点', '体验感强'], 'detailUrl': 'https://www.bing.com/search?q=' + quote(f'{city} 景点附近 精品酒店 官网'), 'imageQuery': f'{city} 精品酒店'},
        {'name': f'{city}高性价比连锁酒店', 'area': f'{city}交通枢纽周边', 'price': 299, 'rating': 4.5, 'reviewCount': 2100, 'room': '标准间', 'tags': ['预算友好', '实用'], 'detailUrl': 'https://www.bing.com/search?q=' + quote(f'{city} 高性价比 连锁酒店 官网'), 'imageQuery': f'{city} 连锁酒店'},
    ]

    def event_stream():
        yield _sse({'type': 'start'})
        yield _sse({'type': 'status', 'content': '正在生成本地演示酒店结果'})
        for hotel in hotels:
            yield _sse({'type': 'hotel', 'hotel': hotel})
        yield _sse({'type': 'done', 'count': len(hotels)})

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


@csrf_exempt
def flight_ai_search(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        data = request.POST.dict()
    origin = str(data.get('from') or '北京').strip()
    destination = str(data.get('to') or '上海').strip()

    flights = [
        {'airline': '东方航空', 'code': 'MU5102', 'fromAirport': f'{origin}机场', 'toAirport': f'{destination}机场', 'departTime': '08:30', 'arriveTime': '10:45', 'duration': 135, 'direct': True, 'price': 520, 'discount': '早班特价', 'tags': ['直飞', '低价'], 'detailUrl': 'https://www.bing.com/search?q=' + quote(f'{origin} 到 {destination} 机票 预订')},
        {'airline': '中国国航', 'code': 'CA1501', 'fromAirport': f'{origin}机场', 'toAirport': f'{destination}机场', 'departTime': '11:20', 'arriveTime': '13:35', 'duration': 135, 'direct': True, 'price': 680, 'discount': '舒适直飞', 'tags': ['直飞', '含行李'], 'detailUrl': 'https://www.bing.com/search?q=' + quote(f'{origin} 到 {destination} 机票 预订')},
        {'airline': '南方航空', 'code': 'CZ3101', 'fromAirport': f'{origin}机场', 'toAirport': f'{destination}机场', 'departTime': '17:10', 'arriveTime': '19:30', 'duration': 140, 'direct': True, 'price': 760, 'discount': '晚间优惠', 'tags': ['直飞', '退改灵活'], 'detailUrl': 'https://www.bing.com/search?q=' + quote(f'{origin} 到 {destination} 机票 预订')},
    ]

    def event_stream():
        yield _sse({'type': 'start'})
        yield _sse({'type': 'status', 'content': '正在生成本地演示机票结果'})
        for flight in flights:
            yield _sse({'type': 'flight', 'flight': flight})
        yield _sse({'type': 'done', 'count': len(flights)})

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


@csrf_exempt
def search_ai(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        data = request.POST.dict()

    city = str(data.get('city') or data.get('country') or '目的地').strip()
    days = str(data.get('days') or '3').strip()
    people = str(data.get('people') or '2').strip()
    budget = str(data.get('budget') or '适中').strip()
    message = str(data.get('message') or '').strip()

    plan = (
        f'{city}{days}日旅行建议，适合{people}人出行，预算按{budget}控制。\\n\\n'
        f'第1天：抵达{city}，先办理入住，下午安排城市核心区漫步，晚上体验当地美食。\\n'
        f'第2天：游览{city}代表性景点，上午安排博物馆或历史街区，下午去热门观景点。\\n'
        f'第3天：根据体力选择周边短途游或购物休闲，预留返程时间。\\n\\n'
        '住宿建议：优先选择交通方便的市中心或地铁周边。\\n'
        '交通建议：提前查好机场/车站到酒店路线，热门景点尽量错峰。'
    )
    if message:
        plan += f'\\n\\n已根据你的要求调整：{message}'

    def event_stream():
        yield _sse({'type': 'start'})
        yield _sse({'type': 'content', 'content': plan})
        yield _sse({'type': 'done'})

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
