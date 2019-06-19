# Generated by Django 2.1.8 on 2019-06-06 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_auto_20190605_0718'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='target',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feeders', to='api.Session'),
        ),
    ]