# Generated by Django 2.1.7 on 2019-03-25 04:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0084_auto_20190324_2142'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='contender',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='contender',
            name='appearance',
        ),
        migrations.RemoveField(
            model_name='contender',
            name='outcome',
        ),
        migrations.DeleteModel(
            name='Contender',
        ),
    ]
