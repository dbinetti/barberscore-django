# Generated by Django 2.1.8 on 2019-05-26 21:41

from django.db import migrations

def forward(apps, schema_editor):
    Convention = apps.get_model('cmanager.convention')
    cs = Convention.objects.select_related('group')
    for c in cs:
        c.district = c.group.code
        c.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cmanager', '0003_convention_district'),
    ]

    operations = [
        migrations.RunPython(forward)
    ]
