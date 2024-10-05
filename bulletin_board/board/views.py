from urllib.parse import urlencode

from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse, QueryDict, Http404, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView

from .filters import EventFilter, AuthorFilter, ResponseFilter
from .models import Event, Responses, Players, Category, AnswertoResponse
from .forms import AddPostForm, AddResponseForm
from .utils import DataMixin

# Create your views here.





class MainPage(DataMixin,ListView):
    context_object_name = 'events'
    template_name = 'index.html'

    def get_queryset(self):
        return Event.objects.filter(is_published=True).annotate(total=Count('resp')).order_by('-time_create').select_related('player').prefetch_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context,title='Все объявления')


class PostSearch(DataMixin,ListView):
    template_name = 'search_event.html'
    context_object_name = 'events'

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

    page_number = request.GET.get('page')

    return render(request=request, template_name='category.html', context={'category': category,  'author' : author, 'page_number': page_number})





class ShowPost(LoginRequiredMixin,DataMixin,DetailView):
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
            title=f'Объявление {context["event"].title}' if context["object"] is not None else 'Объявление не создано или находится в черновике',
             total=len(context["event"].resp.all()) if context["object"] is not None else None)




class CreateEvent(LoginRequiredMixin,DataMixin,CreateView):
    template_name = 'create_event.html'
    form_class = AddPostForm

    def form_valid(self, form):
        f = form.save(commit=False)
        f.player = Players.objects.get(user_id=self.request.user.id)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context, title=f'Создание объявления', update=False, player=Players.objects.get(user_id=self.request.user.id))

    def dispatch(self, request, *args, **kwargs):
        if Players.objects.filter(user_id=self.request.user.id).exists() or self.request.user.is_superuser:
            return super(CreateEvent, self).dispatch(request, *args, **kwargs)

        return redirect('create profile')



class UpdateEvent(LoginRequiredMixin,DataMixin,UpdateView):
    model = Event
    form_class = AddPostForm
    template_name = 'create_event.html'
    pk_url_kwarg = 'event_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return self.get_mixin_objects(context,
                                      title=f'Редактирование объявления',
                                      update=True,
                                      player=Players.objects.get(user_id=self.request.user.id))

    def dispatch(self, request, *args, **kwargs):
        if self.request.user == Event.objects.get(pk=self.kwargs[self.pk_url_kwarg]).player.user or self.request.user.is_superuser:
            return super(UpdateEvent, self).dispatch(request, *args, **kwargs)

        return redirect(reverse('detail',kwargs={'event_slug': Event.objects.get(pk=self.kwargs[self.pk_url_kwarg]).slug}))

class CreateResponse(LoginRequiredMixin,DataMixin,CreateView):
    template_name = 'create_response.html'
    model = Responses
    form_class = AddResponseForm
    pk_url_kwarg = "event_id"

    def form_valid(self, form):
        resp = form.save(commit=False)
        resp.event = Event.objects.get(pk=self.kwargs[self.pk_url_kwarg])
        resp.player = Players.objects.get(user_id=self.request.user.id)
        self.player = resp.player
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context,
                                      responses=Responses.objects.filter(event_id=self.kwargs[self.pk_url_kwarg]),
                                      event=Event.objects.get(pk=self.kwargs[self.pk_url_kwarg]),
                                      player=Players.objects.get(user_id=self.request.user.id))

    def dispatch(self, request, *args, **kwargs):
        if Players.objects.filter(user_id=self.request.user.id).exists() or self.request.user.is_superuser:
            return super(CreateResponse, self).dispatch(request,*args,**kwargs)

        return redirect('create profile')

    def get_success_url(self):
        resp = list(Responses.objects.filter(player_id=self.player.id, event_id=self.kwargs[self.pk_url_kwarg]).order_by('time_create'))[-1]

        if resp.event.player.user.id != resp.player.user.id:
            subject = 'Новый отклик!'
            text = f'{"Уважаемый" if resp.event.player.sex == "Male" else "Уважаемая"} {resp.event.player}!\n' \
                   f'Новый отклик от игрока {resp.player} к объявлению {resp.event}!\n\nС уважением,\nКоманда Bulletin Board'
            html = render_to_string(request=self.request, template_name='message_after_resp.html',
                                              context={'resp': resp})
            msg = EmailMultiAlternatives(
                subject=subject, body=text, from_email=None, to=[resp.event.player.user.email]
            )
            msg.attach_alternative(html, "text/html")
            msg.send()

        return reverse('response', kwargs={'event_id': self.kwargs[self.pk_url_kwarg]})






class UpdateResponse(LoginRequiredMixin,DataMixin,UpdateView):
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
    def dispatch(self, request, *args, **kwargs):
        if Responses.objects.get(pk=self.kwargs[self.pk_url_kwarg]).player is None:
            return redirect(reverse('response', kwargs={'event_id': Responses.objects.get(pk=self.kwargs[self.pk_url_kwarg]).event.id}))
        if self.request.user == Responses.objects.get(pk=self.kwargs[self.pk_url_kwarg]).player.user or self.request.user.is_superuser:
            return super(UpdateResponse, self).dispatch(request,*args,**kwargs)

        return redirect(reverse('response', kwargs={'event_id' : Responses.objects.get(pk=self.kwargs[self.pk_url_kwarg]).event.id}))






@login_required
def delete_post(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)

    data = {
        'title' : f'Вы действительно хотите удалить объявление "{event.title}" ?',
        'event' : event

    }

    return render(request, 'delete_post.html', data) if request.user == event.player.user or request.user.is_superuser else redirect(reverse('detail', kwargs={'event_slug': event_slug}))

@login_required
def successful_delete(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    event.delete()
    return render(request, 'successful_delete.html', context={'event' : event})


class PlayerProfile(LoginRequiredMixin, DataMixin,DetailView):
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



class CreateProfile(LoginRequiredMixin, DataMixin,CreateView):
    model = Players
    fields = ['name', 'age', 'sex', 'city','level','guild', 'profile_picture']
    template_name = 'create_profile.html'


    def form_valid(self, form):
        f = form.save(commit=False)
        f.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context)

    def dispatch(self, request, *args, **kwargs):
        if Players.objects.filter(user_id=self.request.user.id).exists():
            return redirect(reverse('player', kwargs={'player_id': Players.objects.get(user_id=self.request.user.id).id}))

        return super(CreateProfile, self).dispatch(request, *args, **kwargs)



class UpdateProfile(LoginRequiredMixin, DataMixin,UpdateView):
    model = Players
    fields = ['name', 'age', 'sex', 'city','level','guild', 'profile_picture']
    pk_url_kwarg = 'player_id'
    template_name = 'create_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context,
                                      title=Players.objects.get(pk=self.kwargs[self.pk_url_kwarg]))

    def dispatch(self, request, *args, **kwargs):
        if self.request.user == Players.objects.get(pk=self.kwargs[self.pk_url_kwarg]).user or self.request.user.is_superuser:
            return super(UpdateProfile, self).dispatch(request, *args, **kwargs)


        return redirect(reverse('player', kwargs={'player_id':self.kwargs[self.pk_url_kwarg]}))




class DeleteProfile(LoginRequiredMixin, DeleteView):
    template_name = 'delete_profile.html'
    model = Players
    pk_url_kwarg = 'player_id'
    context_object_name = 'author'



    def dispatch(self, request, *args, **kwargs):
        if self.request.user == Players.objects.get(pk=self.kwargs[self.pk_url_kwarg]).user or self.request.user.is_superuser:
            self.user = Players.objects.get(pk=self.kwargs[self.pk_url_kwarg]).user
            return super(DeleteProfile, self).dispatch(request, *args, **kwargs)

        return redirect(reverse('player', kwargs={'player_id': self.kwargs[self.pk_url_kwarg]}))

    def get_success_url(self):
        user = self.request.user
        if not user.is_superuser:
            logout(self.request)
        get_user_model().objects.get(pk=self.user.pk).delete()
        return reverse('main')


class SearchProfile(LoginRequiredMixin,DataMixin,ListView):
    template_name = 'search_player.html'
    context_object_name = 'authors'


    def get_queryset(self):
        queryset = Players.objects.all().select_related('guild').select_related('user').prefetch_related('events')
        self.filterset = AuthorFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context,
                                      filterset=self.filterset,
                                      title='Поиск автора по фильтрам')




class AllResponses(LoginRequiredMixin,ListView):
    template_name = 'responses.html'
    context_object_name = 'responses'


    def get_queryset(self):
        return Responses.objects.filter(event_id=self.kwargs['event_id']).select_related('player').select_related('event')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = Event.objects.filter(pk=self.kwargs['event_id']).prefetch_related('category')[0]
        return context

@login_required
def delete_response(request,resp_id):
    resp = get_object_or_404(Responses, pk=resp_id)

    if Responses.objects.get(pk=resp_id).player is None:
        if request.user.is_superuser or request.user == Responses.objects.get(pk=resp_id).event.player.user:
            Responses.objects.get(pk=resp_id).delete()
    else:
        if request.user == Responses.objects.get(pk=resp_id).player.user or request.user.is_superuser or request.user == Responses.objects.get(pk=resp_id).event.player.user:
            Responses.objects.get(pk=resp_id).delete()


    return redirect(reverse('response', kwargs={'event_id': resp.event.pk}))



class AllAuthors(LoginRequiredMixin,DataMixin,ListView):
    model = Players
    template_name = 'authors.html'
    context_object_name = 'authors'

    def get_queryset(self):
        return Players.objects.all().select_related('guild').prefetch_related('events')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_objects(context, title='Все авторы')


class AllAnswers(LoginRequiredMixin,ListView):
    template_name = 'show_answers_to_response.html'
    context_object_name = 'answers'


    def get_queryset(self):
        return AnswertoResponse.objects.filter(resp_id=self.kwargs['resp_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = Responses.objects.get(pk=self.kwargs['resp_id']).event.pk
        context['responses'] = Responses.objects.filter(event_id=event_id)
        context['ourresp'] = Responses.objects.get(pk=self.kwargs['resp_id']).pk
        context['event'] = Responses.objects.get(pk=self.kwargs['resp_id']).event
        return context


class CreateAnswerToResponse(LoginRequiredMixin,DataMixin,CreateView):
    model = AnswertoResponse
    fields = ['message']
    template_name = 'create_answer_to_response.html'


    def form_valid(self, form):
        answer = form.save(commit=False)
        answer.resp = Responses.objects.get(pk=self.kwargs['resp_id'])
        answer.player = Players.objects.get(user_id=self.request.user.id)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = Responses.objects.get(pk=self.kwargs['resp_id']).event.pk
        return self.get_mixin_objects(context,
                                      responses=Responses.objects.filter(event_id=event_id),
                                      ourresp=Responses.objects.get(pk=self.kwargs['resp_id']).pk,
                                      event=Responses.objects.get(pk=self.kwargs['resp_id']).event,
                                      player = Players.objects.get(user_id=self.request.user.id))

    def dispatch(self, request, *args, **kwargs):
        if Players.objects.filter(user_id=self.request.user.id).exists():
            return super(CreateAnswerToResponse,self).dispatch(request,*args,**kwargs)

        return redirect(reverse('show answers to response', kwargs={'resp_id' : self.kwargs['resp_id']}))

    def get_success_url(self):
        answ = list(AnswertoResponse.objects.filter(player_id=self.request.user.player.id,
                                                    resp_id=self.kwargs['resp_id']).order_by('time_create'))[-1]

        if self.request.user.id != answ.resp.player.user.id:
            subject = 'Новый отклик!'
            text = f'{"Уважаемый" if answ.resp.player.sex == "Male" else "Уважаемая"} {answ.resp.player}!\n' \
                       f'Игрок {answ.player} прокомментировал Ваш отклик к объявлению {answ.resp.event}!\n\nС уважением,\nКоманда Bulletin Board'
            html = render_to_string(request=self.request, template_name='message_after_answ.html',
                                        context={'answ': answ})
            msg = EmailMultiAlternatives(
                    subject=subject, body=text, from_email=None, to=[answ.resp.player.user.email]
                )
            msg.attach_alternative(html, "text/html")
            msg.send()

        return reverse('show answers to response', kwargs={'resp_id':self.kwargs['resp_id']})



class UpdateAnswerToResponse(LoginRequiredMixin,DataMixin,UpdateView):
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

    def dispatch(self, request, *args, **kwargs):
        if AnswertoResponse.objects.get(pk=self.kwargs[self.pk_url_kwarg]).player is None:
            return redirect(reverse('show answers to response',
                                    kwargs={
                                        'resp_id': AnswertoResponse.objects.get(pk=self.kwargs['answ_id']).resp.id}))
        else:
            if self.request.user == AnswertoResponse.objects.get(pk=self.kwargs[self.pk_url_kwarg]).player.user \
                    or self.request.user.is_superuser:
                return super(UpdateAnswerToResponse, self).dispatch(request,*args, **kwargs)

        return redirect(reverse('show answers to response',
                                kwargs={'resp_id' : AnswertoResponse.objects.get(pk=self.kwargs['answ_id']).resp.id}))

@login_required
def delete_answer(request, answ_id):
    answer = get_object_or_404(AnswertoResponse, pk=answ_id)

    if AnswertoResponse.objects.get(pk=answ_id).player is None:
        if request.user.is_superuser or AnswertoResponse.objects.get(pk=answ_id).resp.event.player.user == request.user:
            AnswertoResponse.objects.get(pk=answ_id).delete()
    else:
        if request.user == AnswertoResponse.objects.get(pk=answ_id).player.user or request.user.is_superuser\
                or AnswertoResponse.objects.get(pk=answ_id).resp.event.player.user == request.user:

            AnswertoResponse.objects.get(pk=answ_id).delete()

    return redirect(reverse('show answers to response', kwargs={'resp_id': answer.resp_id}))

class PrivateWebPage(LoginRequiredMixin, DataMixin,ListView):
    template_name = 'private_page.html'
    context_object_name = 'responses'

    def get_queryset(self):
        events = Event.published.filter(player_id=self.kwargs['player_id']).prefetch_related('resp').prefetch_related('category').select_related('player')
        responses = Responses.objects.filter(Q(event__in=events) & ~Q(player_id=self.kwargs['player_id']) & ~Q(player_id=None))
        self.filterset = ResponseFilter(self.request.GET, queryset=responses, request=self.request.user.id)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

    def dispatch(self, request, *args, **kwargs):
        if self.request.user == Players.objects.get(pk=self.kwargs['player_id']).user:
            return super(PrivateWebPage, self).dispatch(request,*args, **kwargs)

        return redirect(reverse('player', kwargs={'player_id' : self.kwargs['player_id']}))

def take_player_by_response(request, resp_id):
    resp = get_object_or_404(Responses, pk=resp_id)

    if resp.player is not None:
        if not resp.is_taken and request.user == resp.event.player.user and resp.event.player.user != resp.player.user:
            send_mail(
                subject='Ваш отклик принят!',
                message=f'{"Уважаемый" if resp.player.sex == "Male" else "Уважаемая"} {resp.player}!\n'
                        f'Ваш отклик "{resp}" на объявление {resp.event} был принят!\n\nПоздравляем,\nКоманда Bulletin Board',
                from_email=None,
                recipient_list=[resp.player.user.email],
                html_message=render_to_string(request=request,template_name='message_for_taken_players.html',context={'resp' : resp})
            )
            Responses.objects.filter(pk=resp_id).update(is_taken=True)

    return redirect(reverse('private webpage', kwargs={'player_id' : request.user.player.id}))\
        if request.user == resp.event.player.user else redirect(reverse('response', kwargs={'event_id' : resp.event.id}))


class Draft(LoginRequiredMixin,DataMixin,ListView):
    template_name = 'draft.html'
    context_object_name = 'events'


    def get_queryset(self):
        return Event.objects.filter(is_published=False, player_id=self.kwargs['player_id']).select_related('player').prefetch_related('category')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user == Players.objects.get(pk=self.kwargs['player_id']).user \
                or self.request.user.is_superuser:
            return super(Draft, self).dispatch(request,*args, **kwargs)

        return redirect(reverse('player', kwargs={'player_id' : self.kwargs['player_id']}))


