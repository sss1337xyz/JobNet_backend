from django.db import models

from kwork.helpers import generate_random_session_key
from django.utils import timezone as django_datetime
from django.contrib.auth.models import AbstractBaseUser


class User(models.Model):
    wallet = models.CharField(max_length=256)
    profession = models.CharField(max_length=60)

    def __str__(self):
        return self.wallet

    @property
    def has_authorized_session(self):
        return hasattr(self, 'authorized_session')

    def unauthorize_from_current_session(self):
        if self.has_authorized_session:
            self.authorized_session.unauthorize()


class ClientSession(models.Model):
    session_key = models.CharField(verbose_name='Ключ сессии', max_length=128, default=generate_random_session_key)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='authorized_session', )
    authorized_at = models.DateTimeField(verbose_name='Время, в которое выполнена текущая авторизация', null=True,
                                         default=None)

    def authorize(self, profile):
        profile.unauthorize_from_current_session()
        self.user = profile
        self.authorized_at = django_datetime.now()

        self.save(update_fields=('user', 'authorized_at'))

    def unauthorize(self):
        self.user = None
        self.authorized_at = None

        self.save(update_fields=('user', 'authorized_at'))

    def get_session_key(self):
        return self.session_key
