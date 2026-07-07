from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Destination(models.Model):
    """目的地/景点"""
    name = models.CharField('名称', max_length=100)
    name_en = models.CharField('英文名称', max_length=100, blank=True)
    country = models.CharField('国家', max_length=100)
    city = models.CharField('城市', max_length=100, blank=True)
    description = models.TextField('描述', blank=True)
    image = models.ImageField('图片', upload_to='destinations/', blank=True)
    image_url = models.CharField('图片URL', max_length=500, blank=True,
                                 help_text='静态图片路径，如 images/gallery/g1.jpg')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    is_active = models.BooleanField('是否启用', default=True)

    class Meta:
        verbose_name = '目的地'
        verbose_name_plural = '目的地'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.country})'


class TourPackage(models.Model):
    """旅游套餐"""
    name = models.CharField('套餐名称', max_length=200)
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='目的地')
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    original_price = models.DecimalField('原价', max_digits=10, decimal_places=2, null=True, blank=True)
    duration_days = models.IntegerField('天数', default=5)
    duration_nights = models.IntegerField('晚数', default=6)
    rating = models.DecimalField('评分', max_digits=3, decimal_places=1, default=5.0,
                                 validators=[MinValueValidator(0), MaxValueValidator(5)])
    review_count = models.IntegerField('评价数', default=0)
    image_url = models.CharField('图片URL', max_length=500, blank=True,
                                 help_text='如 images/packages/p1.jpg')
    features = models.TextField('特色', blank=True, help_text='每行一条特色')
    is_recommended = models.BooleanField('推荐', default=False)
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '旅游套餐'
        verbose_name_plural = '旅游套餐'
        ordering = ['-is_recommended', 'name']

    def __str__(self):
        return self.name

    def feature_list(self):
        return [f.strip() for f in self.features.split('\n') if f.strip()]


class Hotel(models.Model):
    """酒店"""
    name = models.CharField('酒店名称', max_length=200)
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='所在目的地')
    city = models.CharField('城市', max_length=100)
    address = models.CharField('地址', max_length=500, blank=True)
    stars = models.IntegerField('星级', default=5, validators=[MinValueValidator(1), MaxValueValidator(7)])
    price_per_night = models.DecimalField('每晚价格', max_digits=10, decimal_places=2)
    rating = models.DecimalField('评分', max_digits=3, decimal_places=1, default=4.5,
                                 validators=[MinValueValidator(0), MaxValueValidator(5)])
    review_count = models.IntegerField('评价数', default=0)
    image_url = models.CharField('图片URL', max_length=500, blank=True)
    description = models.TextField('描述', blank=True)
    amenities = models.TextField('设施服务', blank=True, help_text='每行一项')
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '酒店'
        verbose_name_plural = '酒店'

    def __str__(self):
        return self.name

    def amenity_list(self):
        return [a.strip() for a in self.amenities.split('\n') if a.strip()]


class RoomType(models.Model):
    """酒店房型"""
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_types',
                              verbose_name='酒店')
    name = models.CharField('房型名称', max_length=100)
    price_per_night = models.DecimalField('每晚价格', max_digits=10, decimal_places=2)
    capacity = models.IntegerField('可住人数', default=2)
    available_rooms = models.IntegerField('可用房间数', default=10)
    description = models.CharField('描述', max_length=300, blank=True)
    is_active = models.BooleanField('启用', default=True)

    class Meta:
        verbose_name = '房型'
        verbose_name_plural = '房型'

    def __str__(self):
        return f'{self.hotel.name} - {self.name}'


class Flight(models.Model):
    """航班"""
    FLIGHT_TYPE_CHOICES = [
        ('one_way', '单程'),
        ('round_trip', '往返'),
    ]

    airline = models.CharField('航空公司', max_length=100)
    flight_number = models.CharField('航班号', max_length=20, blank=True)
    origin_city = models.CharField('出发城市', max_length=100)
    destination_city = models.CharField('到达城市', max_length=100)
    departure_time = models.DateTimeField('出发时间')
    arrival_time = models.DateTimeField('到达时间')
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    flight_type = models.CharField('航班类型', max_length=20, choices=FLIGHT_TYPE_CHOICES, default='one_way')
    seats_available = models.IntegerField('余票', default=100)
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '航班'
        verbose_name_plural = '航班'
        ordering = ['departure_time']

    def __str__(self):
        return f'{self.airline} {self.flight_number}: {self.origin_city} -> {self.destination_city}'


class SeatClass(models.Model):
    """航班舱位"""
    SEAT_CHOICES = [
        ('economy', '经济舱'),
        ('premium', '超级经济舱'),
        ('business', '商务舱'),
        ('first', '头等舱'),
    ]

    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='seat_classes',
                               verbose_name='航班')
    class_type = models.CharField('舱位类型', max_length=20, choices=SEAT_CHOICES, default='economy')
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    available_seats = models.IntegerField('可用座位', default=50)

    class Meta:
        verbose_name = '舱位'
        verbose_name_plural = '舱位'
        unique_together = ['flight', 'class_type']

    def __str__(self):
        return f'{self.flight} - {self.get_class_type_display()}'


class ExtraService(models.Model):
    """额外服务（保险、接机等）"""
    SERVICE_TYPE_CHOICES = [
        ('insurance', '旅游保险'),
        ('pickup', '接机服务'),
        ('luggage', '行李托运'),
        ('visa', '签证代办'),
        ('guide', '私人导游'),
    ]

    name = models.CharField('服务名称', max_length=100)
    service_type = models.CharField('服务类型', max_length=20, choices=SERVICE_TYPE_CHOICES)
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    description = models.TextField('描述', blank=True)
    is_active = models.BooleanField('启用', default=True)

    class Meta:
        verbose_name = '额外服务'
        verbose_name_plural = '额外服务'

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    """用户评价展示"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='用户')
    guest_name = models.CharField('游客姓名', max_length=100)
    location = models.CharField('所在地', max_length=200, blank=True)
    avatar_url = models.CharField('头像URL', max_length=500, blank=True)
    quote = models.TextField('评价内容')
    rating = models.DecimalField('评分', max_digits=3, decimal_places=1, default=5.0,
                                 validators=[MinValueValidator(0), MaxValueValidator(5)])
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '用户评价'
        verbose_name_plural = '用户评价'

    def __str__(self):
        return f'{self.guest_name} 的评价'


class BlogPost(models.Model):
    """博客文章/攻略"""
    CATEGORY_CHOICES = [
        ('guide', '攻略'),
        ('news', '资讯'),
        ('story', '游记'),
        ('tips', '小贴士'),
    ]

    title = models.CharField('标题', max_length=200)
    category = models.CharField('分类', max_length=20, choices=CATEGORY_CHOICES, default='guide')
    author = models.CharField('作者', max_length=100, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='相关目的地')
    excerpt = models.TextField('摘要', blank=True)
    content = models.TextField('内容', blank=True)
    image_url = models.CharField('封面URL', max_length=500, blank=True)
    published_date = models.DateField('发布日期', default=timezone.now)
    is_published = models.BooleanField('发布', default=True)
    view_count = models.IntegerField('浏览量', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '博客文章'
        verbose_name_plural = '博客文章'
        ordering = ['-published_date']

    def __str__(self):
        return self.title


class UserReview(models.Model):
    """用户旅行评价与晒图"""
    REVIEW_TYPE_CHOICES = [
        ('package', '套餐'),
        ('hotel', '酒店'),
        ('flight', '航班'),
        ('destination', '目的地'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    review_type = models.CharField('评价类型', max_length=20, choices=REVIEW_TYPE_CHOICES)
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, null=True, blank=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, null=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField('评分', validators=[MinValueValidator(1), MaxValueValidator(5)], default=5)
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    image_url = models.CharField('晒图URL', max_length=500, blank=True)
    image = models.ImageField('晒图', upload_to='reviews/', blank=True)
    is_approved = models.BooleanField('已审核', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '用户评价'
        verbose_name_plural = '用户评价'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.title}'


class Favorite(models.Model):
    """收藏"""
    FAVORITE_TYPE_CHOICES = [
        ('package', '套餐'),
        ('hotel', '酒店'),
        ('flight', '航班'),
        ('blog', '攻略'),
        ('destination', '目的地'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    favorite_type = models.CharField('收藏类型', max_length=20, choices=FAVORITE_TYPE_CHOICES)
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, null=True, blank=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, null=True, blank=True)
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, null=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField('收藏时间', auto_now_add=True)

    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} 收藏'


class SpecialOffer(models.Model):
    """特惠活动"""
    title = models.CharField('活动标题', max_length=200)
    subtitle = models.CharField('副标题', max_length=200, blank=True)
    description = models.TextField('描述', blank=True)
    discount = models.IntegerField('折扣百分比', help_text='如 60 表示6折', default=60)
    price = models.DecimalField('现价', max_digits=10, decimal_places=2)
    original_price = models.DecimalField('原价', max_digits=10, decimal_places=2)
    image_url = models.CharField('图片URL', max_length=500, blank=True)
    features = models.TextField('特色', blank=True)
    is_active = models.BooleanField('启用', default=True)
    start_date = models.DateField('开始日期', null=True, blank=True)
    end_date = models.DateField('结束日期', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '特惠活动'
        verbose_name_plural = '特惠活动'

    def __str__(self):
        return self.title

    def feature_list(self):
        return [f.strip() for f in self.features.split('\n') if f.strip()]


class Subscriber(models.Model):
    """邮件订阅"""
    email = models.EmailField('邮箱', unique=True)
    is_active = models.BooleanField('启用', default=True)
    subscribed_at = models.DateTimeField('订阅时间', auto_now_add=True)

    class Meta:
        verbose_name = '邮件订阅'
        verbose_name_plural = '邮件订阅'
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """用户扩展资料"""
    CURRENCY_CHOICES = [
        ('CNY', '人民币 ¥'),
        ('USD', '美元 $'),
        ('EUR', '欧元 €'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='用户')
    phone = models.CharField('手机号', max_length=20, blank=True)
    avatar_url = models.CharField('头像URL', max_length=500, blank=True)
    preferred_currency = models.CharField('偏好货币', max_length=3, choices=CURRENCY_CHOICES, default='CNY')
    bio = models.TextField('个人简介', blank=True)

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'

    def __str__(self):
        return f'{self.user.username} 的资料'


class Booking(models.Model):
    """预订订单"""
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('confirmed', '已确认'),
        ('cancelled', '已取消'),
        ('completed', '已完成'),
    ]

    BOOKING_TYPE_CHOICES = [
        ('package', '旅游套餐'),
        ('hotel', '酒店'),
        ('flight', '航班'),
        ('custom', '定制套餐'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    booking_type = models.CharField('预订类型', max_length=20, choices=BOOKING_TYPE_CHOICES)
    package = models.ForeignKey(TourPackage, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='套餐')
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='酒店')
    flight = models.ForeignKey(Flight, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='航班')
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='房型')
    seat_class = models.ForeignKey(SeatClass, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='舱位')
    extra_services = models.ManyToManyField(ExtraService, blank=True, verbose_name='额外服务')
    total_price = models.DecimalField('总价', max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField('优惠金额', max_digits=10, decimal_places=2, default=0)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    guest_count = models.IntegerField('人数', default=1)
    check_in = models.DateField('入住/出发日期', null=True, blank=True)
    check_out = models.DateField('退房/返回日期', null=True, blank=True)
    note = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '预订订单'
        verbose_name_plural = '预订订单'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_booking_type_display()} - {self.user.username} - {self.created_at.strftime("%Y-%m-%d")}'

    def get_item_name(self):
        if self.booking_type == 'package' and self.package:
            return self.package.name
        if self.booking_type == 'hotel' and self.hotel:
            return self.hotel.name
        if self.booking_type == 'flight' and self.flight:
            return f'{self.flight.airline} {self.flight.flight_number}'
        if self.booking_type == 'custom':
            parts = []
            if self.flight:
                parts.append(f'机票:{self.flight.destination_city}')
            if self.hotel:
                parts.append(f'酒店:{self.hotel.name}')
            return ' + '.join(parts) if parts else '定制套餐'
        return '未知'
