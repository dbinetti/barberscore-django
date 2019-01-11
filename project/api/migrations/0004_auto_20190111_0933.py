# Generated by Django 2.1.4 on 2019-01-11 17:33

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_song_penalties'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='penalties',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(choices=[(10, 'Primarily Patriotic Intent'), (20, 'Primarily Religious Intent'), (30, 'Instrumental Accompaniment'), (40, 'Chorus Exceeding 4-Part Texture'), (50, 'Sound Equipment or Electronic Enhancement')]), blank=True, default=list, size=None),
        ),
    ]
