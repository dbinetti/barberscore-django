# Generated by Django 2.1.4 on 2019-01-18 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20190114_0953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='bhs_id',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]