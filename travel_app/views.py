import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Guide, GuideComment

# 1. 获取攻略列表（所有人可见，支持按目的地过滤）
def get_guides(request):
    destination = request.GET.get('destination', '')
    if destination:
        guides = Guide.objects.filter(destination__icontains=destination).order_by('-created_at')
    else:
        guides = Guide.objects.all().order_by('-created_at')
        
    # 转换为列表返回
    guide_list = []
    for g in guides:
        guide_list.append({
            'id': g.id,
            'title': g.title,
            'destination': g.destination,
            'author': g.user.username,
            'image_url': g.image_url,
            'likes': g.likes,
            'created_at': g.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return JsonResponse({'status': 'success', 'data': guide_list})

# 2. 查看攻略详情与该攻略下的所有评论
def guide_detail(request, guide_id):
    try:
        guide = Guide.objects.get(id=guide_id)
    except Guide.DoesNotExist:
        return JsonResponse({'status': 'fail', 'message': '攻略不存在'}, status=404)
        
    # 获取该攻略的所有评论
    comments = guide.comments.all().order_by('-created_at').values('user__username', 'content', 'created_at')
    comment_list = list(comments)
    
    data = {
        'id': guide.id,
        'title': guide.title,
        'destination': guide.destination,
        'content': guide.content,
        'author': guide.user.username,
        'image_url': guide.image_url,
        'likes': guide.likes,
        'created_at': guide.created_at.strftime('%Y-%m-%d %H:%M'),
        'comments': comment_list
    }
    return JsonResponse({'status': 'success', 'data': data})

# 3. 发布新攻略（必须登录）
def create_guide(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'fail', 'message': '请先登录'}, status=401)
        
    if request.method == 'POST':
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        
        guide = Guide.objects.create(
            user=request.user,
            title=data.get('title'),
            destination=data.get('destination'),
            content=data.get('content'),
            image_url=data.get('image_url', '')
        )
        return JsonResponse({'status': 'success', 'message': '攻略发布成功', 'guide_id': guide.id})
    return JsonResponse({'status': 'fail', 'message': '请使用POST请求'})

# 4. 给攻略点赞（所有人/登录用户均可，简单实现机制）
def like_guide(request, guide_id):
    if request.method == 'POST':
        try:
            guide = Guide.objects.get(id=guide_id)
            guide.likes += 1
            guide.save()
            return JsonResponse({'status': 'success', 'likes': guide.likes})
        except Guide.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': '攻略不存在'}, status=404)

# 5. 发表攻略评论（必须登录）
def add_guide_comment(request, guide_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'fail', 'message': '请先登录'}, status=401)
        
    if request.method == 'POST':
        try:
            guide = Guide.objects.get(id=guide_id)
        except Guide.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': '攻略不存在'}, status=404)
            
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        GuideComment.objects.create(
            user=request.user,
            guide=guide,
            content=data.get('content')
        )
        return JsonResponse({'status': 'success', 'message': '评论成功'})
