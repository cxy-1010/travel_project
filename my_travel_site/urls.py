"""
URL configuration for my_travel_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from travel_app import booking_views, views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('packages/', booking_views.packages_page, name='packages'),
    path('destinations/<str:destination>/packages/', views.destination_packages, name='destination_packages'),
    path('book-package/<str:package_id>/', views.book_package, name='book_package'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('my-bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('ai-assistant/', views.ai_assistant, name='ai_assistant'),
    path('hotel-search/', views.hotel_search, name='hotel_search'),
    path('flight-search/', views.flight_search, name='flight_search'),
    path('api/hotel-search/', views.hotel_ai_search, name='hotel_ai_search'),
    path('api/flight-search/', views.flight_ai_search, name='flight_ai_search'),
    path('api/search/', views.search_ai, name='search_ai'),
    path('api/register/', views.user_register),
    path('api/login/', views.user_login),
    path('api/logout/', views.api_user_logout),
    path('api/search/flights/', views.search_flights),
    path('api/search/hotels/', views.search_hotels),
    path('api/order/create/', views.create_order),
    path('api/order/my/', views.my_orders),
    path('api/guides/', views.get_guides),
    path('api/guides/<int:guide_id>/', views.guide_detail),
    path('api/guides/create/', views.create_guide),
    path('api/guides/<int:guide_id>/like/', views.like_guide),
    path('api/guides/<int:guide_id>/favorite/', views.favorite_guide),
    path('api/guides/<int:guide_id>/comment/', views.add_guide_comment),
    path('api/external-guides/', views.external_guides),
    path('api/proxy-image/', views.proxy_image),
    path('api/news/<int:news_id>/favorite/', views.favorite_news),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('api/send-email-code/', views.send_email_code, name='send_email_code'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('news/', views.news_list, name='news_list'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('news/all/', views.news_all_hub, name='news_all_hub'),
    path('favorites/', views.favorites_page, name='favorites'),
    path('comments/', views.comments_page, name='comments'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
