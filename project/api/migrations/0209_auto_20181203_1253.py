# Generated by Django 2.1.4 on 2018-12-03 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0208_auto_20181203_1237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='mc_pk',
            field=models.CharField(blank=True, db_index=True, max_length=36, null=True),
        ),
    ]