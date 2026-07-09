from django.db import migrations


def seed_more_travel_packages(apps, schema_editor):
    TravelPackage = apps.get_model('travel_app', 'TravelPackage')

    packages = [
        {
            'slug': 'thailand-phuket-island',
            'name': '泰国普吉岛海岛悠享 5 日',
            'destination': '泰国',
            'price': '¥5,299 起',
            'image_url': 'https://images.unsplash.com/photo-1508009603885-50cf7c579365?auto=format&fit=crop&w=900&q=80',
            'fallback_image': 'images/packages/p1.jpg',
            'duration': '5 天 4 晚',
            'hotel': '海滨度假酒店',
            'transport': '接送机 + 跳岛船票',
            'meal': '海鲜晚餐 + 泰式料理',
            'highlights': '皮皮岛出海\n普吉老街漫步\n海滨日落晚餐',
            'rating': 5,
            'reviews': 2875,
            'display_order': 6,
        },
        {
            'slug': 'iceland-aurora-ringroad',
            'name': '冰岛极光与南岸瀑布 7 日',
            'destination': '冰岛',
            'price': '¥18,900 起',
            'image_url': 'https://images.unsplash.com/photo-1483347756197-71ef80e95f73?auto=format&fit=crop&w=900&q=80',
            'fallback_image': 'images/packages/p2.jpg',
            'duration': '7 天 6 晚',
            'hotel': '雷克雅未克精选酒店',
            'transport': '当地环线巴士 + 专车',
            'meal': '酒店早餐 + 温泉体验',
            'highlights': '极光观测\n黄金圈路线\n黑沙滩与瀑布',
            'rating': 5,
            'reviews': 1548,
            'display_order': 7,
        },
        {
            'slug': 'egypt-cairo-nile',
            'name': '埃及金字塔与尼罗河巡游 8 日',
            'destination': '埃及',
            'price': '¥12,800 起',
            'image_url': 'https://images.unsplash.com/photo-1503177119275-0aa32b3a936c?auto=format&fit=crop&w=900&q=80',
            'fallback_image': 'images/packages/p3.jpg',
            'duration': '8 天 7 晚',
            'hotel': '开罗五星酒店 + 游轮',
            'transport': '内陆航班 + 游轮',
            'meal': '船上餐食 + 当地风味餐',
            'highlights': '吉萨金字塔\n卢克索神庙\n尼罗河游轮',
            'rating': 5,
            'reviews': 1986,
            'display_order': 8,
        },
        {
            'slug': 'peru-machu-picchu',
            'name': '秘鲁马丘比丘古文明 9 日',
            'destination': '秘鲁',
            'price': '¥22,600 起',
            'image_url': 'https://images.unsplash.com/photo-1526392060635-9d6019884377?auto=format&fit=crop&w=900&q=80',
            'fallback_image': 'images/packages/p4.jpg',
            'duration': '9 天 8 晚',
            'hotel': '利马 + 库斯科精选酒店',
            'transport': '内陆航班 + 景区火车',
            'meal': '安第斯风味餐',
            'highlights': '马丘比丘遗址\n库斯科老城\n圣谷火车之旅',
            'rating': 5,
            'reviews': 1124,
            'display_order': 9,
        },
        {
            'slug': 'new-zealand-south-island',
            'name': '新西兰南岛湖山自驾 8 日',
            'destination': '新西兰',
            'price': '¥17,500 起',
            'image_url': 'https://images.unsplash.com/photo-1469521669194-babb45599def?auto=format&fit=crop&w=900&q=80',
            'fallback_image': 'images/packages/p5.jpg',
            'duration': '8 天 7 晚',
            'hotel': '湖景酒店 + 小镇民宿',
            'transport': '租车自驾套餐',
            'meal': '酒店早餐 + 酒庄午餐',
            'highlights': '皇后镇湖景\n库克山国家公园\n米尔福德峡湾',
            'rating': 5,
            'reviews': 1762,
            'display_order': 10,
        },
        {
            'slug': 'singapore-family-city',
            'name': '新加坡亲子城市乐园 4 日',
            'destination': '新加坡',
            'price': '¥4,899 起',
            'image_url': 'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?auto=format&fit=crop&w=900&q=80',
            'fallback_image': 'images/packages/p6.jpg',
            'duration': '4 天 3 晚',
            'hotel': '市中心亲子酒店',
            'transport': '机场接送 + 地铁卡',
            'meal': '娘惹餐 + 美食中心体验',
            'highlights': '滨海湾花园\n圣淘沙乐园\n夜间动物园',
            'rating': 5,
            'reviews': 2468,
            'display_order': 11,
        },
        {
            'slug': 'morocco-sahara-medina',
            'name': '摩洛哥撒哈拉与古城 8 日',
            'destination': '摩洛哥',
            'price': '¥13,900 起',
            'image_url': 'https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?auto=format&fit=crop&w=900&q=80',
            'fallback_image': 'images/packages/p1.jpg',
            'duration': '8 天 7 晚',
            'hotel': '传统庭院酒店 + 沙漠营地',
            'transport': '越野车 + 城际用车',
            'meal': '塔吉锅 + 沙漠晚餐',
            'highlights': '马拉喀什老城\n撒哈拉星空\n舍夫沙万蓝城',
            'rating': 5,
            'reviews': 1329,
            'display_order': 12,
        },
        {
            'slug': 'usa-newyork-museum',
            'name': '美国纽约博物馆与天际线 6 日',
            'destination': '美国',
            'price': '¥11,600 起',
            'image_url': 'https://images.unsplash.com/photo-1485871981521-5b1fd3805eee?auto=format&fit=crop&w=900&q=80',
            'fallback_image': 'images/packages/p2.jpg',
            'duration': '6 天 5 晚',
            'hotel': '曼哈顿精选酒店',
            'transport': '机场接送 + 城市通票',
            'meal': '百老汇周边晚餐',
            'highlights': '大都会博物馆\n自由女神游船\n帝国大厦夜景',
            'rating': 5,
            'reviews': 2054,
            'display_order': 13,
        },
    ]

    for package in packages:
        TravelPackage.objects.update_or_create(
            slug=package['slug'],
            defaults={**package, 'is_featured': True, 'is_active': True},
        )


def remove_more_travel_packages(apps, schema_editor):
    TravelPackage = apps.get_model('travel_app', 'TravelPackage')
    TravelPackage.objects.filter(
        slug__in=[
            'thailand-phuket-island',
            'iceland-aurora-ringroad',
            'egypt-cairo-nile',
            'peru-machu-picchu',
            'new-zealand-south-island',
            'singapore-family-city',
            'morocco-sahara-medina',
            'usa-newyork-museum',
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('travel_app', '0008_alter_travelpackage_is_featured'),
    ]

    operations = [
        migrations.RunPython(seed_more_travel_packages, remove_more_travel_packages),
    ]
