from django.db import migrations


def seed_travel_packages(apps, schema_editor):
    TravelPackage = apps.get_model('travel_app', 'TravelPackage')

    packages = [
        {
            'slug': 'santorini-volcano-sea',
            'name': '希腊圣托里尼火山海景 6 日',
            'destination': '希腊',
            'price': '¥8,999 起',
            'image_url': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=900&q=80',
            'fallback_image': 'images/packages/p1.jpg',
            'duration': '6 天 5 晚',
            'hotel': '悬崖海景酒店',
            'transport': '接送机 + 岛内用车',
            'meal': '特色晚餐 + 酒庄体验',
            'rating': 5,
            'reviews': 2680,
        },
        {
            'slug': 'kyoto-culture',
            'name': '日本京都古都文化 5 日',
            'destination': '日本',
            'price': '¥6,499 起',
            'image_url': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=900&q=80',
            'fallback_image': 'images/packages/p2.jpg',
            'duration': '5 天 4 晚',
            'hotel': '市中心精选酒店',
            'transport': '关西机场接送',
            'meal': '茶道 + 和风料理',
            'rating': 5,
            'reviews': 2146,
        },
        {
            'slug': 'bali-ubud-coast',
            'name': '巴厘岛海岸与乌布疗愈 6 日',
            'destination': '巴厘岛',
            'price': '¥7,299 起',
            'image_url': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=900&q=80',
            'fallback_image': 'images/packages/p3.jpg',
            'duration': '6 天 5 晚',
            'hotel': '泳池度假酒店',
            'transport': '专车环岛游',
            'meal': '海景下午茶 + 当地餐',
            'rating': 5,
            'reviews': 3098,
        },
        {
            'slug': 'swiss-alps-train',
            'name': '瑞士少女峰全景列车 7 日',
            'destination': '瑞士',
            'price': '¥16,800 起',
            'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=900&q=80',
            'fallback_image': 'images/packages/p4.jpg',
            'duration': '7 天 6 晚',
            'hotel': '湖区精品酒店',
            'transport': '瑞士铁路通票',
            'meal': '山景早餐 + 奶酪火锅',
            'rating': 5,
            'reviews': 1864,
        },
        {
            'slug': 'paris-art-seine',
            'name': '巴黎艺术与塞纳河漫游 5 日',
            'destination': '法国',
            'price': '¥9,699 起',
            'image_url': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=900&q=80',
            'fallback_image': 'images/packages/p5.jpg',
            'duration': '5 天 4 晚',
            'hotel': '左岸或歌剧院商圈',
            'transport': '市区交通卡',
            'meal': '法式甜点 + 塞纳河晚餐',
            'rating': 5,
            'reviews': 2410,
        },
        {
            'slug': 'maldives-island',
            'name': '马尔代夫双人岛屿假期 6 日',
            'destination': '马尔代夫',
            'price': '¥14,999 起',
            'image_url': 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?auto=format&fit=crop&w=900&q=80',
            'fallback_image': 'images/packages/p6.jpg',
            'duration': '6 天 4 晚',
            'hotel': '沙屋/水屋可选',
            'transport': '快艇或水飞接驳',
            'meal': '早晚餐 + 浮潜体验',
            'rating': 5,
            'reviews': 3342,
        },
    ]

    for index, package in enumerate(packages):
        TravelPackage.objects.update_or_create(
            slug=package['slug'],
            defaults={**package, 'display_order': index, 'is_featured': True, 'is_active': True},
        )


def remove_seeded_travel_packages(apps, schema_editor):
    TravelPackage = apps.get_model('travel_app', 'TravelPackage')
    TravelPackage.objects.filter(
        slug__in=[
            'santorini-volcano-sea',
            'kyoto-culture',
            'bali-ubud-coast',
            'swiss-alps-train',
            'paris-art-seine',
            'maldives-island',
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('travel_app', '0006_travelpackage'),
    ]

    operations = [
        migrations.RunPython(seed_travel_packages, remove_seeded_travel_packages),
    ]
