# Generated by Django 2.0.7 on 2018-08-20 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0087_auto_20180820_0848'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='mc_pk',
            field=models.CharField(blank=True, db_index=True, max_length=36, null=True, unique=True),
        ),
    ]