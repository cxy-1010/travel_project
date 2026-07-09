"""
URL configuration for my_travel_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from travel_app import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('destinations/<str:destination>/packages/', views.destination_packages, name='destination_packages'),
    path('ai-assistant/', views.ai_assistant, name='ai_assistant'),
    path('hotel-search/', views.hotel_search, name='hotel_search'),
    path('flight-search/', views.flight_search, name='flight_search'),
    path('api/hotel-search/', views.hotel_ai_search, name='hotel_ai_search'),
    path('api/flight-search/', views.flight_ai_search, name='flight_ai_search'),
    path('api/search/', views.search_ai, name='search_ai'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
