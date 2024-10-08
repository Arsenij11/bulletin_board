# Generated by Django 5.1 on 2024-09-09 20:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0015_alter_author_age'),
    ]

    operations = [
        migrations.AlterField(
            model_name='responses',
            name='ad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='resp', to='board.post'),
        ),
        migrations.AlterField(
            model_name='responses',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='resp', to='board.author'),
        ),
    ]
