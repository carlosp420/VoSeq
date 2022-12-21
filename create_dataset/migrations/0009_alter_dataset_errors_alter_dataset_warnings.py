# Generated by Django 4.1.3 on 2022-11-20 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('create_dataset', '0008_dataset_progress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='errors',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='warnings',
            field=models.JSONField(blank=True, null=True),
        ),
    ]