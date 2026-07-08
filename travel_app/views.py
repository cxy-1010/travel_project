import json
import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Flight, FlightPrice, Hotel, HotelRoom, Package, PackageExtra, Booking, Guide, GuideComment

# ============================================================
# 攻略相关视图（保持不变）
# ============================================================
def get_guides(request):
    destination = request.GET.get("destination", "")
    if destination:
        guides = Guide.objects.filter(destination__icontains=destination).order_by("-created_at")
    else:
        guides = Guide.objects.all().order_by("-created_at")
    guide_list = []
    for g in guides:
        guide_list.append({
            "id": g.id,
            "title": g.title,
            "destination": g.destination,
            "author": g.user.username,
            "image_url": g.image_url,
            "likes": g.likes,
            "created_at": g.created_at.strftime("%Y-%m-%d %H:%M"),
        })
    return JsonResponse({"status": "success", "data": guide_list})

def guide_detail(request, guide_id):
    try:
        guide = Guide.objects.get(id=guide_id)
    except Guide.DoesNotExist:
        return JsonResponse({"status": "fail", "message": "攻略不存在"}, status=404)
    comments = guide.comments.all().order_by("-created_at").values("user__username", "content", "created_at")
    comment_list = list(comments)
    data = {
        "id": guide.id,
        "title": guide.title,
        "destination": guide.destination,
        "content": guide.content,
        "author": guide.user.username,
        "image_url": guide.image_url,
        "likes": guide.likes,
        "created_at": guide.created_at.strftime("%Y-%m-%d %H:%M"),
        "comments": comment_list,
    }
    return JsonResponse({"status": "success", "data": data})

def create_guide(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "fail", "message": "请先登录"}, status=401)
    if request.method == "POST":
        data = json.loads(request.body) if request.content_type == "application/json" else request.POST
        guide = Guide.objects.create(
            user=request.user,
            title=data.get("title"),
            destination=data.get("destination"),
            content=data.get("content"),
            image_url=data.get("image_url", ""),
        )
        return JsonResponse({"status": "success", "message": "攻略发布成功", "guide_id": guide.id})
    return JsonResponse({"status": "fail", "message": "请使用POST请求"})

def like_guide(request, guide_id):
    if request.method == "POST":
        try:
            guide = Guide.objects.get(id=guide_id)
            guide.likes += 1
            guide.save()
            return JsonResponse({"status": "success", "likes": guide.likes})
        except Guide.DoesNotExist:
            return JsonResponse({"status": "fail", "message": "攻略不存在"}, status=404)

def add_guide_comment(request, guide_id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "fail", "message": "请先登录"}, status=401)
    if request.method == "POST":
        try:
            guide = Guide.objects.get(id=guide_id)
        except Guide.DoesNotExist:
            return JsonResponse({"status": "fail", "message": "攻略不存在"}, status=404)
        data = json.loads(request.body) if request.content_type == "application/json" else request.POST
        GuideComment.objects.create(user=request.user, guide=guide, content=data.get("content"))
        return JsonResponse({"status": "success", "message": "评论成功"})


# ============================================================
# 首页 - 展示所有套餐
# ============================================================
def index(request):
    packages = Package.objects.all().order_by("-created_at")
    return render(request, "index.html", {"packages": packages})


# ============================================================
# 用户注册
# ============================================================
def register_view(request):
    if request.method == "POST":
        data = json.loads(request.body) if request.content_type == "application/json" else request.POST
        username = data.get("username")
        password = data.get("password")
        email = data.get("email", "")
        if not username or not password:
            if request.content_type == "application/json":
                return JsonResponse({"status": "fail", "message": "用户名和密码不能为空"})
            return render(request, "register.html", {"error": "用户名和密码不能为空"})
        if User.objects.filter(username=username).exists():
            if request.content_type == "application/json":
                return JsonResponse({"status": "fail", "message": "用户名已存在"})
            return render(request, "register.html", {"error": "用户名已存在"})
        user = User.objects.create_user(username=username, password=password, email=email)
        login(request, user)
        if request.content_type == "application/json":
            return JsonResponse({"status": "success", "message": "注册成功"})
        return redirect("/")
    return render(request, "register.html")


# ============================================================
# 用户登录
# ============================================================
def login_view(request):
    if request.method == "POST":
        data = json.loads(request.body) if request.content_type == "application/json" else request.POST
        username = data.get("username")
        password = data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get("next", "/")
            if request.content_type == "application/json":
                return JsonResponse({"status": "success", "message": "登录成功"})
            return redirect(next_url)
        else:
            if request.content_type == "application/json":
                return JsonResponse({"status": "fail", "message": "用户名或密码错误"})
            return render(request, "login.html", {"error": "用户名或密码错误"})
    return render(request, "login.html")


# ============================================================
# 用户登出
# ============================================================
def logout_view(request):
    logout(request)
    return redirect("/")


# ============================================================
# 套餐预订
# ============================================================
@login_required(login_url="/login/")
def book_package(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    if request.method == "POST":
        data = json.loads(request.body) if request.content_type == "application/json" else request.POST
        num_people = int(data.get("num_people", 1))
        contact_name = data.get("contact_name", "")
        contact_phone = data.get("contact_phone", "")
        travel_date_str = data.get("travel_date", "")

        if num_people < 1:
            return render(request, "book_package.html", {"package": package, "error": "出行人数至少为1"})
        if not travel_date_str:
            return render(request, "book_package.html", {"package": package, "error": "请选择出行日期"})

        travel_date = datetime.datetime.strptime(travel_date_str, "%Y-%m-%d").date()
        if travel_date <= datetime.date.today():
            return render(request, "book_package.html", {"package": package, "error": "出行日期必须晚于今天"})

        unit_price = float(package.discount_price) if package.discount_price else float(package.original_price)
        total_price = round(unit_price * num_people, 2)

        booking = Booking.objects.create(
            user=request.user,
            package=package,
            num_people=num_people,
            total_price=total_price,
            contact_name=contact_name,
            contact_phone=contact_phone,
            travel_date=travel_date,
            status="pending",
        )
        return redirect("/my-bookings/")
    return render(request, "book_package.html", {"package": package})


# ============================================================
# 我的预订列表
# ============================================================
@login_required(login_url="/login/")
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related("package").order_by("-created_at")
    return render(request, "my_bookings.html", {"bookings": bookings})


# ============================================================
# 取消预订
# ============================================================
@login_required(login_url="/login/")
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == "POST":
        booking.status = "cancelled"
        booking.save()
        return redirect("/my-bookings/")
    return redirect("/my-bookings/")


# ============================================================
# JSON API
# ============================================================
def get_packages_json(request):
    packages = Package.objects.all().order_by("-created_at")
    data = []
    for p in packages:
        data.append({
            "id": p.id,
            "name": p.name,
            "destination": p.destination,
            "itinerary": p.itinerary,
            "original_price": float(p.original_price),
            "discount_price": float(p.discount_price) if p.discount_price else None,
            "current_price": p.current_price,
            "has_discount": p.has_discount,
            "duration": p.duration,
            "image": p.image,
            "rating": float(p.rating),
            "extras": [{"name": e.name, "price": float(e.price)} for e in p.extras.all()],
        })
    return JsonResponse({"status": "success", "data": data})


def get_package_detail(request, package_id):
    p = get_object_or_404(Package.objects.prefetch_related("extras"), id=package_id)
    data = {
        "id": p.id,
        "name": p.name,
        "destination": p.destination,
        "itinerary": p.itinerary,
        "original_price": float(p.original_price),
        "discount_price": float(p.discount_price) if p.discount_price else None,
        "current_price": p.current_price,
        "has_discount": p.has_discount,
        "duration": p.duration,
        "image": p.image,
        "rating": float(p.rating),
        "extras": [{"name": e.name, "price": float(e.price)} for e in p.extras.all()],
    }
    return JsonResponse({"status": "success", "data": data})


def get_flights_hotels_json(request):
    flights = Flight.objects.all().order_by("-created_at")
    hotels = Hotel.objects.all().order_by("-created_at")
    return JsonResponse({
        "flights": [{"id": f.id, "flight_no": f.flight_no, "route": f"{f.departure_city} → {f.arrival_city}", "departure": f.departure_time.strftime("%Y-%m-%d %H:%M")} for f in flights],
        "hotels": [{"id": h.id, "name": h.name, "city": h.city, "stars": h.stars} for h in hotels],
    })


# ============================================================
# 套餐管理 API（管理员）
# ============================================================
@csrf_exempt
@staff_member_required(login_url="/admin/login/")
def add_flight(request):
    if request.method == "POST":
        data = json.loads(request.body) if request.content_type == "application/json" else request.POST
        flight = Flight.objects.create(
            flight_no=data.get("flight_no"),
            departure_city=data.get("departure_city"),
            arrival_city=data.get("arrival_city"),
            departure_time=datetime.datetime.strptime(data.get("departure_time"), "%Y-%m-%d %H:%M"),
            arrival_time=datetime.datetime.strptime(data.get("arrival_time"), "%Y-%m-%d %H:%M"),
        )
        return JsonResponse({"status": "success", "message": "航班添加成功", "id": flight.id})
    return JsonResponse({"status": "fail", "message": "请使用POST请求"})

@csrf_exempt
@staff_member_required(login_url="/admin/login/")
def add_hotel(request):
    if request.method == "POST":
        data = json.loads(request.body) if request.content_type == "application/json" else request.POST
        hotel = Hotel.objects.create(
            name=data.get("name"),
            city=data.get("city"),
            stars=data.get("stars", 3),
            description=data.get("description", ""),
            image=data.get("image", ""),
        )
        return JsonResponse({"status": "success", "message": "酒店添加成功", "id": hotel.id})
    return JsonResponse({"status": "fail", "message": "请使用POST请求"})

@csrf_exempt
@staff_member_required(login_url="/admin/login/")
def add_flight_price(request):
    if request.method == "POST":
        data = json.loads(request.body) if request.content_type == "application/json" else request.POST
        try:
            flight = Flight.objects.get(id=data.get("flight_id"))
        except Flight.DoesNotExist:
            return JsonResponse({"status": "fail", "message": "航班不存在"}, status=404)
        fp = FlightPrice.objects.create(flight=flight, supplier=data.get("supplier"), cabin_class=data.get("cabin_class", "economy"), price=data.get("price"))
        return JsonResponse({"status": "success", "message": "价格添加成功", "id": fp.id})
    return JsonResponse({"status": "fail", "message": "请使用POST请求"})

@csrf_exempt
@staff_member_required(login_url="/admin/login/")
def add_hotel_room(request):
    if request.method == "POST":
        data = json.loads(request.body) if request.content_type == "application/json" else request.POST
        try:
            hotel = Hotel.objects.get(id=data.get("hotel_id"))
        except Hotel.DoesNotExist:
            return JsonResponse({"status": "fail", "message": "酒店不存在"}, status=404)
        hr = HotelRoom.objects.create(hotel=hotel, room_type=data.get("room_type"), price_per_night=data.get("price_per_night"))
        return JsonResponse({"status": "success", "message": "房型添加成功", "id": hr.id})
    return JsonResponse({"status": "fail", "message": "请使用POST请求"})

@csrf_exempt
@staff_member_required(login_url="/admin/login/")
def create_package(request):
    if request.method == "POST":
        data = json.loads(request.body) if request.content_type == "application/json" else request.POST
        package = Package.objects.create(
            name=data.get("name"),
            destination=data.get("destination", ""),
            itinerary=data.get("itinerary", ""),
            original_price=data.get("original_price", 0),
            discount_price=data.get("discount_price") if data.get("discount_price") else None,
            duration=data.get("duration", "5天4晚"),
            image=data.get("image", "images/packages/p1.jpg"),
            rating=data.get("rating", 4.5),
        )
        return JsonResponse({"status": "success", "message": "套餐创建成功", "id": package.id})
    return JsonResponse({"status": "fail", "message": "请使用POST请求"})

@csrf_exempt
@staff_member_required(login_url="/admin/login/")
def delete_package(request, package_id):
    if request.method == "POST":
        package = get_object_or_404(Package, id=package_id)
        package.delete()
        return JsonResponse({"status": "success", "message": "套餐已删除"})
    return JsonResponse({"status": "fail", "message": "请使用POST请求"})
