# Generated by Django 5.1 on 2024-09-09 19:22

import django.db.models.manager
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0010_ad_is_published'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='ad',
            managers=[
                ('published', django.db.models.manager.Manager()),
            ],
        ),
        migrations.RemoveField(
            model_name='author',
            name='surname',
        ),
    ]
