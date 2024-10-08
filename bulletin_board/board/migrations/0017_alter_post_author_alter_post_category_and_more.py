# Generated by Django 5.1 on 2024-09-09 20:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0016_alter_responses_ad_alter_responses_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ad', to='board.author'),
        ),
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ads', to='board.category'),
        ),
        migrations.AlterField(
            model_name='responses',
            name='ad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resp', to='board.post'),
        ),
        migrations.AlterField(
            model_name='responses',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resp', to='board.author'),
        ),
    ]
