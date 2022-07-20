# Generated by Django 4.0.4 on 2022-07-17 21:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0006_remove_source_encoding_remove_source_url"),
    ]

    operations = [
        migrations.CreateModel(
            name="Filter",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=1024)),
                ("type", models.CharField(max_length=32)),
                (
                    "options",
                    models.JSONField(
                        blank=True, default=dict, help_text="Filter options"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StreamFilter",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "filter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="db.filter",
                    ),
                ),
                (
                    "stream",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="db.stream",
                    ),
                ),
            ],
        ),
    ]
