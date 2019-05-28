# Generated by Django 2.1.8 on 2019-05-28 13:54

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_panelist_legacy_row_id'),
        ('keller', '0012_auto_20190528_0543'),
    ]

    operations = [
        migrations.CreateModel(
            name='CleanPanelist',
            fields=[
                ('id', models.IntegerField(editable=False, primary_key=True, serialize=False)),
                ('year', models.IntegerField()),
                ('season', models.IntegerField(choices=[(1, 'Summer'), (2, 'Midwinter'), (3, 'Fall'), (4, 'Spring')])),
                ('district', models.CharField(max_length=255)),
                ('convention', models.CharField(max_length=255)),
                ('session', models.IntegerField(choices=[(32, 'Chorus'), (41, 'Quartet'), (42, 'Mixed'), (43, 'Senior'), (44, 'Youth'), (45, 'Unknown'), (46, 'VLQ')])),
                ('round', models.IntegerField(choices=[(1, 'Finals'), (2, 'Semi-Finals'), (3, 'Quarter-Finals')])),
                ('category', models.IntegerField(choices=[(30, 'Music'), (40, 'Performance'), (50, 'Singing')])),
                ('num', models.IntegerField()),
                ('judge', models.CharField(max_length=255)),
                ('scores', django.contrib.postgres.fields.jsonb.JSONField()),
                ('panelist', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Panelist')),
            ],
        ),
    ]