# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-13 19:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0032_session_actives_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='description',
            field=models.TextField(blank=True, help_text='\n            The Public Description.  Will be sent in all email communications.', max_length=1000),
        ),
        migrations.AddField(
            model_name='session',
            name='notes',
            field=models.TextField(blank=True, help_text='\n            Private Notes (for internal use only).  Will not be sent.'),
        ),
    ]