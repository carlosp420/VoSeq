# Generated by Django 2.2.13 on 2021-05-26 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('create_dataset', '0007_dataset_task_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='progress',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
