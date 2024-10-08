# Generated by Django 5.1 on 2024-09-10 20:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0027_alter_responses_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='players',
            name='guild',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='player', to='board.category'),
            preserve_default=False,
        ),
    ]
