from django.contrib import admin
from django.urls import path
from travel_app import views

urlpatterns = [
    path('', views.home_page, name='home'),
    
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
