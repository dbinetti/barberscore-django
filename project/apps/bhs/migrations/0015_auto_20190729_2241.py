# Generated by Django 2.2.3 on 2019-07-30 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bhs', '0014_auto_20190729_2238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='kind',
            field=models.IntegerField(choices=[(32, 'Chorus'), (41, 'Quartet'), (46, 'VLQ')], help_text='\n            The kind of group.\n        '),
        ),
    ]