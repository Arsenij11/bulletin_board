import random

from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, DeleteView

from .forms import LoginUserForm, RegistrationForm, UserPasswordChangeForm, Confirm_Email

from .models import EmailConfirm

# Create your views here.





class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'

    def form_valid(self, form):
        f = form.cleaned_data
        if EmailConfirm.objects.filter(user__username=f['username']).exists():
            return redirect(reverse('users:confirm_email', kwargs={'user_id': get_user_model().objects.get(username=f['username']).pk}))
        return super().form_valid(form)

class Registration(CreateView):
    template_name = 'register.html'
    form_class = RegistrationForm


    def form_valid(self, form):
        form = form.save(commit=False)
        self.user_id = form.id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('users:confirm_email', kwargs={'user_id': self.user_id})



class UserPasswordChange(PasswordChangeView):
    template_name = 'password_change_form.html'
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')





def confirm_email(request, user_id):
    if request.method == 'POST':
        form = Confirm_Email(request.POST,user_id=user_id)
        if form.is_valid():
            check_key = EmailConfirm.objects.filter(key=form.cleaned_data['key'], user_id=user_id)
            check_key.delete()
            return render(request, 'successful_registration.html')


    else:
        form = Confirm_Email()

    return render(request, 'confirm_email.html', {'form' : form})




def logout_user(request):
    logout(request)
    return redirect(reverse('users:login'))