# Generated by Django 2.1.7 on 2019-03-25 04:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0083_remove_appearance_contesting'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='outcome',
            name='advance',
        ),
        migrations.RemoveField(
            model_name='outcome',
            name='level',
        ),
        migrations.RemoveField(
            model_name='outcome',
            name='minimum',
        ),
        migrations.RemoveField(
            model_name='outcome',
            name='spots',
        ),
        migrations.RemoveField(
            model_name='outcome',
            name='threshold',
        ),
    ]
