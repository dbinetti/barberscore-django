# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-20 17:31
from __future__ import unicode_literals

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_venue_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chart',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, b'New'), (10, b'Active')], default=0),
        ),
    ]
