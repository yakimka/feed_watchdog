# Generated by Django 4.0.4 on 2022-05-25 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("db", "0002_remove_receiver_recipient_receiver_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="source",
            name="parser_options",
            field=models.JSONField(
                blank=True, default=dict, help_text="Parser options"
            ),
        ),
    ]