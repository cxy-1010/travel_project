from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from travel_app import booking_views, views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_page, name='home'),
    path('packages/', booking_views.packages_page, name='packages'),
    path('destinations/<str:destination>/packages/', booking_views.destination_packages, name='destination_packages'),
    path('book-package/<str:package_id>/', booking_views.book_package, name='book_package'),
    path('my-bookings/', booking_views.my_bookings, name='my_bookings'),
    path('my-bookings/<int:booking_id>/', booking_views.booking_detail, name='booking_detail'),
    path('ai-assistant/', booking_views.ai_assistant, name='ai_assistant'),
    path('hotel-search/', booking_views.hotel_search, name='hotel_search'),
    path('flight-search/', booking_views.flight_search, name='flight_search'),
    path('api/hotel-search/', booking_views.hotel_ai_search, name='hotel_ai_search'),
    path('api/flight-search/', booking_views.flight_ai_search, name='flight_ai_search'),
    path('api/search/', booking_views.search_ai, name='search_ai'),
    path('login/', booking_views.UserLoginView.as_view(), name='login'),
    path('register/', booking_views.register, name='register'),
    path('api/send-email-code/', booking_views.send_email_code, name='send_email_code'),
    path('logout/', booking_views.user_logout_page, name='logout'),
    path('profile/', booking_views.profile, name='profile'),
    
    # 基础与认证API（同学A主控）
    path('api/register/', views.user_register),
    path('api/login/', views.user_login),
    path('api/logout/', views.user_logout),
    
    # 搜索与预订API（同学C主控）
    path('api/search/flights/', views.search_flights),
    path('api/search/hotels/', views.search_hotels),
    path('api/order/create/', views.create_order),
    path('api/order/my/', views.my_orders),
    
    # 攻略与社区API（同学D主控 - 你）
    path('api/guides/', views.get_guides),
    path('api/guides/<int:guide_id>/', views.guide_detail),
    path('api/guides/create/', views.create_guide),
    path('api/guides/<int:guide_id>/like/', views.like_guide),
    path('api/guides/<int:guide_id>/favorite/', views.favorite_guide),
    path('api/guides/<int:guide_id>/comment/', views.add_guide_comment),
    path('api/news/<int:news_id>/favorite/', views.favorite_news),

    path('news/', views.news_list, name='news_list'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('news/all/', views.news_all_hub, name='news_all_hub'),
    path('favorites/', views.favorites_page, name='favorites'),
    path('comments/', views.comments_page, name='comments'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
