# 由 Django 6.0.6 于 2026-07-10 02:31 生成

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel_app', '0011_flight_hotel_travelnews_guide_guidecomment_order_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='路线标题')),
                ('country', models.CharField(blank=True, max_length=100, verbose_name='国家/地区')),
                ('city', models.CharField(blank=True, max_length=100, verbose_name='城市')),
                ('destination', models.CharField(blank=True, max_length=120, verbose_name='目的地')),
                ('check_in', models.DateField(blank=True, null=True, verbose_name='出发日期')),
                ('check_out', models.DateField(blank=True, null=True, verbose_name='返回日期')),
                ('days', models.PositiveIntegerField(blank=True, null=True, verbose_name='行程天数')),
                ('people', models.PositiveIntegerField(blank=True, null=True, verbose_name='出行人数')),
                ('budget', models.CharField(blank=True, max_length=80, verbose_name='预算')),
                ('content', models.TextField(blank=True, verbose_name='路线内容')),
                ('selected_item', models.JSONField(blank=True, null=True, verbose_name='加入行程项目')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='保存时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_routes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
    ]
