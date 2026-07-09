from django.db import models
from django.contrib.auth.models import User

# === 航班模型 ===
class Flight(models.Model):
    flight_number = models.CharField(max_length=20, verbose_name="航班号")
    airline = models.CharField(max_length=50, verbose_name="航空公司")
    departure = models.CharField(max_length=50, verbose_name="出发地")
    destination = models.CharField(max_length=50, verbose_name="目的地")
    departure_time = models.DateTimeField(verbose_name="出发时间")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    rating = models.FloatField(default=5.0, verbose_name="评分")

    def __str__(self):
        return f"{self.flight_number} ({self.departure} -> {self.destination})"

# === 酒店模型 ===
class Hotel(models.Model):
    name = models.CharField(max_length=100, verbose_name="酒店名称")
    destination = models.CharField(max_length=50, verbose_name="所在城市")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="每晚价格")
    rating = models.FloatField(default=5.0, verbose_name="评分")
    address = models.CharField(max_length=200, verbose_name="详细地址")

    def __str__(self):
        return self.name

# === 订单模型 ===
class Order(models.Model):
    ORDER_TYPES = (('flight', '航班'), ('hotel', '酒店'))
    STATUS_CHOICES = (('pending', '待支付'), ('paid', '已支付'), ('cancelled', '已取消'))
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    item_type = models.CharField(max_length=10, choices=ORDER_TYPES, verbose_name="订单类型")
    item_id = models.IntegerField(verbose_name="商品ID")
    item_name = models.CharField(max_length=100, verbose_name="商品名称")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="订单金额")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="订单状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

# === 攻略模型 ===
class Guide(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="作者")
    title = models.CharField(max_length=200, verbose_name="标题")
    destination = models.CharField(max_length=100, verbose_name="目的地")
    content = models.TextField(verbose_name="正文")
    image_url = models.CharField(max_length=500, blank=True, null=True, verbose_name="图片URL")
    likes = models.IntegerField(default=0, verbose_name="点赞数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

# 专门用来存储旅客评论/攻略互动的数据库表
class GuideComment(models.Model):
    guide = models.ForeignKey(
        Guide,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        null=True,
        verbose_name="所属攻略"
    )
    title = models.CharField(max_length=100, verbose_name="标题")
    destination = models.CharField(max_length=50, verbose_name="目的地")
    content = models.TextField(verbose_name="评论正文")
    bg_color = models.CharField(max_length=20, default="#007BFF", verbose_name="徽章背景色")
    text_color = models.CharField(max_length=20, default="#FFFFFF", verbose_name="徽章文字色")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="发布者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class GuideFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="收藏用户")
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='favorites', verbose_name="收藏攻略")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="收藏时间")

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'guide')

    def __str__(self):
        return f"{self.user.username} 收藏 {self.guide.title}"
    
class TravelNews(models.Model):
    NEWS_TYPES = (
        ('news', '实时新闻'),
        ('guide', '精选攻略'),
    )
    
    title = models.CharField(max_length=200, verbose_name="新闻/攻略标题")
    category = models.CharField(max_length=10, choices=NEWS_TYPES, default='news', verbose_name="分类")
    summary = models.CharField(max_length=500, verbose_name="摘要（一句话简介）")
    content = models.TextField(verbose_name="详细正文（支持富文本/长文）")
    cover_url = models.URLField(max_length=500, default="https://images.unsplash.com/photo-1507525428034-b723cf961d3e", verbose_name="封面图链接")
    views_count = models.PositiveIntegerField(default=0, verbose_name="浏览量")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")

    class Meta:
        ordering = ['-created_at'] # 默认按最新发布时间倒序排列

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"
