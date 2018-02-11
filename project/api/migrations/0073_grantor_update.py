# Generated by Django 2.0.2 on 2018-02-11 20:03

from django.db import migrations

import logging
log = logging.getLogger('importer')


def data_migration(apps, schema_editor):
    Grantor = apps.get_model('api', 'Grantor')
    Group = apps.get_model('api', 'Group')
    grantors = Grantor.objects.all()
    for grantor in grantors:
        try:
            grantor.group = grantor.organization.groups.get(status__gt=0)
        except Group.DoesNotExist:
            grantor.group = None
        except Group.MultipleObjectsReturned:
            grantor.group = None
        grantor.save()
    return


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0072_convention_update'),
    ]

    operations = [
        migrations.RunPython(data_migration),
    ]
