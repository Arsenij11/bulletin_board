from django.apps import AppConfig


class BoardConfig(AppConfig):
    verbose_name = 'Доска объявлений (событий) для игроков Mmorpg'
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'board'
