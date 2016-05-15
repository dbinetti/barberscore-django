# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-15 19:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_round_num_songs'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='assistant',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='assistant',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='assistant',
            name='person',
        ),
        migrations.RemoveField(
            model_name='assistant',
            name='session',
        ),
        migrations.AlterUniqueTogether(
            name='participant',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='participant',
            name='convention',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='organization',
        ),
        migrations.DeleteModel(
            name='Assistant',
        ),
        migrations.DeleteModel(
            name='Participant',
        ),
    ]
