# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-16 13:30
from __future__ import unicode_literals

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0121_auto_20170816_0624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(0, 'New'), (5, 'Invited'), (7, 'Withdrawn'), (10, 'Submitted'), (20, 'Approved'), (30, 'Rejected'), (50, 'Verified'), (52, 'Scratched'), (55, 'Disqualified'), (57, 'Started'), (60, 'Finished'), (70, 'Completed'), (90, 'Announced'), (95, 'Archived')], default=0),
        ),
    ]
