# Generated by Django 2.1.7 on 2019-03-25 05:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0085_auto_20190324_2148'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='appearance',
            unique_together={('round', 'num')},
        ),
    ]