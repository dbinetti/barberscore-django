# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-29 18:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_auto_20171129_1028'),
    ]

    operations = [
        migrations.AddField(
            model_name='grid',
            name='start',
            field=models.DateTimeField(blank=True, help_text='\n            The actual start time.', null=True),
        ),
    ]