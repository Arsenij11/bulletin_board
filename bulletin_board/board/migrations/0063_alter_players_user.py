# Generated by Django 5.1 on 2024-10-02 08:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0062_responses_is_taken_alter_players_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='players',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='player', to=settings.AUTH_USER_MODEL, verbose_name='username'),
        ),
    ]
