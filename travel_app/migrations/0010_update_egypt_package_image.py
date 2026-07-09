from django.db import migrations


def update_egypt_package_image(apps, schema_editor):
    TravelPackage = apps.get_model('travel_app', 'TravelPackage')
    TravelPackage.objects.filter(slug='egypt-cairo-nile').update(
        image_url='images/packages/egypt-cairo-nile.jpg',
        fallback_image='images/packages/egypt-cairo-nile.jpg',
    )


def restore_egypt_package_image(apps, schema_editor):
    TravelPackage = apps.get_model('travel_app', 'TravelPackage')
    TravelPackage.objects.filter(slug='egypt-cairo-nile').update(
        image_url='https://images.unsplash.com/photo-1503177119275-0aa32b3a936c?auto=format&fit=crop&w=900&q=80',
        fallback_image='images/packages/p3.jpg',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('travel_app', '0009_seed_more_travelpackage'),
    ]

    operations = [
        migrations.RunPython(update_egypt_package_image, restore_egypt_package_image),
    ]
