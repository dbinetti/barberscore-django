# Generated by Django 2.1.7 on 2019-03-15 21:36

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('mem', '0007_auto_20190315_1313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='cell_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128),
        ),
        migrations.AlterField(
            model_name='person',
            name='first_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='person',
            name='home_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128),
        ),
        migrations.AlterField(
            model_name='person',
            name='last_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='person',
            name='middle_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='person',
            name='nick_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='person',
            name='prefix',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='person',
            name='suffix',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='person',
            name='work_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128),
        ),
    ]