# Generated by Django 2.1.8 on 2019-05-26 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmanager', '0004_auto_20190526_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='convention',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
