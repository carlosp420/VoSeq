# Generated by Django 2.2.13 on 2021-05-25 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('create_dataset', '0006_dataset_charset_block'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='task_uuid',
            field=models.TextField(blank=True, null=True),
        ),
    ]