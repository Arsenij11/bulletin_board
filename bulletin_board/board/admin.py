from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from .models import Event, Players, Responses, Category



@admin.register(Event)
class EventPanel(admin.ModelAdmin):
    list_display = ['title', 'preview','slug','player','post_photo','categories','is_published', 'time_create', 'time_update', 'brief_info_of_awards', 'requirement_level', 'count_of_responses']
    fields = ['title','slug','text','player','post_photo','photo','video','category','is_published', 'awards', 'requirement_level']
    readonly_fields = ['post_photo']
    ordering = ['-time_create']
    list_display_links = ['title', 'preview']
    list_editable = ['is_published']
    actions = ['set_published', 'set_draft']
    filter_horizontal = ['category']


    @admin.display(description='Фото объявления')
    def post_photo(self, event: Event):
        return mark_safe(f'<img src={event.photo.url} width=100>') if event.photo else 'Без фото'

    @admin.display(description='Награды')
    def brief_info_of_awards(self, event: Event):
        return event.awards[:50] + '...'

    @admin.display(description='Количество откликов на объявление')
    def count_of_responses(self, event: Event):
        return len(event.resp.all())

    @admin.display(description='Категории')
    def categories(self, event: Event):
        return list(event.category.all())

    @admin.action(description='Опубликовать выбранные записи')
    def set_published(self, request, queryset):
        for q in queryset:
            if q.is_published:
                return self.message_user(request, 'Ошибка! В записях присутствуют уже опубликованные!', messages.ERROR)

        count = queryset.update(is_published=True)

        correct_word = None
        correct_ending = 'Опубликован'

        if str(count)[-1] == '1' and str(count)[-1:-3:-1] != '11':
            correct_word = 'запись'
            correct_ending += 'a'
        elif str(count)[-1] in ['2','3','4'] and str(count)[-1:-3:-1] not in ['12','13','14']:
            correct_word = 'записи'
            correct_ending += 'ы'
        else:
            correct_word = 'записей'
            correct_ending += 'ы'

        return self.message_user(request, f'{correct_ending} {count} {correct_word}', messages.SUCCESS)

    @admin.action(description='Снять с публикации выбранные записи')
    def set_draft(self, request, queryset):
        for q in queryset:
            if not q.is_published:
                return self.message_user(request, 'Ошибка! В записях присутствуют уже снятые с публикации!', messages.ERROR)

        count = queryset.update(is_published=False)

        correct_word = None
        correct_ending = 'Снят'

        if str(count)[-1] == '1' and str(count)[-1:-3:-1] != '11':
            correct_word = 'запись'
            correct_ending += 'a'
        elif str(count)[-1] in ['2', '3', '4'] and str(count)[-1:-3:-1] not in ['12','13','14']:
            correct_word = 'записи'
            correct_ending += 'ы'
        else:
            correct_word = 'записей'
            correct_ending += 'ы'

        return self.message_user(request, f'{correct_ending} с публикации {count} {correct_word}', messages.SUCCESS)


class PostFilter(admin.SimpleListFilter):
    title = 'Количество постов'
    parameter_name = 'count_of_posts'

    def lookups(self, request, model_admin):
        return [('Nothing', 'Ни одного поста'), ('1-5', '1-5'), ('5 and upper', 'Выше 5')]

    def queryset(self, request, queryset):
        if self.value() == 'Nothing':
            return queryset.filter(name__in=[q.name for q in queryset.all() if len(q.events.all()) == 0])
        elif self.value() == '1-5':
            return queryset.filter(name__in=[q.name for q in queryset.all() if len(q.events.all()) in range(1,5)])
        elif self.value() == '5 and upper':
            return queryset.filter(name__in=[q.name for q in queryset.all() if len(q.events.all()) >= 5])
        else:
            return queryset

class PlayerFilter(admin.SimpleListFilter):
    title = 'Количество игроков, принадлежащих к гильдии'
    parameter_name = 'count_of_players'

    def lookups(self, request, model_admin):
        return [('Nothing', 'Ни одного'), ('1-5', '1-5'), ('5 and upper','5 и выше')]

    def queryset(self, request, queryset):
        if self.value() == 'Nothing':
            return queryset.filter(name__in=[q.name for q in queryset.all() if len(q.player.all()) == 0])
        elif self.value() == '1-5':
            return queryset.filter(name__in=[q.name for q in queryset.all() if len(q.player.all()) in range(1,5)])
        elif self.value() == '5 and upper':
            return queryset.filter(name__in=[q.name for q in queryset.all() if len(q.player.all()) >= 5])
        else:
            return queryset


@admin.register(Category)
class CategoryPanel(admin.ModelAdmin):
    list_display = ['name', 'slug', 'posts', 'players']
    ordering = ['name']
    prepopulated_fields = {'slug' : ('name', )}
    list_display_links = ['name', 'slug']
    list_filter = [PostFilter, PlayerFilter]

    @admin.display(description='Количество объявлений, связанных с категорией')
    def posts(self, category: Category):
        return len(category.events.all())

    @admin.display(description='Количество игроков, принадлежащих к гильдии')
    def players(self, category: Category):
        return len(category.player.all())


class RatingFilter(admin.SimpleListFilter):
    title = 'Рейтинг'
    parameter_name = 'r'

    def lookups(self, request, model_admin):
        return [('Less than 1.0', 'Меньше 1.0'), ('1.0 - 3.0','1.0 - 3.0'), ('3.0 - 5.0', '3.0 - 5.0'), ('5.0', '5.0')]

    def queryset(self, request, queryset):
        if self.value() == 'Less than 1.0':
            return queryset.filter(rating__lt=1.0)
        elif self.value() == '1.0 - 3.0':
            return queryset.filter(rating__range=(1.0, 3.0 - 0.1))
        elif self.value() == '3.0 - 5.0':
            return queryset.filter(rating__range=(3.0, 5.0 - 0.1))
        elif self.value() == '5.0':
            return queryset.filter(rating=5.0)
        else:
            return queryset

class LevelFilter(admin.SimpleListFilter):
    title = 'Уровень'
    parameter_name = 'Level'

    def lookups(self, request, model_admin):
        return [('Less than 10','Ниже 10'), ('10-30', '10-30'), ('30-50', '30-50'), ('50', '50')]

    def queryset(self, request, queryset):
        if self.value() == 'Less than 10':
            return queryset.filter(level__lt=10)
        elif self.value() == '10-30':
            return queryset.filter(level__range=(10,30-1))
        elif self.value() == '30-50':
            return queryset.filter(level__range=(30,50-1))
        elif self.value() == '50':
            return queryset.filter(level=50)
        else:
            return queryset

class CountOfPostFilter(admin.SimpleListFilter):
    title = 'Количество постов'
    parameter_name = 'count_of_posts'

    def lookups(self, request, model_admin):
        return [('Nothing', 'Ни одного поста'), ('1-5', '1-5'), ('5 and upper', 'Выше 5')]

    def queryset(self, request, queryset):
        if self.value() == 'Nothing':
            return queryset.filter(name__in=[q.name for q in queryset.all() if len(q.events.all()) == 0])
        elif self.value() == '1-5':
            return queryset.filter(name__in=[q.name for q in queryset.all() if len(q.events.all()) in range(1,5)])
        elif self.value() == '5 and upper':
            return queryset.filter(name__in=[q.name for q in queryset.all() if len(q.events.all()) >= 5])
        else:
            return queryset

class CountOfResponsesFilter(admin.SimpleListFilter):
    title = 'Количество откликов'
    parameter_name = 'count_of_resp'

    def lookups(self, request, model_admin):
        return [('Nothing', 'Ни одного отклика'), ('1-5', '1-5'), ('5 and upper', 'Выше 5')]

    def queryset(self, request, queryset):
        if self.value() == 'Nothing':
            return queryset.filter(name__in=[q.name for q in queryset.all() if len(q.resp.all()) == 0])
        elif self.value() == '1-5':
            return queryset.filter(name__in=[q.name for q in queryset.all() if len(q.resp.all()) in range(1,5)])
        elif self.value() == '5 and upper':
            return queryset.filter(name__in=[q.name for q in queryset.all() if len(q.resp.all()) >= 5])
        else:
            return queryset

class IsProfilePictureFilter(admin.SimpleListFilter):
    title = 'Аватарка'
    parameter_name = 'ava'

    def lookups(self, request, model_admin):
        return [('Yes', 'Есть'), ('No', 'Нет')]

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(name__in=[q.name for q in queryset.all() if q.profile_picture])
        elif self.value() == 'No':
            return queryset.filter(name__in=[q.name for q in queryset.all() if not q.profile_picture])
        else:
            return queryset

@admin.register(Players)
class PlayersPanel(admin.ModelAdmin):
    list_display = ['name', 'user', 'ava', 'registration_time','level', 'rating','age', 'sex', 'city', 'guild', 'count_of_posts', 'count_of_responses',]
    fields = ['name', 'user', 'profile_picture','ava', 'level', 'rating','age', 'sex', 'city', 'guild', ]
    readonly_fields = ['ava']
    ordering = ['-level', '-rating', 'name', ]
    list_display_links = ['name', 'user']
    list_editable = ['level','age', 'city', 'rating']
    actions = ['set_null_age', 'set_null_city', 'up_rating_to_max', 'up_rating_to_one', 'down_rating_to_min', 'down_rating_to_one']
    # list_per_page = 5
    list_filter = [RatingFilter,LevelFilter,CountOfPostFilter, CountOfResponsesFilter, IsProfilePictureFilter, 'guild', 'sex']

    @admin.display(description='Текущая аватарка')
    def ava(self, player: Players):
        return mark_safe(f'<img src="{player.profile_picture.url}" width="100">') if player.profile_picture else 'Без аватарки'

    @admin.display(description='Количество объявлений, выставленных пользователем')
    def count_of_posts(self, player: Players):
        return len(player.events.all())

    @admin.display(description='Количество откликов, оставленных пользователем')
    def count_of_responses(self, player: Players):
        return len(player.resp.all())

    @admin.action(description='Стереть данные о возрасте')
    def set_null_age(self, request, queryset):
        for q in queryset:
            if q.age is None:
                return self.message_user(request, 'Ошибка! В выбранных записях присутствуют пользователи без данных о возрасте!', messages.ERROR)


        list_of_names = ', '.join([query.name for query in queryset.all()])

        queryset.update(age=None)

        return self.message_user(request, f'Данные о возрасте были успешно удалены у следующих пользователей: {list_of_names}', messages.SUCCESS)

    @admin.action(description='Стереть данные о городе проживания')
    def set_null_city(self, request, queryset):
        for q in queryset:
            if q.city is None:
                return self.message_user(request, 'Ошибка! В выбранных записях присутствуют пользователи без данных о городе проживания!', messages.ERROR)

        list_of_names = ', '.join([query.name for query in queryset.all()])

        queryset.update(city=None)

        return self.message_user(request,
                                 f'Данные о городе были успешно удалены у следующих пользователей: {list_of_names}',
                                 messages.SUCCESS)

    @admin.action(description='Повысить рейтинг до 5.0 (максимума)')
    def up_rating_to_max(self, request, queryset):
        for q in queryset:
            if q.rating == 5.0:
                return self.message_user(request, 'Ошибка! В списке присутствует пользователь с максимальным уровнем рейтинга!', messages.ERROR)



        count = queryset.update(rating=5.0)

        correct_word = 'пользователя' if str(count)[-1] == '1' and str(count)[-1:-3:-1] != '11' else 'пользователей'


        return self.message_user(request, f'Рейтинг был успешно повышен до максимума у {count} {correct_word}', messages.SUCCESS)

    @admin.action(description='Повысить рейтинг на 1.0')
    def up_rating_to_one(self, request, queryset):
        for q in queryset:
            if q.rating > 4.0:
                return self.message_user(request,
                                         'Ошибка! В списке присутствует пользователь с уровнем рейтинга, находящимся в диапазоне (4.0, 5.0] !',
                                         messages.ERROR)


        count = 0
        for query in queryset:
            rating = query.rating
            queryset.filter(pk=query.pk).update(rating=rating+1.0)
            count += 1


        correct_word = 'пользователя' if str(count)[-1] == '1' and str(count)[-1:-3:-1] != '11' else 'пользователей'

        return self.message_user(request, f'Рейтинг был успешно повышен на 1.0 у {count} {correct_word}', messages.SUCCESS)

    @admin.action(description='Обнулить рейтинг')
    def down_rating_to_min(self, request, queryset):
        for q in queryset:
            if q.rating == 0.0:
                return self.message_user(request,
                                         'Ошибка! В списке присутствует пользователь с минимальным уровнем рейтинга!',
                                         messages.ERROR)

        count = queryset.update(rating=0.0)

        correct_word = 'пользователя' if str(count)[-1] == '1' and str(count)[-1:-3:-1] != '11' else 'пользователей'

        return self.message_user(request, f'Рейтинг был обнулён у {count} {correct_word}',
                                 messages.WARNING)

    @admin.action(description='Понизить рейтинг на 1.0')
    def down_rating_to_one(self, request, queryset):
        for q in queryset:
            if q.rating < 1.0:
                return self.message_user(request,
                                         'Ошибка! В списке присутствует пользователь с уровнем рейтинга, находящимся в диапазоне [0.0, 1.0)!',
                                         messages.ERROR)


        count = 0
        for query in queryset:
            rating = query.rating
            queryset.filter(pk=query.pk).update(rating=rating-1.0)
            count += 1


        correct_word = 'пользователя' if str(count)[-1] == '1' and str(count)[-1:-3:-1] != '11' else 'пользователей'

        return self.message_user(request, f'Рейтинг был понижен на 1.0 у {count} {correct_word}', messages.WARNING)


@admin.register(Responses)
class ResponsesPanel(admin.ModelAdmin):
    list_display = ['event', 'time_create', 'player', 'message', ]
    ordering = [ '-time_create', 'event', 'player__name']
    list_display_links = ['event', 'time_create']

