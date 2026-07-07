from datetime import datetime
from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.db import transaction

from .models import (
    Destination, TourPackage, Hotel, Flight, Testimonial,
    BlogPost, SpecialOffer, Subscriber, Booking,
    RoomType, SeatClass, ExtraService, UserReview, Favorite, UserProfile,
)
from .utils import get_best_deal, get_best_value, get_user_currency
import json

PACKAGE_BUNDLE_DISCOUNT_RATE = Decimal('0.05')


def _apply_sort(queryset, sort, price_field):
    if sort == 'price_asc':
        return queryset.order_by(price_field)
    if sort == 'price_desc':
        return queryset.order_by(f'-{price_field}')
    if sort == 'rating':
        return queryset.order_by('-rating')
    return queryset


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def _calc_nights(check_in, check_out, default=1):
    if check_in and check_out and check_out > check_in:
        return (check_out - check_in).days
    return default


def _decrement_inventory(booking):
    """支付成功后扣减座位/房间库存"""
    guest_count = booking.guest_count or 1
    if booking.seat_class:
        booking.seat_class.available_seats = max(
            0, booking.seat_class.available_seats - guest_count
        )
        booking.seat_class.save(update_fields=['available_seats'])
    elif booking.flight:
        booking.flight.seats_available = max(
            0, booking.flight.seats_available - guest_count
        )
        booking.flight.save(update_fields=['seats_available'])

    if booking.room_type:
        booking.room_type.available_rooms = max(0, booking.room_type.available_rooms - 1)
        booking.room_type.save(update_fields=['available_rooms'])


def _validate_inventory(booking):
    """预订前检查库存是否充足"""
    guest_count = booking.guest_count or 1
    if booking.seat_class and booking.seat_class.available_seats < guest_count:
        return False, '所选舱位余票不足'
    if booking.flight and not booking.seat_class and booking.flight.seats_available < guest_count:
        return False, '航班余票不足'
    if booking.room_type and booking.room_type.available_rooms < 1:
        return False, '所选房型已无空房'
    return True, ''


def index(request):
    packages = TourPackage.objects.filter(is_active=True)
    hotels = Hotel.objects.filter(is_active=True)
    flights = Flight.objects.filter(is_active=True)
    destinations = Destination.objects.filter(is_active=True)[:8]
    testimonials = Testimonial.objects.filter(is_active=True)
    blog_posts = BlogPost.objects.filter(is_published=True)[:3]
    special_offers = SpecialOffer.objects.filter(is_active=True)
    destination_choices = Destination.objects.filter(is_active=True).values('name', 'city', 'country')
    extra_services = ExtraService.objects.filter(is_active=True)

    context = {
        'packages': packages[:6],
        'hotels': hotels[:6],
        'flights': flights[:6],
        'destinations': destinations,
        'testimonials': testimonials,
        'blog_posts': blog_posts,
        'special_offers': special_offers,
        'destinations_json': json.dumps(list(destination_choices), ensure_ascii=False),
        'best_package': get_best_deal(list(packages), 'price'),
        'best_hotel': get_best_value(list(hotels), 'price_per_night', 'rating'),
        'best_flight': get_best_deal(list(flights), 'price'),
        'extra_services': extra_services,
    }
    return render(request, 'index.html', context)


def package_list(request):
    packages = TourPackage.objects.filter(is_active=True)
    destination = request.GET.get('destination', '')
    sort = request.GET.get('sort', '')

    if destination:
        packages = packages.filter(
            Q(destination__name__icontains=destination) |
            Q(destination__city__icontains=destination)
        )
    packages = _apply_sort(packages, sort, 'price')
    package_list_all = list(packages)
    best_deal = get_best_deal(package_list_all, 'price')
    best_value = get_best_value(package_list_all, 'price', 'rating')

    paginator = Paginator(packages, 9)
    packages_page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'package_list.html', {
        'packages': packages_page,
        'destination': destination,
        'sort': sort,
        'best_deal': best_deal,
        'best_value': best_value,
    })


def package_detail(request, pk):
    package = get_object_or_404(TourPackage, pk=pk, is_active=True)
    related_packages = TourPackage.objects.filter(is_active=True).exclude(pk=pk)[:3]
    reviews = UserReview.objects.filter(package=package, is_approved=True)[:10]
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(
            user=request.user, favorite_type='package', package=package
        ).exists()
    return render(request, 'package_detail.html', {
        'package': package,
        'related_packages': related_packages,
        'reviews': reviews,
        'is_favorited': is_favorited,
    })


def hotel_list(request):
    hotels = Hotel.objects.filter(is_active=True)
    city = request.GET.get('city', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    stars = request.GET.get('stars', '')
    sort = request.GET.get('sort', '')
    check_in = request.GET.get('check_in', '')
    check_out = request.GET.get('check_out', '')

    if city:
        hotels = hotels.filter(Q(city__icontains=city) | Q(name__icontains=city))
    if min_price:
        hotels = hotels.filter(price_per_night__gte=min_price)
    if max_price:
        hotels = hotels.filter(price_per_night__lte=max_price)
    if stars:
        hotels = hotels.filter(stars=stars)

    hotels = _apply_sort(hotels, sort, 'price_per_night')
    if not sort:
        hotels = hotels.order_by('name')
    hotel_list_all = list(hotels)
    best_deal = get_best_deal(hotel_list_all, 'price_per_night')
    best_value = get_best_value(hotel_list_all, 'price_per_night', 'rating')

    paginator = Paginator(hotels, 9)
    hotels_page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'hotel_list.html', {
        'hotels': hotels_page,
        'city': city,
        'min_price': min_price,
        'max_price': max_price,
        'stars': stars,
        'sort': sort,
        'check_in': check_in,
        'check_out': check_out,
        'best_deal': best_deal,
        'best_value': best_value,
    })


def hotel_detail(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk, is_active=True)
    room_types = hotel.room_types.filter(is_active=True)
    reviews = UserReview.objects.filter(hotel=hotel, is_approved=True)[:10]
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(
            user=request.user, favorite_type='hotel', hotel=hotel
        ).exists()
    return render(request, 'hotel_detail.html', {
        'hotel': hotel,
        'room_types': room_types,
        'reviews': reviews,
        'is_favorited': is_favorited,
    })


def flight_list(request):
    flights = Flight.objects.filter(is_active=True)
    origin = request.GET.get('origin', '')
    destination = request.GET.get('destination', '')
    flight_type = request.GET.get('flight_type', '')
    departure_date = request.GET.get('departure_date', '')
    sort = request.GET.get('sort', '')

    if origin:
        flights = flights.filter(origin_city__icontains=origin)
    if destination:
        flights = flights.filter(destination_city__icontains=destination)
    if flight_type:
        flights = flights.filter(flight_type=flight_type)
    if departure_date:
        parsed = _parse_date(departure_date)
        if parsed:
            flights = flights.filter(departure_time__date=parsed)

    flights = _apply_sort(flights, sort, 'price')
    flight_list_all = list(flights)
    best_deal = get_best_deal(flight_list_all, 'price')

    paginator = Paginator(flights, 10)
    flights_page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'flight_list.html', {
        'flights': flights_page,
        'origin': origin,
        'destination': destination,
        'flight_type': flight_type,
        'departure_date': departure_date,
        'sort': sort,
        'best_deal': best_deal,
    })


def destination_list(request):
    destinations = Destination.objects.filter(is_active=True)
    query = request.GET.get('q', '').strip()
    if query:
        destinations = destinations.filter(
            Q(name__icontains=query) | Q(country__icontains=query) | Q(city__icontains=query)
        )
    return render(request, 'destination_list.html', {
        'destinations': destinations,
        'query': query,
    })


def destination_detail(request, pk):
    destination = get_object_or_404(Destination, pk=pk, is_active=True)
    packages = TourPackage.objects.filter(destination=destination, is_active=True)[:6]
    hotels = Hotel.objects.filter(destination=destination, is_active=True)[:6]
    blog_posts = BlogPost.objects.filter(destination=destination, is_published=True)[:4]
    reviews = UserReview.objects.filter(destination=destination, is_approved=True)[:10]
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(
            user=request.user, favorite_type='destination', destination=destination
        ).exists()
    return render(request, 'destination_detail.html', {
        'destination': destination,
        'packages': packages,
        'hotels': hotels,
        'blog_posts': blog_posts,
        'reviews': reviews,
        'is_favorited': is_favorited,
    })


def flight_detail(request, pk):
    flight = get_object_or_404(Flight, pk=pk, is_active=True)
    seat_classes = flight.seat_classes.all()
    reviews = UserReview.objects.filter(flight=flight, is_approved=True)[:10]
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(
            user=request.user, favorite_type='flight', flight=flight
        ).exists()
    return render(request, 'flight_detail.html', {
        'flight': flight,
        'seat_classes': seat_classes,
        'reviews': reviews,
        'is_favorited': is_favorited,
    })


def blog_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk, is_published=True)
    post.view_count += 1
    post.save(update_fields=['view_count'])
    related_posts = BlogPost.objects.filter(is_published=True).exclude(pk=pk)[:3]
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(
            user=request.user, favorite_type='blog', blog_post=post
        ).exists()
    return render(request, 'blog_detail.html', {
        'post': post,
        'related_posts': related_posts,
        'is_favorited': is_favorited,
    })


def blog_list(request):
    posts = BlogPost.objects.filter(is_published=True)
    category = request.GET.get('category', '')
    if category:
        posts = posts.filter(category=category)

    paginator = Paginator(posts, 6)
    posts_page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'blog_list.html', {
        'posts': posts_page,
        'current_category': category,
    })


def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, '两次输入的密码不一致')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'register.html')

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, f'欢迎 {username}，注册成功！')
        return redirect('index')
    return render(request, 'register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'index')
            messages.success(request, f'欢迎回来，{username}！')
            return redirect(next_url)
        messages.error(request, '用户名或密码错误')
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    messages.success(request, '您已成功退出登录')
    return redirect('index')


@login_required
def user_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        request.user.email = request.POST.get('email', request.user.email)
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.save()

        profile.phone = request.POST.get('phone', '')
        profile.bio = request.POST.get('bio', '')
        profile.avatar_url = request.POST.get('avatar_url', '')
        profile.preferred_currency = request.POST.get('preferred_currency', 'CNY')
        profile.save()
        request.session['currency'] = profile.preferred_currency
        messages.success(request, '个人资料已更新')
        return redirect('user_profile')
    return render(request, 'profile.html', {'profile': profile})


def change_currency(request):
    currency = request.GET.get('currency', 'CNY')
    if currency not in ('CNY', 'USD', 'EUR'):
        currency = 'CNY'
    request.session['currency'] = currency
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.preferred_currency = currency
        profile.save()
    next_url = request.GET.get('next', '/')
    return redirect(next_url)


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).prefetch_related('extra_services')
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    return render(request, 'my_bookings.html', {
        'bookings': bookings,
        'status_filter': status_filter,
        'status_choices': Booking.STATUS_CHOICES,
    })


@login_required
def create_booking(request):
    if request.method != 'POST':
        return redirect('index')

    booking_type = request.POST.get('booking_type')
    item_id = request.POST.get('item_id')
    guest_count = int(request.POST.get('guest_count', 1))
    check_in = _parse_date(request.POST.get('check_in'))
    check_out = _parse_date(request.POST.get('check_out'))
    nights = _calc_nights(check_in, check_out)

    booking = Booking(
        user=request.user,
        booking_type=booking_type,
        guest_count=guest_count,
        status='pending',
        check_in=check_in,
        check_out=check_out,
        note=request.POST.get('note', ''),
    )

    if booking_type == 'package':
        pkg = get_object_or_404(TourPackage, pk=item_id)
        booking.package = pkg
        booking.total_price = pkg.price * guest_count

    elif booking_type == 'hotel':
        hotel = get_object_or_404(Hotel, pk=item_id)
        room_type_id = request.POST.get('room_type_id')
        if room_type_id:
            room_type = get_object_or_404(RoomType, pk=room_type_id, hotel=hotel, is_active=True)
            booking.hotel = hotel
            booking.room_type = room_type
            booking.total_price = room_type.price_per_night * nights
        else:
            booking.hotel = hotel
            booking.total_price = hotel.price_per_night * nights

    elif booking_type == 'flight':
        flight = get_object_or_404(Flight, pk=item_id)
        seat_class_id = request.POST.get('seat_class_id')
        if seat_class_id:
            seat_class = get_object_or_404(SeatClass, pk=seat_class_id, flight=flight)
            booking.flight = flight
            booking.seat_class = seat_class
            booking.total_price = seat_class.price * guest_count
        else:
            booking.flight = flight
            booking.total_price = flight.price * guest_count

    elif booking_type == 'custom':
        flight_id = request.POST.get('flight_id')
        hotel_id = request.POST.get('hotel_id')
        nights = int(request.POST.get('nights', 1))
        total = Decimal('0')

        if flight_id:
            flight = get_object_or_404(Flight, pk=flight_id)
            seat_class_id = request.POST.get('seat_class_id')
            if seat_class_id:
                seat_class = get_object_or_404(SeatClass, pk=seat_class_id, flight=flight)
                booking.flight = flight
                booking.seat_class = seat_class
                total += seat_class.price * guest_count
            else:
                booking.flight = flight
                total += flight.price * guest_count

        if hotel_id:
            hotel = get_object_or_404(Hotel, pk=hotel_id)
            room_type_id = request.POST.get('room_type_id')
            if room_type_id:
                room_type = get_object_or_404(RoomType, pk=room_type_id, hotel=hotel, is_active=True)
                booking.hotel = hotel
                booking.room_type = room_type
                total += room_type.price_per_night * nights
            else:
                booking.hotel = hotel
                total += hotel.price_per_night * nights

        discount = total * PACKAGE_BUNDLE_DISCOUNT_RATE
        booking.discount_amount = discount
        booking.total_price = total - discount
        booking.check_in = check_in
        booking.check_out = check_out

    else:
        messages.error(request, '无效的预订类型')
        return redirect('index')

    ok, err_msg = _validate_inventory(booking)
    if not ok:
        messages.error(request, err_msg)
        return redirect(request.META.get('HTTP_REFERER', 'index'))

    booking.save()

    extra_service_ids = request.POST.getlist('extra_services')
    if extra_service_ids:
        services = ExtraService.objects.filter(pk__in=extra_service_ids, is_active=True)
        booking.extra_services.set(services)
        booking.total_price += sum(s.price for s in services)
        booking.save()

    messages.success(request, '预订成功！订单状态为"待支付"，请尽快完成支付。')
    return redirect('my_bookings')


@login_required
def pay_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status == 'pending':
        with transaction.atomic():
            booking.status = 'paid'
            booking.save()
            _decrement_inventory(booking)
        messages.success(request, '支付成功！订单已确认。')
    elif booking.status == 'paid':
        booking.status = 'confirmed'
        booking.save()
        messages.success(request, '订单已确认！')
    return redirect('my_bookings')


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status in ('pending', 'paid'):
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, '订单已取消')
    return redirect('my_bookings')


def custom_package(request):
    flights = Flight.objects.filter(is_active=True).prefetch_related('seat_classes')
    hotels = Hotel.objects.filter(is_active=True).prefetch_related('room_types')
    extra_services = ExtraService.objects.filter(is_active=True)

    flight_options = {}
    for flight in flights:
        flight_options[str(flight.pk)] = {
            'price': float(flight.price),
            'seats': [
                {'id': s.pk, 'label': s.get_class_type_display(), 'price': float(s.price)}
                for s in flight.seat_classes.all()
            ],
        }

    hotel_options = {}
    for hotel in hotels:
        hotel_options[str(hotel.pk)] = {
            'price': float(hotel.price_per_night),
            'rooms': [
                {'id': r.pk, 'label': r.name, 'price': float(r.price_per_night)}
                for r in hotel.room_types.filter(is_active=True)
            ],
        }

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, '请先登录后再预订定制套餐')
            return redirect_to_login(request.get_full_path())
        return create_booking(request)

    return render(request, 'custom_package.html', {
        'flights': flights,
        'hotels': hotels,
        'extra_services': extra_services,
        'flight_options_json': json.dumps(flight_options),
        'hotel_options_json': json.dumps(hotel_options),
    })


@login_required
def toggle_favorite(request):
    fav_type = request.POST.get('favorite_type')
    item_id = request.POST.get('item_id')
    next_url = request.POST.get('next', 'index')

    filters = {'user': request.user, 'favorite_type': fav_type}
    if fav_type == 'package':
        filters['package_id'] = item_id
    elif fav_type == 'hotel':
        filters['hotel_id'] = item_id
    elif fav_type == 'flight':
        filters['flight_id'] = item_id
    elif fav_type == 'blog':
        filters['blog_post_id'] = item_id
    elif fav_type == 'destination':
        filters['destination_id'] = item_id
    else:
        messages.error(request, '无效的收藏类型')
        return redirect(next_url)

    existing = Favorite.objects.filter(**filters).first()
    if existing:
        existing.delete()
        messages.info(request, '已取消收藏')
    else:
        Favorite.objects.create(**filters)
        messages.success(request, '收藏成功')
    return redirect(next_url)


@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'my_favorites.html', {'favorites': favorites})


@login_required
def submit_review(request):
    if request.method != 'POST':
        return redirect('index')

    review_type = request.POST.get('review_type')
    item_id = request.POST.get('item_id')
    next_url = request.POST.get('next', 'index')

    review = UserReview(
        user=request.user,
        review_type=review_type,
        rating=int(request.POST.get('rating', 5)),
        title=request.POST.get('title', ''),
        content=request.POST.get('content', ''),
        image_url=request.POST.get('image_url', ''),
    )

    if request.FILES.get('image'):
        review.image = request.FILES['image']

    if review_type == 'package':
        review.package_id = item_id
    elif review_type == 'hotel':
        review.hotel_id = item_id
    elif review_type == 'flight':
        review.flight_id = item_id
    elif review_type == 'destination':
        review.destination_id = item_id
    else:
        messages.error(request, '无效的评价类型')
        return redirect(next_url)

    review.save()
    messages.success(request, '评价提交成功，感谢您的分享！')
    return redirect(next_url)


def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            _, created = Subscriber.objects.get_or_create(email=email)
            if created:
                messages.success(request, '订阅成功，感谢您的关注！')
            else:
                messages.info(request, '您已订阅过我们的资讯')
        else:
            messages.error(request, '请输入有效的邮箱地址')
    return redirect('index')


def search(request):
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '')
    if not query:
        return redirect('index')

    packages = TourPackage.objects.filter(is_active=True, name__icontains=query)
    hotels = Hotel.objects.filter(is_active=True, name__icontains=query)
    flights = Flight.objects.filter(
        Q(is_active=True) & (
            Q(origin_city__icontains=query) |
            Q(destination_city__icontains=query) |
            Q(airline__icontains=query)
        )
    )
    destinations = Destination.objects.filter(
        Q(is_active=True) & (
            Q(name__icontains=query) |
            Q(country__icontains=query) |
            Q(city__icontains=query)
        )
    )

    if sort == 'price_asc':
        packages = packages.order_by('price')
        hotels = hotels.order_by('price_per_night')
        flights = flights.order_by('price')
    elif sort == 'price_desc':
        packages = packages.order_by('-price')
        hotels = hotels.order_by('-price_per_night')
        flights = flights.order_by('-price')

    return render(request, 'search_results.html', {
        'query': query,
        'packages': packages,
        'hotels': hotels,
        'flights': flights,
        'destinations': destinations,
        'sort': sort,
        'best_package': get_best_deal(list(packages), 'price'),
        'best_hotel': get_best_deal(list(hotels), 'price_per_night'),
        'best_flight': get_best_deal(list(flights), 'price'),
    })
