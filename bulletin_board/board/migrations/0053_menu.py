# Generated by Django 5.1 on 2024-09-23 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0052_alter_players_age_alter_players_city_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True, verbose_name='Заголовок меню')),
                ('URL', models.CharField(max_length=100, unique=True, verbose_name='URL-адрес')),
            ],
        ),
    ]
