import random

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, EmailMultiAlternatives, mail_managers
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.deconstruct import deconstructible

from .models import EmailConfirm






class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput())
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput())

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']




class RegistrationForm(UserCreationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput())
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput())
    email = forms.CharField(label='E-mail', widget=forms.EmailInput(), required=True)

    class Meta:
        model = get_user_model()
        fields = ['username','email','password1', 'password2']


    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('Данный email уже был введён другим пользователем!')
        return email

    def save(self, commit=True):
        user = super(RegistrationForm, self).save()

        keys = [e.key for e in EmailConfirm.objects.all()] if len(EmailConfirm.objects.all()) > 0 else []

        list_of_codes = [i for i in range(1000,10000) if i not in keys]

        user_key = random.choice(list_of_codes)

        send_mail(
            subject='Добро пожаловать на наш сайт!',
            message=f'Здравствуйте!\nЧтобы закончить регистрацию, введите этот код {user_key}!'
                    f'\n\nС уважением,\nКоманда Bulletin Board\n\n\nP.s. : Если Вы не указывали данный e-mail, '
                    f'проигнорируйте сообщение',
            from_email=None,  # будет использовано значение DEFAULT_FROM_EMAIL
            recipient_list=[user.email],
        )

        EmailConfirm.objects.create(user_id=user.id, key=user_key)

        return user


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput())
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput())
    new_password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput())

class Confirm_Email(forms.Form):
    key = forms.IntegerField(label='Код подтверждения',
                             validators=[MinValueValidator(1000, 'Код подтверждения неверный!'),
                                         MaxValueValidator(9999, 'Код подтверждения неверный!'),
                                        ])

    def __init__(self,  *args, user_id=None):
        super().__init__(*args)
        self.user_id = user_id



    def clean_key(self):
        key = self.cleaned_data['key']
        check_key = EmailConfirm.objects.filter(key=key, user_id=self.user_id)
        if len(check_key) == 0:
            raise ValidationError('Код подтверждения неверный!')
        else:
            return key




