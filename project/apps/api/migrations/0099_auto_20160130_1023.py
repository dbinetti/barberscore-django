# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-30 18:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0098_auto_20160129_2212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='score',
            name='dixon_test',
            field=models.BooleanField(default=False),
        ),
    ]
