# Generated by Django 2.2.13 on 2020-11-25 01:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('create_dataset', '0004_auto_20201101_1848'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='sister_dataset_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
