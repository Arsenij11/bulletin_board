from urllib.parse import urlencode

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.http import HttpResponse, QueryDict, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView

from .filters import EventFilter, AuthorFilter
from .models import Event, Responses, Players, Category, AnswertoResponse
from .forms import AddPostForm, AddResponseForm
from .utils import DataMixin

# Create your views here.

menu = [{'title' : 'Bulletin Board', 'URL' : 'main'},
        {'title' : 'О сайте', 'URL' : 'about'},
        {'title' : 'Создать объявление', 'URL' : 'create_event'},
        {'title' : 'Найти объявление', 'URL' : 'search_event'},
        {'title' : 'Найти автора', 'URL' : 'search_player'},
        {'title' : 'Войти', 'URL' : 'login'},
        {'title' : 'Создать профиль', 'URL' : 'create profile'}]



class MainPage(DataMixin,ListView):
    context_object_name = 'events'
    template_name = 'index.html'
    paginate_by = 1

    def get_queryset(self):
        return Event.objects.filter(is_published=True).annotate(total=Count('resp')).order_by('-time_create').select_related('player').prefetch_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context,title='Все объявления')


class PostSearch(DataMixin,ListView):
    template_name = 'search_event.html'
    context_object_name = 'events'
    paginate_by = 1

    def get_queryset(self):
        queryset = Event.published.all().annotate(total=Count('resp')).order_by('-time_create').select_related('player').prefetch_related('category')
        self.filterset = EventFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context, title='Поиск объявлений по фильтрам', filterset=self.filterset)




class About(DataMixin,TemplateView):
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context,
                                      title='О сайте',
                                      categories=Category.objects.annotate(total=Count('events')).filter(total__gt=0))



def show_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)

    author = True if request.path != reverse('category', kwargs={'category_slug' : category_slug}) else False

    return render(request=request, template_name='category.html', context={'category': category, 'menu' : menu, 'author' : author})

#
# class Show_posts_by_category(DataMixin,ListView):
#     template_name = 'category.html'
#     context_object_name = 'category'
#     paginate_by = 1
#
#     def get_queryset(self):
#         return Category.objects.filter(slug=self.kwargs['category_slug'])[0]
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return self.get_mixin_objects(context,
#                                       author=False)





class ShowPost(DataMixin,DetailView):
    template_name = 'detail_event.html'
    slug_url_kwarg = 'event_slug'
    context_object_name = 'event'

    def get_object(self, queryset=None):
        try:
            get_object_or_404(Event.published, slug=self.kwargs[self.slug_url_kwarg])
        except Http404:
            self.template_name = 'invalid_event.html'
            return None
        else:
            event = Event.published.filter(slug=self.kwargs[self.slug_url_kwarg]).prefetch_related('category')[0]
            return event


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects\
            (context,
            title=f'Объявление {context["event"].title}' if context["object"] is not None else 'Объявление не создано или находится на проверке',
             total=len(context["event"].resp.all()) if context["object"] is not None else None)




class CreateEvent(DataMixin,CreateView):
    template_name = 'create_event.html'
    model = Responses
    form_class = AddPostForm

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context, title=f'Создание объявления')

class UpdateEvent(DataMixin,UpdateView):
    model = Event
    form_class = AddPostForm
    template_name = 'create_event.html'
    pk_url_kwarg = 'event_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return self.get_mixin_objects(context,
                                      title=f'Редактирование объявления',
                                      update=True)

class CreateResponse(DataMixin,CreateView):
    template_name = 'create_response.html'
    model = Responses
    form_class = AddResponseForm
    pk_url_kwarg = "event_id"

    def form_valid(self, form):
        resp = form.save(commit=False)
        resp.event = Event.objects.get(pk=self.kwargs[self.pk_url_kwarg])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context,
                                      responses=Responses.objects.filter(event_id=self.kwargs[self.pk_url_kwarg]),
                                      event=Event.objects.get(pk=self.kwargs[self.pk_url_kwarg]))



class UpdateResponse(DataMixin,UpdateView):
    model = Responses
    template_name = 'update_response.html'
    fields = ['message']
    pk_url_kwarg = "resp_id"

    def form_valid(self, form):
        resp = form.save(commit=False)
        resp.event = Responses.objects.get(pk=self.kwargs[self.pk_url_kwarg]).event
        resp.player = Responses.objects.get(pk=self.kwargs[self.pk_url_kwarg]).player
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        event = Responses.objects.get(pk=self.kwargs[self.pk_url_kwarg]).event
        return self.get_mixin_objects(context,
                                      author=Responses.objects.get(pk=self.kwargs[self.pk_url_kwarg]).player,
                                      event=event,
                                      responses=Responses.objects.filter(event_id=event.pk),
                                      ourresp=Responses.objects.get(pk=self.kwargs[self.pk_url_kwarg]))


def delete_post(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)

    data = {
        'title' : f'Вы действительно хотите удалить объявление "{event.title}" ?',
        'menu' : menu,
        'event' : event

    }


    return render(request, 'delete_post.html', data)


def successful_delete(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    Event.objects.get(slug=event_slug).delete()
    return render(request, 'successful_delete.html', context={'event' : event, 'menu' : menu})


class PlayerProfile(DataMixin,DetailView):
    template_name = 'player.html'
    pk_url_kwarg = 'player_id'
    context_object_name = 'player'

    def get_object(self, queryset=None):
        return get_object_or_404(Players, pk=self.kwargs[self.pk_url_kwarg])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if str(context['player'].age)[-1] == '1':
            year = 'год'
        elif str(context['player'].age)[-1] in ['2', '3', '4']:
            year = 'года'
        else:
            year = 'лет'
        return self.get_mixin_objects(context,
                                      events=Event.published.filter(player_id=self.kwargs[self.pk_url_kwarg]),
                                      responses=Responses.objects.filter(player_id=self.kwargs[self.pk_url_kwarg]),
                                      year=year)



class CreateProfile(DataMixin,CreateView):
    model = Players
    fields = '__all__'
    template_name = 'create_profile.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context)

class UpdateProfile(DataMixin,UpdateView):
    model = Players
    fields = '__all__'
    pk_url_kwarg = 'player_id'
    template_name = 'create_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context,
                                      title=Players.objects.get(pk=self.kwargs[self.pk_url_kwarg]))


class SearchProfile(DataMixin,ListView):
    template_name = 'search_player.html'
    context_object_name = 'authors'
    paginate_by = 1

    def get_queryset(self):
        queryset = Players.objects.all().select_related('guild').select_related('user').prefetch_related('events')
        self.filterset = AuthorFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context,
                                      filterset=self.filterset,
                                      title='Поиск автора по фильтрам')




class AllResponses(DataMixin,ListView):
    template_name = 'responses.html'
    context_object_name = 'responses'


    def get_queryset(self):
        return Responses.objects.filter(event_id=self.kwargs['event_id']).select_related('player').select_related('event')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context,event=Event.objects.filter(pk=self.kwargs['event_id']).prefetch_related('category')[0])

def delete_response(request,resp_id):
    resp = get_object_or_404(Responses, pk=resp_id)
    Responses.objects.get(pk=resp_id).delete()

    return redirect(reverse('response', kwargs={'event_id': resp.event.pk}))

class AllAuthors(DataMixin,ListView):
    model = Players
    template_name = 'authors.html'
    context_object_name = 'authors'
    paginate_by = 1

    def get_queryset(self):
        return Players.objects.all().select_related('guild').prefetch_related('events')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context, title='Все авторы')


class AllAnswers(DataMixin,ListView):
    template_name = 'show_answers_to_response.html'
    context_object_name = 'answers'


    def get_queryset(self):
        return AnswertoResponse.objects.filter(resp_id=self.kwargs['resp_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = Responses.objects.get(pk=self.kwargs['resp_id']).event.pk
        return self.get_mixin_objects(context,
                                      responses=Responses.objects.filter(event_id=event_id),
                                      ourresp=Responses.objects.get(pk=self.kwargs['resp_id']).pk,
                                      event=Responses.objects.get(pk=self.kwargs['resp_id']).event)


class CreateAnswerToResponse(DataMixin,CreateView):
    model = AnswertoResponse
    fields = ['player', 'message']
    template_name = 'create_answer_to_response.html'


    def form_valid(self, form):
        answer = form.save(commit=False)
        answer.resp = Responses.objects.get(pk=self.kwargs['resp_id'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = Responses.objects.get(pk=self.kwargs['resp_id']).event.pk
        return self.get_mixin_objects(context,
                                      responses=Responses.objects.filter(event_id=event_id),
                                      ourresp=Responses.objects.get(pk=self.kwargs['resp_id']).pk,
                                      event=Responses.objects.get(pk=self.kwargs['resp_id']).event)


class UpdateAnswerToResponse(DataMixin,UpdateView):
    model = AnswertoResponse
    fields = ['message']
    template_name = 'update_answer_to_response.html'
    pk_url_kwarg = 'answ_id'

    def form_valid(self, form):
        answer = form.save(commit=False)
        answer.resp = AnswertoResponse.objects.get(pk=self.kwargs[self.pk_url_kwarg]).resp
        answer.player = AnswertoResponse.objects.get(pk=self.kwargs[self.pk_url_kwarg]).player
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resp_id = AnswertoResponse.objects.get(pk=self.kwargs[self.pk_url_kwarg]).resp.pk
        event_id = Responses.objects.get(pk=resp_id).event.pk
        return self.get_mixin_objects(context,
                                      responses=Responses.objects.filter(event_id=event_id),
                                      ourresp = Responses.objects.get(pk=resp_id).pk,
                                      ouransw = self.kwargs[self.pk_url_kwarg],
                                      event = Responses.objects.get(pk=resp_id).event,
                                      author = AnswertoResponse.objects.get(pk=self.kwargs[self.pk_url_kwarg]).player
                                      )


def delete_answer(request, answ_id):
    answer = get_object_or_404(AnswertoResponse, pk=answ_id)
    AnswertoResponse.objects.get(pk=answ_id).delete()

    return redirect(reverse('show answers to response', kwargs={'resp_id': answer.resp_id}))


def login(request):
    return HttpResponse('Авторизация')