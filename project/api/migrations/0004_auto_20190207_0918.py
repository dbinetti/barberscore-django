# Generated by Django 2.1.5 on 2019-02-07 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20190205_2217'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='officer',
            unique_together={('group', 'person', 'office')},
        ),
    ]