import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Guide, GuideComment, GuideFavorite, TravelNews
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Flight, Hotel, Order
from django.db.models import Q


def _liked_guide_ids(request):
    return {str(guide_id) for guide_id in request.session.get('liked_guides', [])}


def _is_guide_liked(request, guide_id):
    return str(guide_id) in _liked_guide_ids(request)


def _session_favorite_guide_ids(request):
    return {str(guide_id) for guide_id in request.session.get('favorite_guides', [])}


def _favorite_guide_ids(request):
    if request.user.is_authenticated:
        return {
            str(guide_id)
            for guide_id in GuideFavorite.objects.filter(user=request.user).values_list('guide_id', flat=True)
        }
    return _session_favorite_guide_ids(request)


def _is_guide_favorited(request, guide_id):
    return str(guide_id) in _favorite_guide_ids(request)


# 1. 获取攻略列表（所有人可见，支持按目的地过滤）
def get_guides(request):
    keyword = request.GET.get('search', '').strip()
    destination = request.GET.get('destination', '').strip()
    liked_guides = _liked_guide_ids(request)
    favorite_guides = _favorite_guide_ids(request)

    guides = Guide.objects.select_related('user').prefetch_related('comments', 'favorites').all()
    if destination:
        guides = guides.filter(destination__icontains=destination)
    if keyword:
        guides = guides.filter(
            Q(destination__icontains=keyword) |
            Q(title__icontains=keyword) |
            Q(content__icontains=keyword)
        )
        
    guide_list = []
    for g in guides:
        guide_list.append({
            'id': g.id,
            'title': g.title,
            'destination': g.destination,
            'content': g.content,
            'author': g.user.username,
            'image_url': g.image_url,
            'likes': g.likes,
            'liked': str(g.id) in liked_guides,
            'favorited': str(g.id) in favorite_guides,
            'favorite_count': g.favorites.count(),
            'comment_count': g.comments.count(),
            'created_at': g.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return JsonResponse({'status': 'success', 'data': guide_list})

# 2. 查看攻略详情与该攻略下的所有评论
def guide_detail(request, guide_id):
    guide = get_object_or_404(Guide.objects.select_related('user'), id=guide_id)
        
    comment_list = [
        {
            'author': comment.user.username,
            'title': comment.title,
            'content': comment.content,
            'destination': comment.destination,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
        }
        for comment in guide.comments.select_related('user').all()
    ]
    
    data = {
        'id': guide.id,
        'title': guide.title,
        'destination': guide.destination,
        'content': guide.content,
        'author': guide.user.username,
        'image_url': guide.image_url,
        'likes': guide.likes,
        'liked': _is_guide_liked(request, guide.id),
        'favorited': _is_guide_favorited(request, guide.id),
        'favorite_count': guide.favorites.count(),
        'created_at': guide.created_at.strftime('%Y-%m-%d %H:%M'),
        'comments': comment_list
    }
    return JsonResponse({'status': 'success', 'data': data})

# 3. 发布新攻略（必须登录）
@csrf_exempt
def create_guide(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            title = (data.get('title') or '').strip()
            destination = (data.get('destination') or '').strip()
            content = (data.get('content') or '').strip()

            if not title or not destination or not content:
                return JsonResponse({'status': 'fail', 'message': '标题、目的地和正文不能为空'}, status=400)
            
            user = request.user if request.user.is_authenticated else User.objects.get_or_create(username='互动游客')[0]
            
            new_guide = Guide.objects.create(
                user=user,
                title=title,
                destination=destination,
                content=content
            )
            
            return JsonResponse({
                'status': 'success',
                'message': '发布成功',
                'guide_id': new_guide.id
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': '仅支持POST请求'}, status=405)

# 4. 给攻略点赞（所有人/登录用户均可，简单实现机制）
@csrf_exempt
@require_POST
def like_guide(request, guide_id):
    guide = get_object_or_404(Guide, id=guide_id)
    guide_key = str(guide.id)
    liked_guides = _liked_guide_ids(request)

    if guide_key in liked_guides:
        liked_guides.remove(guide_key)
        guide.likes = max(guide.likes - 1, 0)
        liked = False
    else:
        liked_guides.add(guide_key)
        guide.likes += 1
        liked = True

    request.session['liked_guides'] = list(liked_guides)
    request.session.modified = True
    guide.save(update_fields=['likes'])
    return JsonResponse({'status': 'success', 'likes': guide.likes, 'liked': liked})


@csrf_exempt
@require_POST
def favorite_guide(request, guide_id):
    guide = get_object_or_404(Guide, id=guide_id)

    if request.user.is_authenticated:
        favorite, created = GuideFavorite.objects.get_or_create(user=request.user, guide=guide)
        favorited = created
        if not created:
            favorite.delete()
            favorited = False
    else:
        guide_key = str(guide.id)
        favorite_guides = _session_favorite_guide_ids(request)
        if guide_key in favorite_guides:
            favorite_guides.remove(guide_key)
            favorited = False
        else:
            favorite_guides.add(guide_key)
            favorited = True
        request.session['favorite_guides'] = list(favorite_guides)
        request.session.modified = True

    return JsonResponse({
        'status': 'success',
        'favorited': favorited,
        'favorite_count': guide.favorites.count()
    })

# 5. 发表攻略评论（必须登录）
@csrf_exempt
def add_guide_comment(request, guide_id):
    if request.method == 'POST':
        guide = get_object_or_404(Guide, id=guide_id)
            
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        content = (data.get('content') or '').strip()
        if not content:
            return JsonResponse({'status': 'fail', 'message': '评论内容不能为空'}, status=400)

        user = request.user if request.user.is_authenticated else User.objects.get_or_create(username='互动游客')[0]
        comment = GuideComment.objects.create(
            user=user,
            guide=guide,
            title=f"回复：{guide.title[:40]}",
            destination=guide.destination,
            content=content
        )
        return JsonResponse({
            'status': 'success',
            'message': '评论成功',
            'comment': {
                'author': comment.user.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })
    return JsonResponse({'status': 'fail', 'message': '仅支持POST'}, status=405)
    
def user_register(request):
    if request.method == 'POST':
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        username, password = data.get('username'), data.get('password')
        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': 'fail', 'message': '用户名已存在'})
        User.objects.create_user(username=username, password=password)
        return JsonResponse({'status': 'success', 'message': '注册成功'})
    return JsonResponse({'status': 'fail', 'message': '仅支持POST'})

def user_login(request):
    if request.method == 'POST':
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        user = authenticate(request, username=data.get('username'), password=data.get('password'))
        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'success', 'message': '登录成功'})
        return JsonResponse({'status': 'fail', 'message': '账号或密码错误'})
    return JsonResponse({'status': 'fail', 'message': '仅支持POST'})

def user_logout(request):
    logout(request)
    return JsonResponse({'status': 'success', 'message': '已退出登录'})

# 航班搜索（支持目的地过滤，并按价格从低到高排序，实现价格比较）
def search_flights(request):
    dest = request.GET.get('destination', '')
    flights = Flight.objects.filter(destination__icontains=dest).order_by('price') if dest else Flight.objects.all().order_by('price')
    data = [{'id': f.id, 'flight_number': f.flight_number, 'airline': f.airline, 'departure': f.departure, 'destination': f.destination, 'price': float(f.price), 'rating': f.rating} for f in flights]
    return JsonResponse({'status': 'success', 'data': data})

# 酒店搜索
def search_hotels(request):
    dest = request.GET.get('destination', '')
    hotels = Hotel.objects.filter(destination__icontains=dest).order_by('price') if dest else Hotel.objects.all().order_by('price')
    data = [{'id': h.id, 'name': h.name, 'destination': h.destination, 'price': float(h.price), 'rating': h.rating, 'address': h.address} for h in hotels]
    return JsonResponse({'status': 'success', 'data': data})

# 预订下单
def create_order(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'fail', 'message': '请先登录'}, status=401)
    if request.method == 'POST':
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        order = Order.objects.create(
            user=request.user, item_type=data.get('item_type'),
            item_id=data.get('item_id'), item_name=data.get('item_name'), price=data.get('price')
        )
        return JsonResponse({'status': 'success', 'order_id': order.id})

def my_orders(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'fail', 'message': '请先登录'}, status=401)
    orders = Order.objects.filter(user=request.user).values()
    return JsonResponse({'status': 'success', 'data': list(orders)})

def home_page(request):
    # 1. 获取前端传过来的搜索词 (例如 ?search=北京)
    search_query = request.GET.get('search', '').strip()
    
    # 2. 基础查询：捞取所有攻略
    guides = Guide.objects.select_related('user').prefetch_related('favorites').all().order_by('-created_at')
    
    # 3. 💡 如果用户输入了搜索词，直接在数据库进行筛选过滤！
    if search_query:
        guides = guides.filter(
            Q(destination__icontains=search_query) |  # 匹配目的地城市
            Q(title__icontains=search_query) |        # 匹配标题
            Q(content__icontains=search_query)        # 匹配正文内容
        )
    
    # 4. 色彩库（保持你们之前绚丽的色彩库逻辑）
    color_palette = [
        ("#FFF5F5", "#E53E3E"), ("#EBF8FF", "#3182CE"), 
        ("#F0FDF4", "#16A34A"), ("#FFFDF5", "#D97706"), 
        ("#F3E8FF", "#8B5CF6"), ("#ECEFEE", "#0D9488")
    ]
    city_color_map = {}
    color_index = 0
    
    for g in guides:
        city = g.destination
        if city not in city_color_map:
            city_color_map[city] = color_palette[color_index % len(color_palette)]
            color_index += 1
        g.bg_color = city_color_map[city][0]
        g.text_color = city_color_map[city][1]
        g.is_liked = _is_guide_liked(request, g.id)
        g.is_favorited = _is_guide_favorited(request, g.id)
        g.favorite_count = g.favorites.count()

    # 5. 把过滤后的列表和原本的请求一起传给前端
    latest_news = TravelNews.objects.all()[:3]
    favorite_ids = _favorite_guide_ids(request)
    favorite_guides = Guide.objects.select_related('user').filter(id__in=favorite_ids).order_by('-created_at')

    # 💡 6. 把老数据 guides 和新数据 latest_news 一起打包送走
    return render(request, 'index.html', {
        'g_list': guides,
        'favorite_guides': favorite_guides,
        'news_list': latest_news  # 🎯 加上这行，把新闻塞进前端能拿到的“管道”里！
    })

# 💡 1. 新闻攻略列表页
def news_list(request):
    # 查出所有的旅行资讯
    all_news = TravelNews.objects.all()
    # 也可以按分类筛选，比如：news_only = TravelNews.objects.filter(category='news')
    return render(request, 'news_list.html', {'news_list': all_news})

# 💡 2. 新闻攻略详情页（点击列表里的卡片跳进来看长文）
def news_detail(request, news_id):
    news = get_object_or_404(TravelNews, id=news_id)
    # 每次打开详情页，浏览量默默 +1
    news.views_count += 1
    news.save(update_fields=['views_count'])
    return render(request, 'news_detail.html', {'news': news})

def news_all_hub(request):
    # 🎯 核心：不加任何切片限制，把数据库里收集的所有攻略全部查出来！
    all_stored_news = TravelNews.objects.all().order_by('-created_at')
    return render(request, 'news_all_list.html', {'news_list': all_stored_news})
