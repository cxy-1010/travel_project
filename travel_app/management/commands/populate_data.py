from datetime import datetime, date

from django.core.management.base import BaseCommand
from django.utils import timezone

from travel_app.models import (
    Destination, TourPackage, Hotel, RoomType, Flight, SeatClass,
    ExtraService, Testimonial, BlogPost, SpecialOffer,
)


class Command(BaseCommand):
    help = '填充旅游预订网站的示例数据'

    def handle(self, *args, **options):
        self._create_destinations()
        self._create_packages()
        self._create_hotels()
        self._create_flights()
        self._create_extra_services()
        self._create_testimonials()
        self._create_blog_posts()
        self._create_special_offers()
        self.stdout.write(self.style.SUCCESS('示例数据填充完成！'))

    def _create_destinations(self):
        data = [
            {'name': '土耳其', 'name_en': 'Turkey', 'country': '土耳其', 'city': '伊斯坦布尔', 'image_url': 'images/gallery/g1.jpg'},
            {'name': '俄罗斯', 'name_en': 'Russia', 'country': '俄罗斯', 'city': '莫斯科', 'image_url': 'images/gallery/g2.jpg'},
            {'name': '埃及', 'name_en': 'Egypt', 'country': '埃及', 'city': '开罗', 'image_url': 'images/gallery/g3.jpg'},
            {'name': '法国', 'name_en': 'France', 'country': '法国', 'city': '巴黎', 'image_url': 'images/gallery/g4.jpg'},
            {'name': '印度', 'name_en': 'India', 'country': '印度', 'city': '新德里', 'image_url': 'images/gallery/g5.jpg'},
            {'name': '西班牙', 'name_en': 'Spain', 'country': '西班牙', 'city': '巴塞罗那', 'image_url': 'images/gallery/g6.jpg'},
            {'name': '泰国', 'name_en': 'Thailand', 'country': '泰国', 'city': '曼谷', 'image_url': 'images/gallery/g7.jpg'},
            {'name': '中国', 'name_en': 'China', 'country': '中国', 'city': '北京', 'image_url': 'images/gallery/g8.jpg'},
        ]
        for item in data:
            dest, created = Destination.objects.get_or_create(name=item['name'], defaults=item)
            if created:
                self.stdout.write(f'  创建目的地: {dest.name}')

    def _create_packages(self):
        turkey = Destination.objects.filter(name='土耳其').first()
        france = Destination.objects.filter(name='法国').first()
        india = Destination.objects.filter(name='印度').first()
        spain = Destination.objects.filter(name='西班牙').first()
        thailand = Destination.objects.filter(name='泰国').first()

        data = [
            {
                'name': '伊斯坦布尔文化探索之旅', 'destination': turkey, 'price': 8999, 'duration_days': 5, 'duration_nights': 6,
                'review_count': 2544, 'image_url': 'images/packages/p1.jpg',
                'features': '5 天 6 晚\n5星级豪华酒店\n含早餐\n专业中文导游',
                'is_recommended': True,
            },
            {
                'name': '东南亚海岛度假套餐', 'destination': None, 'price': 7599, 'duration_days': 5, 'duration_nights': 6,
                'review_count': 1842, 'image_url': 'images/packages/p2.jpg',
                'features': '5 天 6 晚\n海景度假酒店\n含早餐\n浮潜体验',
            },
            {
                'name': '巴黎浪漫之旅', 'destination': france, 'price': 8299, 'duration_days': 5, 'duration_nights': 6,
                'review_count': 3102, 'image_url': 'images/packages/p3.jpg',
                'features': '5 天 6 晚\n市中心精品酒店\n含早餐\n卢浮宫门票',
                'is_recommended': True,
            },
            {
                'name': '印度泰姬陵探秘', 'destination': india, 'price': 5599, 'duration_days': 5, 'duration_nights': 6,
                'review_count': 1205, 'image_url': 'images/packages/p4.jpg',
                'features': '5 天 6 晚\n特色民宿\n含早餐\n泰姬陵门票',
            },
            {
                'name': '西班牙艺术之旅', 'destination': spain, 'price': 6999, 'duration_days': 5, 'duration_nights': 6,
                'review_count': 1987, 'image_url': 'images/packages/p5.jpg',
                'features': '5 天 6 晚\n高迪建筑导览\n含早餐\n圣家堂门票',
                'is_recommended': True,
            },
            {
                'name': '泰国曼谷休闲游', 'destination': thailand, 'price': 5599, 'duration_days': 5, 'duration_nights': 6,
                'review_count': 2456, 'image_url': 'images/packages/p6.jpg',
                'features': '5 天 6 晚\n五星度假酒店\n含早餐\n大皇宫门票',
            },
        ]
        for item in data:
            dest = item.pop('destination', None)
            pkg, created = TourPackage.objects.get_or_create(name=item['name'], defaults={**item, 'destination': dest})
            if created:
                self.stdout.write(f'  创建套餐: {pkg.name}')

    def _create_hotels(self):
        data = [
            {
                'name': '伊斯坦布尔博斯普鲁斯大酒店', 'city': '伊斯坦布尔', 'stars': 5, 'price_per_night': 2450,
                'image_url': 'images/packages/p1.jpg', 'rating': 4.8, 'review_count': 1200,
                'amenities': '免费WiFi\n游泳池\n健身房\n餐厅',
                'rooms': [
                    {'name': '标准双人间', 'price_per_night': 2450, 'capacity': 2},
                    {'name': '豪华海景房', 'price_per_night': 3200, 'capacity': 2},
                    {'name': '行政套房', 'price_per_night': 4800, 'capacity': 4},
                ],
            },
            {
                'name': '莫斯科红场假日酒店', 'city': '莫斯科', 'stars': 5, 'price_per_night': 1960,
                'image_url': 'images/packages/p2.jpg', 'rating': 4.6, 'review_count': 980,
                'amenities': '免费WiFi\n商务中心\n餐厅\n停车场',
                'rooms': [
                    {'name': '经济单人间', 'price_per_night': 1400, 'capacity': 1},
                    {'name': '标准双人间', 'price_per_night': 1960, 'capacity': 2},
                    {'name': '家庭房', 'price_per_night': 2800, 'capacity': 4},
                ],
            },
            {
                'name': '巴黎香榭丽舍精品酒店', 'city': '巴黎', 'stars': 5, 'price_per_night': 5950,
                'image_url': 'images/packages/p3.jpg', 'rating': 4.9, 'review_count': 2100,
                'amenities': '免费WiFi\nSPA\n米其林餐厅\n礼宾服务',
                'rooms': [
                    {'name': '经典房', 'price_per_night': 5950, 'capacity': 2},
                    {'name': '露台套房', 'price_per_night': 8500, 'capacity': 2},
                ],
            },
            {
                'name': '曼谷河畔度假村', 'city': '曼谷', 'stars': 5, 'price_per_night': 1540,
                'image_url': 'images/packages/p6.jpg', 'rating': 4.7, 'review_count': 1560,
                'amenities': '免费WiFi\n无边泳池\n泰式SPA\n河景餐厅',
                'rooms': [
                    {'name': '园景房', 'price_per_night': 1540, 'capacity': 2},
                    {'name': '河景房', 'price_per_night': 2100, 'capacity': 2},
                    {'name': '泳池别墅', 'price_per_night': 3500, 'capacity': 4},
                ],
            },
        ]
        for item in data:
            rooms = item.pop('rooms', [])
            hotel, created = Hotel.objects.get_or_create(name=item['name'], defaults=item)
            if created:
                self.stdout.write(f'  创建酒店: {hotel.name}')
            for room in rooms:
                RoomType.objects.get_or_create(hotel=hotel, name=room['name'], defaults=room)

    def _create_flights(self):
        data = [
            {
                'airline': '中国国际航空', 'flight_number': 'CA1234', 'origin_city': '北京', 'destination_city': '伊斯坦布尔',
                'departure_time': timezone.make_aware(datetime(2026, 8, 1, 8, 30)),
                'arrival_time': timezone.make_aware(datetime(2026, 8, 1, 14, 0)),
                'price': 4480, 'flight_type': 'one_way',
                'seats': [
                    {'class_type': 'economy', 'price': 4480},
                    {'class_type': 'premium', 'price': 6200},
                    {'class_type': 'business', 'price': 12800},
                ],
            },
            {
                'airline': '东方航空', 'flight_number': 'MU5678', 'origin_city': '上海', 'destination_city': '莫斯科',
                'departure_time': timezone.make_aware(datetime(2026, 8, 3, 10, 0)),
                'arrival_time': timezone.make_aware(datetime(2026, 8, 3, 16, 30)),
                'price': 3920, 'flight_type': 'one_way',
                'seats': [
                    {'class_type': 'economy', 'price': 3920},
                    {'class_type': 'business', 'price': 10500},
                ],
            },
            {
                'airline': '土耳其航空', 'flight_number': 'TK2090', 'origin_city': '广州', 'destination_city': '伊斯坦布尔',
                'departure_time': timezone.make_aware(datetime(2026, 8, 5, 1, 15)),
                'arrival_time': timezone.make_aware(datetime(2026, 8, 5, 6, 45)),
                'price': 4060, 'flight_type': 'round_trip',
                'seats': [
                    {'class_type': 'economy', 'price': 4060},
                    {'class_type': 'premium', 'price': 5800},
                    {'class_type': 'business', 'price': 11200},
                ],
            },
            {
                'airline': '南方航空', 'flight_number': 'CZ9876', 'origin_city': '广州', 'destination_city': '巴黎',
                'departure_time': timezone.make_aware(datetime(2026, 8, 10, 9, 0)),
                'arrival_time': timezone.make_aware(datetime(2026, 8, 10, 15, 0)),
                'price': 6300, 'flight_type': 'one_way',
                'seats': [
                    {'class_type': 'economy', 'price': 6300},
                    {'class_type': 'business', 'price': 15800},
                ],
            },
            {
                'airline': '泰国国际航空', 'flight_number': 'TG675', 'origin_city': '成都', 'destination_city': '曼谷',
                'departure_time': timezone.make_aware(datetime(2026, 8, 15, 14, 30)),
                'arrival_time': timezone.make_aware(datetime(2026, 8, 15, 18, 0)),
                'price': 1680, 'flight_type': 'round_trip',
                'seats': [
                    {'class_type': 'economy', 'price': 1680},
                    {'class_type': 'premium', 'price': 2800},
                    {'class_type': 'business', 'price': 6500},
                ],
            },
        ]
        for item in data:
            seats = item.pop('seats', [])
            flight, created = Flight.objects.get_or_create(
                airline=item['airline'], flight_number=item['flight_number'],
                origin_city=item['origin_city'], destination_city=item['destination_city'],
                departure_time=item['departure_time'], defaults=item,
            )
            if created:
                self.stdout.write(f'  创建航班: {flight.airline} {flight.flight_number}')
            for seat in seats:
                SeatClass.objects.get_or_create(flight=flight, class_type=seat['class_type'], defaults=seat)

    def _create_extra_services(self):
        data = [
            {'name': '基础旅游保险', 'service_type': 'insurance', 'price': 150,
             'description': '涵盖意外伤害、医疗费用，保额10万元'},
            {'name': '全面旅游保险', 'service_type': 'insurance', 'price': 350,
             'description': '涵盖意外伤害、医疗费用、行李丢失，保额30万元'},
            {'name': '机场接机服务', 'service_type': 'pickup', 'price': 280,
             'description': '专车接机，直达酒店，含行李协助'},
            {'name': '行李托运加购', 'service_type': 'luggage', 'price': 120,
             'description': '额外托运一件23kg行李'},
            {'name': '签证代办服务', 'service_type': 'visa', 'price': 800,
             'description': '专业团队代办签证，含材料审核'},
            {'name': '私人导游服务', 'service_type': 'guide', 'price': 1200,
             'description': '全天中文私人导游，深度游览'},
        ]
        for item in data:
            svc, created = ExtraService.objects.get_or_create(name=item['name'], defaults=item)
            if created:
                self.stdout.write(f'  创建额外服务: {svc.name}')

    def _create_testimonials(self):
        data = [
            {'guest_name': '张明远', 'location': '北京', 'avatar_url': 'images/client/testimonial1.jpg',
             'quote': '通过TourNest预订的土耳其之旅非常完美，价格比其他平台便宜不少，客服响应也很及时！', 'rating': 5.0},
            {'guest_name': '李雨萱', 'location': '上海', 'avatar_url': 'images/client/testimonial2.jpg',
             'quote': '定制套餐功能太棒了，自由组合机票和酒店还打了折，曼谷之行省心又省钱。', 'rating': 5.0},
        ]
        for item in data:
            t, created = Testimonial.objects.get_or_create(guest_name=item['guest_name'], defaults=item)
            if created:
                self.stdout.write(f'  创建评价: {t.guest_name}')

    def _create_blog_posts(self):
        data = [
            {
                'title': '伊斯坦布尔自由行完全攻略：必去景点与美食推荐',
                'category': 'guide', 'author': 'TourNest',
                'excerpt': '从蓝色清真寺到博斯普鲁斯海峡，带你玩转这座横跨欧亚的迷人城市。',
                'content': '伊斯坦布尔是一座横跨欧亚大陆的历史名城。推荐游览蓝色清真寺、圣索菲亚大教堂、大巴扎等经典景点。美食方面不可错过土耳其烤肉、巴克拉瓦甜点。',
                'image_url': 'images/blog/b1.jpg', 'published_date': date(2025, 11, 15),
            },
            {
                'title': '巴黎三日游最佳路线：艺术、美食与浪漫',
                'category': 'guide', 'author': 'TourNest',
                'excerpt': '三天时间如何高效游览巴黎？这份路线规划帮你不错过任何精彩。',
                'content': '第一天：埃菲尔铁塔、塞纳河游船。第二天：卢浮宫、香榭丽舍大街。第三天：凡尔赛宫一日游。别忘了在街头咖啡馆品尝可颂和马卡龙。',
                'image_url': 'images/blog/b2.jpg', 'published_date': date(2025, 11, 15),
            },
            {
                'title': '出境旅行必备：10个省钱小技巧',
                'category': 'tips', 'author': 'TourNest',
                'excerpt': '掌握这些技巧，让你的旅行预算花得更值。',
                'content': '1. 提前预订机票和酒店。2. 使用TourNest比价功能。3. 选择定制套餐享受打包折扣。4. 购买旅游保险防患未然。5. 关注特惠活动。',
                'image_url': 'images/blog/b3.jpg', 'published_date': date(2025, 11, 15),
            },
        ]
        for item in data:
            post, created = BlogPost.objects.get_or_create(title=item['title'], defaults=item)
            if created:
                self.stdout.write(f'  创建攻略: {post.title[:20]}...')

    def _create_special_offers(self):
        data = [
            {
                'title': '暑期特惠：东南亚海岛游', 'description': '限时特惠，享受阳光沙滩与热带风情，名额有限先到先得！',
                'discount': 60, 'price': 6999, 'original_price': 10150, 'image_url': 'images/offer/offer-shape.png',
                'features': '5 天 6 晚\n2 人起订\n含往返机票\n五星酒店住宿\n赠送浮潜体验',
            },
        ]
        for item in data:
            offer, created = SpecialOffer.objects.get_or_create(title=item['title'], defaults=item)
            if created:
                self.stdout.write(f'  创建特惠: {offer.title}')
