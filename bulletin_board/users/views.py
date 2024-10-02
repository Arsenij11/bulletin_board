from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from .forms import LoginUserForm, RegistrationForm, UserPasswordChangeForm


# Create your views here.





class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'


class Registration(CreateView):
    template_name = 'register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('users:login')


class UserPasswordChange(PasswordChangeView):
    template_name = 'password_change_form.html'
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')


def logout_user(request):
    logout(request)
    return redirect(reverse('users:login'))