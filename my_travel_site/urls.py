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
    # 🌟 第二步：给首页牵线搭桥。第一个参数 '' 代表网址根目录
    path('', views.index, name='index'),
]