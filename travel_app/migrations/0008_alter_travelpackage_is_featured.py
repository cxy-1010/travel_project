# 由 Django 6.0.6 于 2026-07-09 03:47 生成

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel_app', '0007_seed_travelpackage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='travelpackage',
            name='is_featured',
            field=models.BooleanField(default=True, verbose_name='Join homepage rotation'),
        ),
    ]
