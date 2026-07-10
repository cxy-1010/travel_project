# 由 Django 6.0.6 于 2026-07-09 09:20 生成

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel_app', '0010_update_egypt_package_image'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight_number', models.CharField(max_length=20, verbose_name='航班号')),
                ('airline', models.CharField(max_length=50, verbose_name='航空公司')),
                ('departure', models.CharField(max_length=50, verbose_name='出发地')),
                ('destination', models.CharField(max_length=50, verbose_name='目的地')),
                ('departure_time', models.DateTimeField(verbose_name='出发时间')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='价格')),
                ('rating', models.FloatField(default=5.0, verbose_name='评分')),
            ],
        ),
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='酒店名称')),
                ('destination', models.CharField(max_length=50, verbose_name='所在城市')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='每晚价格')),
                ('rating', models.FloatField(default=5.0, verbose_name='评分')),
                ('address', models.CharField(max_length=200, verbose_name='详细地址')),
            ],
        ),
        migrations.CreateModel(
            name='TravelNews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='新闻/攻略标题')),
                ('category', models.CharField(choices=[('news', '实时新闻'), ('guide', '精选攻略')], default='news', max_length=10, verbose_name='分类')),
                ('summary', models.CharField(max_length=500, verbose_name='摘要（一句话简介）')),
                ('content', models.TextField(verbose_name='详细正文（支持富文本/长文）')),
                ('cover_url', models.URLField(default='https://images.unsplash.com/photo-1507525428034-b723cf961d3e', max_length=500, verbose_name='封面图链接')),
                ('views_count', models.PositiveIntegerField(default=0, verbose_name='浏览量')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='发布时间')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Guide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='标题')),
                ('destination', models.CharField(max_length=100, verbose_name='目的地')),
                ('content', models.TextField(verbose_name='正文')),
                ('image_url', models.CharField(blank=True, max_length=500, null=True, verbose_name='图片URL')),
                ('likes', models.IntegerField(default=0, verbose_name='点赞数')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='发布时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='作者')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='GuideComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='标题')),
                ('destination', models.CharField(max_length=50, verbose_name='目的地')),
                ('content', models.TextField(verbose_name='评论正文')),
                ('bg_color', models.CharField(default='#007BFF', max_length=20, verbose_name='徽章背景色')),
                ('text_color', models.CharField(default='#FFFFFF', max_length=20, verbose_name='徽章文字色')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='发布时间')),
                ('guide', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='travel_app.guide', verbose_name='所属攻略')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='发布者')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_type', models.CharField(choices=[('flight', '航班'), ('hotel', '酒店')], max_length=10, verbose_name='订单类型')),
                ('item_id', models.IntegerField(verbose_name='商品ID')),
                ('item_name', models.CharField(max_length=100, verbose_name='商品名称')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='订单金额')),
                ('status', models.CharField(choices=[('pending', '待支付'), ('paid', '已支付'), ('cancelled', '已取消')], default='pending', max_length=10, verbose_name='订单状态')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
        ),
        migrations.CreateModel(
            name='GuideFavorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')),
                ('guide', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='travel_app.guide', verbose_name='收藏攻略')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='收藏用户')),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('user', 'guide')},
            },
        ),
    ]
