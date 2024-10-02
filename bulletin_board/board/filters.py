from django import forms
import django_filters
from django.contrib.auth.models import User

from .models import Event, Players, Category, Responses


class EventFilter(django_filters.FilterSet):
   added_before = django_filters.DateTimeFilter(field_name='time_create',lookup_expr='lte',
                                               widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M',attrs={'type': 'datetime-local'},),
                                               label='Дата публикации до:')

   title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label='Заголовок')
   text = django_filters.CharFilter(field_name='text', lookup_expr='icontains', label='Содержание')
   awards = django_filters.CharFilter(field_name='awards', lookup_expr='icontains', label='Награды')
   requirement_level = django_filters.NumberFilter(field_name='requirement_level', lookup_expr='gte', label='Рекомендуемый уровень от')
   class Meta:
       model = Event
       fields = {
           'category' : ['exact']
       }

class AuthorFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Имя')
    guild = django_filters.ModelChoiceFilter(field_name='guild',queryset=Category.objects.all(), label='Гильдия', empty_label='Гильдия не указана')
    level = django_filters.NumberFilter(field_name='level', lookup_expr='lte', label='Уровень до')
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains', label='Город')
    rating = django_filters.NumberFilter(field_name='rating', lookup_expr='lte', label='Рейтинг до')
    class Meta:
        model = Players
        fields = {
            'age' : ['lte'],
            'sex' : ['exact']
        }

class ResponseFilter(django_filters.FilterSet):
    added_before = django_filters.DateTimeFilter(field_name='time_create', lookup_expr='lte',
                                                 widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                                                            attrs={'type': 'datetime-local'}, ),
                                                 label='Дата публикации до:')
    event = django_filters.ModelChoiceFilter(field_name='event', queryset=Event.objects.all(),
                                                     label='Объявление', empty_label='Объявление не выбрано')
    class Meta:
        model = Responses
        fields = {
            'message' : ['icontains']
        }

