# Generated by Django 5.1 on 2024-09-17 15:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0044_alter_post_slug'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Post',
            new_name='Event',
        ),
    ]
