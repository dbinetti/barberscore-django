# Generated by Django 2.1.7 on 2019-04-04 16:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0114_auto_20190402_0925'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='contact_report',
        ),
    ]