# Generated by Django 5.1 on 2024-09-23 13:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0048_alter_players_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='players',
            name='rating',
            field=models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0, message='Ошибка! Минимально допустимое значение: 0.0'), django.core.validators.MaxValueValidator(5.0, message='Ошибка! Минимально допустимое значение: 5.0')], verbose_name='Рейтинг игрока'),
        ),
    ]
