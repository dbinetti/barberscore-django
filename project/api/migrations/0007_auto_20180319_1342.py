# Generated by Django 2.0.3 on 2018-03-19 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20180317_1319'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='award',
            options={'ordering': ['tree_sort']},
        ),
        migrations.AddField(
            model_name='award',
            name='tree_sort',
            field=models.IntegerField(blank=True, editable=False, null=True, unique=True),
        ),
    ]