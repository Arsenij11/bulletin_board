from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class EmailConfirm(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='confirm')
    key = models.IntegerField()
    registration_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} : {self.key}'

    class Meta:
        verbose_name = 'Код подтверждения'
        verbose_name_plural = 'Коды подтверждения'


