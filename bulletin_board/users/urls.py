from django.contrib.auth.views import PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, reverse_lazy
from . import views

app_name = 'users'

urlpatterns = [
    path('login', views.LoginUser.as_view(), name='login'),
    path('logout', views.logout_user, name='logout'),
    path('registration', views.Registration.as_view(), name='registration'),
    path('password-change', views.UserPasswordChange.as_view(), name='password_change'),
    path('password-change/done/',
         PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
    path('password-reset/', PasswordResetView.as_view(
                            template_name='password_reset_form.html',
                            email_template_name='password_reset_email.html',
                            success_url=reverse_lazy('users:password_reset_done')), name='password_reset_form'),
    path('password-reset/done/', PasswordResetDoneView.as_view(
                                 template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
                                             template_name='password_reset_confirm.html',
                                             success_url=reverse_lazy('users:password_reset_complete')), name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(
                                     template_name='password_reset_complete.html'), name='password_reset_complete')
]