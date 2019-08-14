# Generated by Django 2.2.3 on 2019-07-30 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smanager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='district',
            field=models.IntegerField(blank=True, choices=[(110, 'BHS'), (200, 'CAR'), (205, 'CSD'), (210, 'DIX'), (215, 'EVG'), (220, 'FWD'), (225, 'ILL'), (230, 'JAD'), (235, 'LOL'), (240, 'MAD'), (345, 'NED'), (350, 'NSC'), (355, 'ONT'), (360, 'PIO'), (365, 'RMD'), (370, 'SLD'), (375, 'SUN'), (380, 'SWD')], null=True),
        ),
    ]