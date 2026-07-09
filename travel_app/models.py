from django.db import models
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
