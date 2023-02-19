from datetime import timedelta

from django.db import models

from kwork.helpers import generate_random_session_key, TonProof
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


class Deals(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_id')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_id')

    description = models.TextField(max_length=2000)
    price = models.IntegerField()
    status = models.IntegerField()

    days_on_deal = models.IntegerField(verbose_name='Сколько будет длится сделка')
    date_start_deal = models.DateTimeField(verbose_name='Дата принятия сделки', null=True, default=None)
    date_create = models.DateTimeField(verbose_name='Дата, в которое создана сделка', default=django_datetime.now)
    date_finish = models.DateTimeField(verbose_name='Дата, в которое окончена сделка', null=True, default=None)