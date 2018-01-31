# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-29 04:24
from __future__ import unicode_literals

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0040_auto_20180128_2021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competitor',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(-10, 'Missed'), (0, 'New'), (10, 'Made')], default=0, help_text='DO NOT CHANGE MANUALLY unless correcting a mistake.  Use the buttons to change state.'),
        ),
    ]