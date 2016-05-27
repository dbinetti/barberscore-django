# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-26 17:57
from __future__ import unicode_literals

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_auto_20160526_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='performance',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, b'New'), (5, b'Validated'), (10, b'Started'), (20, b'Finished')], default=0),
        ),
    ]
