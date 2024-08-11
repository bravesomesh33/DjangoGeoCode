# Generated by Django 5.0.7 on 2024-08-11 07:04

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_alter_location_address_alter_location_latitude_and_more"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="location",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["formatted_address"],
                name="gin_trgm_idx",
                opclasses=["gin_trgm_ops"],
            ),
        ),
    ]
