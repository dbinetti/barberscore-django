# Generated by Django 2.2.3 on 2019-07-24 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smanager', '0002_auto_20190723_1048'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='contests',
            field=models.ManyToManyField(blank=True, related_name='entries', to='smanager.Contest'),
        ),
    ]
