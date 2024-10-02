from django import forms
from django.core.exceptions import ValidationError

from .models import Event, Players, Responses


def get_event(event_id):
    return Event.objects.get(pk=event_id)

class AddPostForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'slug','text', 'category','awards', 'requirement_level', 'photo', 'video']
        widgets = {'title' : forms.TextInput(attrs={'class' : 'form-input'}),
                   'text' : forms.Textarea(attrs={'cols' : 50, 'rows' : 5}),
                   'awards': forms.Textarea(attrs={'cols': 50, 'rows': 5})
                   }


class AddResponseForm(forms.ModelForm):
    class Meta:
        model = Responses
        fields = ['message']

        widgets = {'message' : forms.Textarea(attrs={'cols' : 50, 'rows' : 5})}







