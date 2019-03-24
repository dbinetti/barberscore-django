# Generated by Django 2.1.7 on 2019-03-22 13:27

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0064_auto_20190318_1142'),
    ]

    operations = [
        migrations.AddField(
            model_name='appearance',
            name='stats',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='competitor',
            name='stats',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]