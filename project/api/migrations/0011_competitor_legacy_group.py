# Generated by Django 2.1.5 on 2019-02-11 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20190211_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='competitor',
            name='legacy_group',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
