from datetime import timedelta

from django.db import models

from kwork.helpers import generate_random_session_key, generate_random_payload
from django.utils import timezone as django_datetime
from django.contrib.auth.models import AbstractBaseUser
from django.utils.text import slugify
from unidecode import unidecode


class User(models.Model):
    wallet = models.CharField(max_length=256)
    profession = models.CharField(max_length=60, null=True)

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


class Payload(models.Model):
    payload = models.CharField(verbose_name='Полезная нагрузка', max_length=128, default=generate_random_payload)
    data_expired = models.DateTimeField(verbose_name='Время окончания', default=django_datetime.now)

    def save(self, *args, **kwargs):
        if self.data_expired is None:
            self.data_expired = django_datetime.now
        self.data_expired += timedelta(minutes=5)
        super().save(*args, **kwargs)

    def check_payload(self):
        now = django_datetime.now()
        print(now)
        print(self.data_expired)
        if self.data_expired <= now:
            raise Exception("Payload expired")
        return True


class Services(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Заглавие услуги', max_length=64)
    image = models.ImageField(upload_to='service_images/')
    description = models.TextField(verbose_name='Описание услуги')
    price = models.IntegerField(verbose_name='Цена услуги')
    requirements = models.TextField(verbose_name='Требования услуги')
    completed = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.title))

        if Services.objects.filter(slug=self.slug).exists():
            # Генерируем новый slug, пока не найдем уникальный
            count = 1
            while Services.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(unidecode(self.title))}-{count}"
                count += 1

        super().save(*args, **kwargs)