from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from travel_app import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # 首页
    path('', views.index, name='index'),

    # 用户认证
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='user_profile'),
    path('change-currency/', views.change_currency, name='change_currency'),

    # 订单
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('create-booking/', views.create_booking, name='create_booking'),
    path('pay-booking/<int:pk>/', views.pay_booking, name='pay_booking'),
    path('cancel-booking/<int:pk>/', views.cancel_booking, name='cancel_booking'),

    # 定制套餐
    path('custom-package/', views.custom_package, name='custom_package'),

    # 收藏与评价
    path('my-favorites/', views.my_favorites, name='my_favorites'),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('submit-review/', views.submit_review, name='submit_review'),

    # 套餐
    path('packages/', views.package_list, name='package_list'),
    path('package/<int:pk>/', views.package_detail, name='package_detail'),

    # 酒店
    path('hotels/', views.hotel_list, name='hotel_list'),
    path('hotel/<int:pk>/', views.hotel_detail, name='hotel_detail'),

    # 航班
    path('flights/', views.flight_list, name='flight_list'),
    path('flight/<int:pk>/', views.flight_detail, name='flight_detail'),

    # 攻略
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),

    # 目的地
    path('destinations/', views.destination_list, name='destination_list'),
    path('destination/<int:pk>/', views.destination_detail, name='destination_detail'),

    # 订阅与搜索
    path('subscribe/', views.subscribe, name='subscribe'),
    path('search/', views.search, name='search'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
