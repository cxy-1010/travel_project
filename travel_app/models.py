from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField('手机号', max_length=20, blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    avatar_url = models.URLField('头像地址', max_length=500, blank=True, default='')
    preferred_currency = models.CharField('偏好货币', max_length=3, blank=True, default='CNY')
    bio = models.TextField('个人简介', blank=True, default='')
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return f'{self.user.username} 的个人资料'


class TravelPackage(models.Model):
    slug = models.SlugField('Package ID', max_length=120, unique=True)
    name = models.CharField('Package name', max_length=200)
    destination = models.CharField('Destination', max_length=100, blank=True)
    price = models.CharField('Price', max_length=50)
    image_url = models.URLField('Image URL', max_length=600, blank=True)
    fallback_image = models.CharField('Fallback image', max_length=200, blank=True, default='images/packages/p1.jpg')
    duration = models.CharField('Duration', max_length=50)
    hotel = models.CharField('Hotel', max_length=120, blank=True)
    transport = models.CharField('Transport', max_length=120, blank=True)
    meal = models.CharField('Meal / experience', max_length=160, blank=True)
    highlights = models.TextField('Highlights', blank=True, default='')
    rating = models.PositiveSmallIntegerField('Rating', default=5)
    reviews = models.PositiveIntegerField('Reviews', default=0)
    is_featured = models.BooleanField('Join homepage rotation', default=True)
    is_active = models.BooleanField('Active', default=True)
    display_order = models.PositiveIntegerField('Display order', default=0)
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    updated_at = models.DateTimeField('Updated at', auto_now=True)

    class Meta:
        ordering = ['display_order', '-updated_at']

    def __str__(self):
        return self.name

    def highlight_list(self):
        return [item.strip() for item in self.highlights.splitlines() if item.strip()]

    def to_card_dict(self):
        return {
            'id': self.slug,
            'name': self.name,
            'destination': self.destination or self.name.split(' ')[0],
            'price': self.price,
            'image_url': self.image_url,
            'fallback_image': self.fallback_image or 'images/packages/p1.jpg',
            'duration': self.duration,
            'hotel': self.hotel,
            'transport': self.transport,
            'meal': self.meal,
            'rating': self.rating,
            'reviews': self.reviews,
            'highlights': self.highlight_list(),
        }


class TravelBooking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', '已预订'),
        ('cancelled', '已取消'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='travel_bookings')
    package_id = models.CharField('套餐编号', max_length=100)
    package_name = models.CharField('套餐名称', max_length=200)
    destination = models.CharField('目的地', max_length=100, blank=True)
    price = models.CharField('价格', max_length=50)
    duration = models.CharField('行程天数', max_length=50)
    hotel = models.CharField('住宿', max_length=120, blank=True)
    transport = models.CharField('交通', max_length=120, blank=True)
    meal = models.CharField('餐饮/体验', max_length=160, blank=True)
    image_url = models.URLField('套餐图片', max_length=600, blank=True)
    travelers = models.PositiveIntegerField('出行人数', default=1)
    start_date = models.DateField('出发日期', blank=True, null=True)
    contact_phone = models.CharField('联系电话', max_length=20, blank=True)
    note = models.TextField('备注', blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='confirmed')
    booked_at = models.DateTimeField('预订时间', auto_now_add=True)

    class Meta:
        ordering = ['-booked_at']

    def __str__(self):
        return f'{self.user.username} - {self.package_name}'


class EmailVerificationCode(models.Model):
    email = models.EmailField('邮箱地址', db_index=True)
    code = models.CharField('验证码', max_length=6)
    purpose = models.CharField('用途', max_length=30, default='register')
    is_used = models.BooleanField('是否已使用', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    expires_at = models.DateTimeField('过期时间')

    class Meta:
        ordering = ['-created_at']

    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def default_expires_at(cls):
        return timezone.now() + timedelta(minutes=10)

    def __str__(self):
        return f'{self.email} - {self.purpose}'
