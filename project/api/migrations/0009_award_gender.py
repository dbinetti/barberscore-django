# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-27 17:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20171127_0832'),
    ]

    operations = [
        migrations.AddField(
            model_name='award',
            name='gender',
            field=models.IntegerField(choices=[(10, 'Male'), (20, 'Female'), (30, 'Mixed')], default=10, help_text='\n            The gender of session.\n        '),
        ),
    ]