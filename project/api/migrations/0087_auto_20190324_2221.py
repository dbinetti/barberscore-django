# Generated by Django 2.1.7 on 2019-03-25 05:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0086_auto_20190324_2220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appearance',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appearances', to='api.Group'),
        ),
    ]