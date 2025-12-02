from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
# Create your models here.

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'),max_length=150, unique=True)
    password = models.CharField(_('password hash'), max_length=128)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    is_admin = models.BooleanField(_('is admin'), default=False)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')