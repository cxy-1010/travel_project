"""
URL configuration for my_travel_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
from travel_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
]
