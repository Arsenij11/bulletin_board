# Generated by Django 5.1 on 2024-09-17 06:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0038_players_registration_time'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Event',
            new_name='Post',
        ),
    ]
