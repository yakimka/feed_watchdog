# Generated by Django 4.0.4 on 2022-07-24 16:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0009_interval_updated"),
    ]

    operations = [
        migrations.AddField(
            model_name="stream",
            name="squash",
            field=models.BooleanField(
                default=False, help_text="Squash posts in one message"
            ),
        ),
    ]
