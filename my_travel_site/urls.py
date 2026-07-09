"""
URL configuration for my_travel_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
# 🌟 第一步：把我们刚才写好主管函数的 views.py 引入进来
from travel_app import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('ai-assistant/', views.ai_assistant, name='ai_assistant'),
    path('hotel-search/', views.hotel_search, name='hotel_search'),
    path('api/hotel-search/', views.hotel_ai_search, name='hotel_ai_search'),
    path('api/search/', views.search_ai, name='search_ai'),
]
