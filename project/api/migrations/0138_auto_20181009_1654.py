# Generated by Django 2.1.2 on 2018-10-09 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0137_auto_20181009_1313'),
    ]

    operations = [
        migrations.AddField(
            model_name='complete',
            name='convention_raw',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='complete',
            name='round_raw',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='complete',
            name='session_raw',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
