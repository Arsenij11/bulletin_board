from django.core.paginator import Paginator
from django.template import Library

from board.models import Category, Event

register = Library()

@register.inclusion_tag('show_posts_by_category.html')
def show_posts_by_category(cat_id, page_number):
    posts = Category.objects.get(pk=cat_id).events.filter(is_published=True)

    paginator = Paginator(posts, 1)

    page_obj = paginator.get_page(page_number)

    return {'events': posts, 'page_obj' : page_obj, 'paginator' : paginator}

@register.inclusion_tag('show_authors_by_category.html')
def show_authors_by_category(cat_id, page_number):
    authors = Category.objects.get(pk=cat_id).player.all()

    paginator = Paginator(authors, 1)

    page_obj = paginator.get_page(page_number)

    return {'authors': authors, 'page_obj' : page_obj, 'paginator' : paginator}

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
   d = context['request'].GET.copy()
   for k, v in kwargs.items():
       d[k] = v
   return d.urlencode()

@register.inclusion_tag('show event.html')
def show_event(event_id, user):
    event = Event.objects.get(pk=event_id)
    return {'event' : event, 'user' : user}

@register.inclusion_tag('information of response.html')
def inf_resp(r, user):
    return {'r' : r, 'user':user}

@register.inclusion_tag('information of answer.html')
def inf_answ(a, user):
    return {'a' : a, 'user' : user}