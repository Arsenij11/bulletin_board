from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse


# Create your models here.
class Published(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)

class Players(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player', verbose_name='username')
    level = models.IntegerField(default=0, verbose_name='Уровень', validators=[MinValueValidator(0, message='Ошибка! Минимально допустимое значение: 0'),
                                                                                MaxValueValidator(50, message='Ошибка! Максимально допустимое значение: 50')])
    name = models.CharField(max_length=100,verbose_name='ФИО', validators=[MinLengthValidator(2, message='Ошибка! Минимально допустимое количество символов: 2'),
                                                                           MaxLengthValidator(100, message='Ошибка! Максимально допустимое количество символов: 100')])
    age = models.IntegerField(blank=True, null=True, verbose_name='Возраст', validators=[MinValueValidator(14, message='Минимально допустимый возраст игрока 14 лет'),
                                                                                         MaxValueValidator(123, message='Вам не может быть столько лет!')])
    sex = models.CharField(max_length=10, choices=[('Male', 'Мужской'),('Female', 'Женский')], verbose_name='Пол')
    city = models.CharField(max_length=100, blank=True, verbose_name='Город проживания', null=True,
                            validators=[MinLengthValidator(2, message='Ошибка! Минимально допустимое количество символов: 2'),
                                        MaxLengthValidator(100, message='Ошибка! Максимально допустимое количество символов: 100')])
    guild = models.ForeignKey(to='Category', on_delete=models.PROTECT, related_name='player', blank=True, verbose_name='Гильдия')
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0, message='Ошибка! Минимально допустимое значение: 0.0'),
                                                        MaxValueValidator(5.0, message='Ошибка! Максимально допустимое значение: 5.0')], verbose_name='Рейтинг игрока')
    registration_time = models.DateTimeField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='photo/players/%Y/%m/%d', default='photo/players/default/Аватарка по умолчанию.jpg', verbose_name='Аватарка')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('player', kwargs={'player_id' : self.pk})

    def count_of_posts(self):
        return len(self.events.all())

    def count_of_responses(self):
        return len(self.resp.all())

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    slug = models.SlugField(max_length=100, db_index=True, verbose_name='Slug категории', unique=True)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('category', kwargs={'category_slug': self.slug})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Event(models.Model):
    player = models.ForeignKey(Players, on_delete=models.CASCADE, related_name='events', verbose_name='Автор объявления')
    title = models.CharField(verbose_name='Заголовок', max_length=100,
                             validators=[MinLengthValidator(10, message='Минимально допустимое количество символов: 50!'),
                                         MaxLengthValidator(100, message='Максимально допустимое количество символов: 100!')])
    text = models.TextField(verbose_name='Содержание', validators=[MinLengthValidator(100, message='Минимально допустимое количество символов: 100!')])
    category = models.ManyToManyField(Category, related_name='events', verbose_name='Категория')
    is_published = models.BooleanField(default=False, choices=list(map(lambda x: (bool(x[0]), x[1]),[(0, 'Черновик'), (1, 'Опубликовано')])), verbose_name='Этап публикации')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    awards = models.TextField(verbose_name='Награды за событие',
                              validators=[MinLengthValidator(50, message='Минимально допустимое количество символов: 50!')])

    requirement_level = models.IntegerField(default=0, verbose_name='Рекомендуемый уровень',
                              validators=[MinValueValidator(0, message='Минимально допустимый уровень: 0!'),
                                          MaxValueValidator(50, message='Максимально допустимый уровень: 50!')])

    slug = models.SlugField(verbose_name='URL объявления',
                            validators=[MinLengthValidator(5, message='Минимально допустимое количество символов: 5!'),
                                        MaxLengthValidator(50, message='Максимально допустимое количество символов: 50!')], unique=True)
    photo = models.ImageField(upload_to='photo/%Y/%m/%d', default=None, null=True, blank=True, verbose_name='Фото контент')
    video = models.FileField(upload_to='video/%Y/%m/%d', default=None, null=True, blank=True,
                              verbose_name='Видео контент')

    objects = models.Manager()
    published = Published()


    def __str__(self):
        return self.title
    def preview(self):
        return self.text[:100] + '...'
    def get_absolute_url(self):
        return reverse('detail', kwargs={'event_slug': self.slug})


    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'


class Responses(models.Model):
    player = models.ForeignKey(Players, on_delete=models.DO_NOTHING, related_name='resp', verbose_name='Игрок')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='resp', verbose_name='Событие/объявление')
    message = models.CharField(max_length=100, verbose_name='Текст сообщения')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата отклика')

    def __str__(self):
        return self.message
    def message_preview(self):
        return self.message[:50]
    def get_absolute_url(self):
        return reverse('response', kwargs={'event_id': self.event.pk})

    class Meta:
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'
        ordering = ['time_create']

class AnswertoResponse(models.Model):
    player = models.ForeignKey(to=Players, on_delete=models.DO_NOTHING, related_name='answers', verbose_name='Игрок')
    resp = models.ForeignKey(to=Responses, on_delete=models.DO_NOTHING, related_name='answers', verbose_name='Отклик')
    message = models.CharField(max_length=100, verbose_name='Текст сообщения')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата ответа на отклик')

    def __str__(self):
        return self.message

    def get_absolute_url(self):
        return reverse('show answers to response', kwargs={'resp_id':self.resp.pk})


    class Meta:
        verbose_name = 'Ответ на отклик'
        verbose_name_plural = 'Ответы на отклик'
        ordering = ['time_create']