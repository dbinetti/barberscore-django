# Generated by Django 2.2.3 on 2019-07-28 19:10

from django.db import migrations

def forward(apps, schema_editor):
    Award = apps.get_model('bhs.award')
    Outcome = apps.get_model('rmanager.outcome')
    cs = Outcome.objects.filter(
        award_id__isnull=False,
    )

    for c in cs:
        a = Award.objects.get(id=c.award_id)
        c.award_name = a.name
        c.save()


class Migration(migrations.Migration):

    dependencies = [
        ('rmanager', '0004_outcome_award_name'),
    ]

    operations = [
        migrations.RunPython(forward)
    ]
