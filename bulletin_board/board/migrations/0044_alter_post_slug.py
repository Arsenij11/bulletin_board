# Generated by Django 5.1 on 2024-09-17 15:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0043_alter_post_awards'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(unique=True, validators=[django.core.validators.MinLengthValidator(5, message='Минимально допустимое количество символов: 5!'), django.core.validators.MaxLengthValidator(50, message='Максимально допустимое количество символов: 50!')], verbose_name='slug объявления'),
        ),
    ]
