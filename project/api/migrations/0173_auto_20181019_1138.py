# Generated by Django 2.1.2 on 2018-10-19 18:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0172_auto_20181019_0907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complete',
            name='panelist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Panelist', unique=True),
        ),
    ]
