from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Flight(models.Model):
    """航班"""
    flight_no = models.CharField('航班号', max_length=20, unique=True)
    departure_city = models.CharField('出发城市', max_length=50)
    arrival_city = models.CharField('到达城市', max_length=50)
    departure_time = models.DateTimeField('出发时间')
    arrival_time = models.DateTimeField('到达时间')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '航班'
        verbose_name_plural = '航班管理'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.flight_no} {self.departure_city}→{self.arrival_city}'


class FlightPrice(models.Model):
    """航班价格 - 同一航班不同供应商/舱位"""
    CLASS_CHOICES = [
        ('economy', '经济舱'),
        ('business', '商务舱'),
        ('first', '头等舱'),
    ]
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='prices', verbose_name='所属航班')
    supplier = models.CharField('供应商', max_length=50)
    cabin_class = models.CharField('舱位', max_length=20, choices=CLASS_CHOICES, default='economy')
    price = models.DecimalField('单价', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = '航班价格'
        verbose_name_plural = '航班价格管理'

    def __str__(self):
        return f'{self.flight.flight_no} - {self.get_cabin_class_display()} - ¥{self.price}'


class Hotel(models.Model):
    """酒店"""
    name = models.CharField('酒店名称', max_length=100)
    city = models.CharField('城市', max_length=50)
    stars = models.IntegerField('星级', default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.TextField('描述', blank=True)
    image = models.CharField('图片路径', max_length=200, blank=True, help_text='示例: images/packages/p1.jpg')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '酒店'
        verbose_name_plural = '酒店管理'

    def __str__(self):
        return f'{self.name}（{"★" * self.stars}）'


class HotelRoom(models.Model):
    """酒店房型"""
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms', verbose_name='所属酒店')
    room_type = models.CharField('房型', max_length=50)
    price_per_night = models.DecimalField('每晚价格', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = '房型'
        verbose_name_plural = '房型管理'

    def __str__(self):
        return f'{self.hotel.name} - {self.room_type} ¥{self.price_per_night}'


class Package(models.Model):
    """旅游套餐"""
    name = models.CharField('套餐名称', max_length=100)
    destination = models.CharField('目的地', max_length=200)
    itinerary = models.TextField('行程安排', blank=True)
    original_price = models.DecimalField('原价', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField('优惠价', max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    duration = models.CharField('行程天数', max_length=50, default='5天4晚')
    image = models.CharField('配图路径', max_length=200, blank=True, default='images/packages/p1.jpg')
    rating = models.DecimalField('评分', max_digits=2, decimal_places=1, default=4.5, validators=[MinValueValidator(0), MaxValueValidator(5)])
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '旅游套餐'
        verbose_name_plural = '旅游套餐管理'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name}'

    @property
    def current_price(self):
        """当前价格 = 有优惠价用优惠价，否则用原价"""
        return float(self.discount_price) if self.discount_price else float(self.original_price)

    @property
    def has_discount(self):
        return self.discount_price is not None and self.discount_price < self.original_price


class PackageExtra(models.Model):
    """套餐增值服务"""
    package = models.ForeignKey('Package', on_delete=models.CASCADE, related_name='extras', verbose_name='所属套餐')
    name = models.CharField('服务名称', max_length=50)
    price = models.DecimalField('价格', max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = '增值服务'
        verbose_name_plural = '增值服务管理'

    def __str__(self):
        return f'{self.name} +¥{self.price}'


class Booking(models.Model):
    """预订记录"""
    STATUS_CHOICES = [
        ('pending', '待确认'),
        ('confirmed', '已确认'),
        ('cancelled', '已取消'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name='用户')
    package = models.ForeignKey('Package', on_delete=models.CASCADE, related_name='bookings', verbose_name='套餐')
    num_people = models.IntegerField('出行人数', default=1, validators=[MinValueValidator(1)])
    total_price = models.DecimalField('总价', max_digits=10, decimal_places=2, blank=True, null=True)
    contact_name = models.CharField('联系人', max_length=100)
    contact_phone = models.CharField('联系电话', max_length=20)
    travel_date = models.DateField('出行日期')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '预订记录'
        verbose_name_plural = '预订记录管理'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.package.name}'


class Guide(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guides')
    title = models.CharField(max_length=200)
    destination = models.CharField(max_length=100)
    content = models.TextField()
    image_url = models.URLField(blank=True)
    likes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class GuideComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


