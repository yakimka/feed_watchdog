# Generated by Django 4.0.4 on 2022-05-28 10:52

from django.db import migrations


def move_url_to_options(apps, schema_editor):
    """
    Move the url to the fetcher_options field.
    """
    Source = apps.get_model("db", "Source")
    for source in Source.objects.all():
        source.fetcher_options = {"url": source.url, "encoding": ""}
        source.save()


class Migration(migrations.Migration):

    dependencies = [
        ("db", "0004_source_fetcher_options_source_fetcher_type"),
    ]

    operations = [
        migrations.RunPython(move_url_to_options),
    ]
