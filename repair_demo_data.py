# -*- coding: utf-8 -*-
import os
from datetime import datetime, date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_travel_site.settings")

import django
django.setup()

from django.utils import timezone
from travel_app.models import (
    Destination,
    TourPackage,
    Hotel,
    Flight,
    BlogPost,
    Testimonial,
    SpecialOffer,
    RoomType,
    SeatClass,
    ExtraService,
)


def main():
    Destination.objects.all().update(is_active=False)
    TourPackage.objects.all().update(is_active=False)
    Hotel.objects.all().update(is_active=False)
    Flight.objects.all().update(is_active=False)
    BlogPost.objects.all().update(is_published=False)
    Testimonial.objects.all().update(is_active=False)
    SpecialOffer.objects.all().update(is_active=False)

    destinations = [
        ("中国", "China", "中国", "北京", "images/gallary/g1.jpg", "历史古都与现代都市交织，适合文化、美食与城市漫游。"),
        ("委内瑞拉", "Venezuela", "委内瑞拉", "卡奈玛", "images/gallary/g2.jpg", "瀑布、雨林和南美自然风光的代表目的地。"),
        ("巴西", "Brazil", "巴西", "里约热内卢", "images/gallary/g3.jpg", "海滩、足球、桑巴和山海城市景观融合。"),
        ("澳大利亚", "Australia", "澳大利亚", "悉尼", "images/gallary/g4.jpg", "海港城市、自然公园和滨海自驾路线丰富。"),
        ("荷兰", "Netherlands", "荷兰", "阿姆斯特丹", "images/gallary/g5.jpg", "运河、博物馆、骑行和欧洲小城风景。"),
        ("土耳其", "Turkey", "土耳其", "伊斯坦布尔", "images/gallary/g6.jpg", "横跨欧亚的文化之城，适合热气球与古城路线。"),
        ("法国", "France", "法国", "巴黎", "images/packages/p3.jpg", "艺术、建筑、美食和浪漫城市体验。"),
        ("泰国", "Thailand", "泰国", "曼谷", "images/packages/p6.jpg", "海岛、夜市、寺庙和热带度假体验。"),
    ]
    dest_map = {}
    for name, name_en, country, city, image_url, description in destinations:
        obj, _ = Destination.objects.update_or_create(
            name=name,
            defaults={
                "name_en": name_en,
                "country": country,
                "city": city,
                "image_url": image_url,
                "description": description,
                "is_active": True,
            },
        )
        dest_map[name] = obj

    packages = [
        ("土耳其热气球奇幻之旅", "土耳其", 1299, 1699, 5, 6, "images/packages/p1.jpg", "卡帕多奇亚热气球\n伊斯坦布尔老城漫步\n五星酒店住宿\n当地特色餐食", True),
        ("俄罗斯冬日童话游", "荷兰", 1099, 1399, 5, 6, "images/packages/p2.jpg", "经典城市观光\n雪景摄影路线\n舒适往返交通\n中文导游服务", False),
        ("法国蔚蓝海岸浪漫游", "法国", 1199, 1499, 5, 6, "images/packages/p3.jpg", "巴黎城市漫游\n蔚蓝海岸度假\n精品酒店住宿\n艺术博物馆门票", True),
        ("印度古文明探索", "巴西", 799, 999, 5, 6, "images/packages/p4.jpg", "历史遗迹巡礼\n当地文化体验\n特色餐食\n安全出行保障", False),
        ("西班牙阳光沙滩游", "荷兰", 999, 1299, 5, 6, "images/packages/p5.jpg", "海滨城市度假\n艺术建筑参观\n自由活动时间\n精品酒店住宿", True),
        ("泰国狂欢海岛游", "泰国", 799, 1199, 5, 6, "images/packages/p6.jpg", "曼谷夜市\n海岛浮潜\n机场接送\n特色海鲜餐", False),
    ]
    for name, dest_name, price, original_price, days, nights, image_url, features, recommended in packages:
        TourPackage.objects.update_or_create(
            name=name,
            defaults={
                "destination": dest_map.get(dest_name),
                "price": price,
                "original_price": original_price,
                "duration_days": days,
                "duration_nights": nights,
                "rating": 4.8,
                "review_count": 1280,
                "image_url": image_url,
                "features": features,
                "is_recommended": recommended,
                "is_active": True,
            },
        )

    hotels = [
        ("伊斯坦布尔博斯普鲁斯大酒店", "土耳其", "伊斯坦布尔", 5, 680, "images/packages/p1.jpg", "海峡景观、早餐、机场接送", "免费WiFi\n机场接送\n海景房\n早餐"),
        ("莫斯科红场假日酒店", "荷兰", "莫斯科", 4, 520, "images/packages/p2.jpg", "靠近市中心，适合城市观光", "免费WiFi\n健身房\n家庭房"),
        ("巴黎香榭丽舍精品酒店", "法国", "巴黎", 5, 980, "images/packages/p3.jpg", "步行可达核心商圈和博物馆", "免费WiFi\n早餐\n行李寄存\n礼宾服务"),
        ("曼谷河畔度假酒店", "泰国", "曼谷", 5, 460, "images/packages/p6.jpg", "河畔泳池与城市夜景", "泳池\n免费WiFi\nSpa\n接机服务"),
    ]
    for name, dest_name, city, stars, price, image_url, description, amenities in hotels:
        hotel, _ = Hotel.objects.update_or_create(
            name=name,
            defaults={
                "destination": dest_map.get(dest_name),
                "city": city,
                "stars": stars,
                "price_per_night": price,
                "rating": 4.7,
                "review_count": 860,
                "image_url": image_url,
                "description": description,
                "amenities": amenities,
                "is_active": True,
            },
        )
        RoomType.objects.update_or_create(
            hotel=hotel,
            name="标准双人间",
            defaults={"price_per_night": price, "capacity": 2, "available_rooms": 8, "description": "含双早，适合双人入住", "is_active": True},
        )
        RoomType.objects.update_or_create(
            hotel=hotel,
            name="豪华景观房",
            defaults={"price_per_night": price + 220, "capacity": 2, "available_rooms": 5, "description": "更大面积和景观楼层", "is_active": True},
        )

    flights = [
        ("中国国际航空", "CA1234", "北京", "伊斯坦布尔", 3200, "one_way"),
        ("中国东方航空", "MU5678", "上海", "巴黎", 3800, "round_trip"),
        ("泰国国际航空", "TG675", "上海", "曼谷", 1800, "round_trip"),
        ("南方航空", "CZ9876", "广州", "悉尼", 4200, "one_way"),
    ]
    for idx, (airline, number, origin, target, price, flight_type) in enumerate(flights, start=1):
        existing = Flight.objects.filter(flight_number=number).order_by("pk")
        if existing.count() > 1:
            existing.exclude(pk=existing.first().pk).delete()
        dep = timezone.make_aware(datetime(2026, 8, 10 + idx, 9 + idx, 0))
        arr = timezone.make_aware(datetime(2026, 8, 10 + idx, 15 + idx, 30))
        flight, _ = Flight.objects.update_or_create(
            flight_number=number,
            defaults={
                "airline": airline,
                "origin_city": origin,
                "destination_city": target,
                "departure_time": dep,
                "arrival_time": arr,
                "price": price,
                "flight_type": flight_type,
                "seats_available": 80,
                "is_active": True,
            },
        )
        SeatClass.objects.update_or_create(flight=flight, class_type="economy", defaults={"price": price, "available_seats": 50})
        SeatClass.objects.update_or_create(flight=flight, class_type="business", defaults={"price": int(price * 1.8), "available_seats": 12})

    blogs = [
        ("漫步布拉格：温和气候与古城建筑攻略", "guide", "images/blog/b1.jpg", "用一天时间走过古城广场、查理大桥和传统小吃街。"),
        ("印度奇幻色彩之旅：历史建筑与安全提示", "tips", "images/blog/b2.jpg", "整理交通、景点、饮食和拍摄建议，适合第一次前往的游客。"),
        ("全球十大自然景观目的地推荐", "guide", "images/blog/b3.jpg", "从冰川、雨林到草原，挑选适合长线旅行的自然景观。"),
    ]
    for title, category, image_url, excerpt in blogs:
        BlogPost.objects.update_or_create(
            title=title,
            defaults={
                "category": category,
                "author": "TourNest 编辑部",
                "excerpt": excerpt,
                "content": excerpt + "\n\n本攻略包含交通、住宿、餐饮和避坑建议，适合作为行前规划参考。",
                "image_url": image_url,
                "published_date": date(2026, 7, 1),
                "is_published": True,
            },
        )

    testimonials = [
        ("凯文·沃森", "英国，伦敦", "images/client/testimonial1.jpg", "套餐安排紧凑但不赶，酒店和机票比价确实省了不少时间。"),
        ("珍妮·苏", "美国，纽约", "images/client/testimonial2.jpg", "订房和机票流程很顺，收藏和攻略页面对计划行程很有帮助。"),
    ]
    for guest_name, location, avatar_url, quote in testimonials:
        Testimonial.objects.update_or_create(
            guest_name=guest_name,
            defaults={"location": location, "avatar_url": avatar_url, "quote": quote, "rating": 5, "is_active": True},
        )

    SpecialOffer.objects.update_or_create(
        title="暑期特惠：东南亚海岛游",
        defaults={
            "subtitle": "机票酒店组合优惠",
            "description": "曼谷与海岛路线限时组合，适合家庭和情侣出行。",
            "discount": 60,
            "price": 999,
            "original_price": 1450,
            "image_url": "images/offer/offer-banner.jpg",
            "features": "海岛浮潜\n机场接送\n特色海鲜餐",
            "is_active": True,
        },
    )

    services = [
        ("基础旅游保险", "insurance", 88, "覆盖常见旅行意外与延误保障"),
        ("机场接送服务", "pickup", 160, "当地司机机场至酒店单程接送"),
        ("额外行李额度", "luggage", 120, "适合长线出行和购物返程"),
        ("私人中文导游", "guide", 480, "半日中文陪同讲解服务"),
    ]
    for name, service_type, price, description in services:
        ExtraService.objects.update_or_create(
            name=name,
            defaults={"service_type": service_type, "price": price, "description": description, "is_active": True},
        )

    print("demo data repaired")


if __name__ == "__main__":
    main()
