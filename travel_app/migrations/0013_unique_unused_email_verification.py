from django.db import migrations, models


def invalidate_duplicate_unused_codes(apps, schema_editor):
    verification_model = apps.get_model('travel_app', 'EmailVerificationCode')
    duplicate_groups = (
        verification_model.objects.filter(is_used=False)
        .values('email', 'purpose')
        .annotate(latest_id=models.Max('id'), total=models.Count('id'))
        .filter(total__gt=1)
    )

    for group in duplicate_groups.iterator():
        verification_model.objects.filter(
            email=group['email'],
            purpose=group['purpose'],
            is_used=False,
        ).exclude(pk=group['latest_id']).update(is_used=True)


class Migration(migrations.Migration):
    dependencies = [
        ('travel_app', '0012_savedroute'),
    ]

    operations = [
        migrations.RunPython(invalidate_duplicate_unused_codes, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='emailverificationcode',
            constraint=models.UniqueConstraint(
                condition=models.Q(is_used=False),
                fields=('email', 'purpose'),
                name='uniq_unused_email_purpose',
            ),
        ),
    ]
