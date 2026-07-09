from django.db import migrations


def repair_userprofile_schema(apps, schema_editor):
    table = 'travel_app_userprofile'
    existing_tables = schema_editor.connection.introspection.table_names()
    if table not in existing_tables:
        UserProfile = apps.get_model('travel_app', 'UserProfile')
        schema_editor.create_model(UserProfile)
        return

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f'PRAGMA table_info({table})')
        existing = {row[1] for row in cursor.fetchall()}
        if 'avatar' not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN avatar varchar(100) NULL")
        if 'updated_at' not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN updated_at datetime NULL")


class Migration(migrations.Migration):

    dependencies = [
        ('travel_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(repair_userprofile_schema, migrations.RunPython.noop),
    ]
