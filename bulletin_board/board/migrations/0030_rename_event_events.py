# Generated by Django 5.1 on 2024-09-10 21:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0029_remove_event_category_event_category'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Event',
            new_name='Events',
        ),
    ]
