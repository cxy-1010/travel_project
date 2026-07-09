import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_travel_site.settings')
django.setup()

from travel_app.models import Flight, Hotel
from django.utils import timezone
import datetime

# 清空旧数据
Flight.objects.all().delete()
Hotel.objects.all().delete()

# 灌入航班
Flight.objects.create(flight_number='CA1501', airline='中国国航', departure='北京', destination='上海', departure_time=timezone.now() + datetime.timedelta(days=1), price=850.00, rating=4.8)
Flight.objects.create(flight_number='MU5102', airline='东方航空', departure='北京', destination='上海', departure_time=timezone.now() + datetime.timedelta(days=1), price=720.00, rating=4.5)
Flight.objects.create(flight_number='CZ3101', airline='南方航空', departure='北京', destination='广州', departure_time=timezone.now() + datetime.timedelta(days=2), price=1200.00, rating=4.6)

# 灌入酒店
Hotel.objects.create(name='上海大酒店', destination='上海', price=550.00, rating=4.7, address='上海市黄浦区南京东路')
Hotel.objects.create(name='快捷假日酒店', destination='上海', price=280.00, rating=4.2, address='上海市静安区')
Hotel.objects.create(name='广州四季酒店', destination='广州', price=1500.00, rating=4.9, address='广州市天河区')

print("=== 航班与酒店模拟数据灌录成功！ ===")