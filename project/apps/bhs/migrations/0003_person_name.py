# Generated by Django 2.2.3 on 2019-07-30 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bhs', '0002_remove_group_district'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='name',
            field=models.CharField(default='', help_text='\n            The common name of the person.', max_length=255),
        ),
    ]