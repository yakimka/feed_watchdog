# Generated by Django 4.0.4 on 2022-05-28 10:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0005_move_url_to_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='source',
            name='encoding',
        ),
        migrations.RemoveField(
            model_name='source',
            name='url',
        ),
    ]
