# Generated by Django 4.2.19 on 2025-04-03 18:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cleaner', '0005_detectedissue_column_data_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detectedissue',
            name='column_data_type',
        ),
    ]
