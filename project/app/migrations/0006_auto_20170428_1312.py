# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-28 20:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20170428_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='office',
            name='kind',
            field=models.IntegerField(blank=True, choices=[('International', [(1, 'International')]), ('District', [(11, 'District'), (12, 'Noncompetitive'), (13, 'Affiliate')]), ('Division', [(21, 'Division')]), ('Group', [(31, 'Quartet'), (32, 'Chapter'), (33, 'Very Large Quartet'), (34, 'Mixed Group')])], help_text='\n            The kind of office.', null=True),
        ),
    ]
