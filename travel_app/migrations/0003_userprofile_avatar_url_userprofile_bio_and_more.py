# 由 Django 6.0.6 于 2026-07-09 02:07 生成

from django.db import migrations, models


def add_legacy_profile_columns(apps, schema_editor):
    table = 'travel_app_userprofile'
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f'PRAGMA table_info({table})')
        existing = {row[1] for row in cursor.fetchall()}
        if 'avatar_url' not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN avatar_url varchar(500) DEFAULT '' NOT NULL")
        if 'bio' not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN bio TEXT DEFAULT '' NOT NULL")
        if 'preferred_currency' not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN preferred_currency varchar(3) DEFAULT 'CNY' NOT NULL")


class Migration(migrations.Migration):

    dependencies = [
        ('travel_app', '0002_repair_userprofile_schema'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='userprofile',
                    name='avatar_url',
                    field=models.URLField(blank=True, default='', max_length=500, verbose_name='头像地址'),
                ),
                migrations.AddField(
                    model_name='userprofile',
                    name='bio',
                    field=models.TextField(blank=True, default='', verbose_name='个人简介'),
                ),
                migrations.AddField(
                    model_name='userprofile',
                    name='preferred_currency',
                    field=models.CharField(blank=True, default='CNY', max_length=3, verbose_name='偏好货币'),
                ),
            ],
            database_operations=[
                migrations.RunPython(add_legacy_profile_columns, migrations.RunPython.noop),
            ],
        ),
    ]
