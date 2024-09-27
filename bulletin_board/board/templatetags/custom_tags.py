from django.template import Library

from board.models import Category, Event

register = Library()

@register.inclusion_tag('show_posts_by_category.html')
def show_posts_by_category(cat_id):
    posts = Category.objects.get(pk=cat_id).events.all()
    return {'events': posts}

@register.inclusion_tag('show_authors_by_category.html')
def show_authors_by_category(cat_id):
    authors = Category.objects.get(pk=cat_id).player.all()
    return {'authors': authors}

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
   d = context['request'].GET.copy()
   for k, v in kwargs.items():
       d[k] = v
   return d.urlencode()

@register.inclusion_tag('show event.html')
def show_event(event_id):
    event = Event.objects.get(pk=event_id)
    return {'event' : event}