"""
URL configuration for my_travel_site project.
"""
from django.contrib import admin
from django.urls import path
from travel_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # 首页 - 展示套餐列表
    path('', views.index, name='index'),
    # 用户注册/登录
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # 套餐预订
    path('book/<int:package_id>/', views.book_package, name='book_package'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    # 攻略相关
    path('api/guides/', views.get_guides, name='get_guides'),
    path('api/guides/<int:guide_id>/', views.guide_detail, name='guide_detail'),
    path('api/guides/create/', views.create_guide, name='create_guide'),
    path('api/guides/<int:guide_id>/like/', views.like_guide, name='like_guide'),
    path('api/guides/<int:guide_id>/comments/', views.add_guide_comment, name='add_guide_comment'),
    # JSON API
    path('api/packages/', views.get_packages_json, name='get_packages_json'),
    path('api/packages/<int:package_id>/', views.get_package_detail, name='get_package_detail'),
    path('api/flights-hotels/', views.get_flights_hotels_json, name='get_flights_hotels_json'),
    # 管理员 API
    path('api/flights/add/', views.add_flight, name='add_flight'),
    path('api/hotels/add/', views.add_hotel, name='add_hotel'),
    path('api/flight-prices/add/', views.add_flight_price, name='add_flight_price'),
    path('api/hotel-rooms/add/', views.add_hotel_room, name='add_hotel_room'),
    path('api/packages/create/', views.create_package, name='create_package'),
    path('api/packages/<int:package_id>/delete/', views.delete_package, name='delete_package'),
]
