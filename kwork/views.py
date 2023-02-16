import asyncio
import json
import random
import string

from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views import View

from .forms import ServicesForm
from .helpers import check_proof
from .models import User, ClientSession, Payload, Services

import hashlib

from tonapi import Tonapi
import os
from dotenv import load_dotenv

from .serializers import ServicesSerializer

from rest_framework import generics

load_dotenv()

TON_API_KEY = os.getenv("TON_API_KEY")


class UserPageView(View):
    def get(self, request, *args, **kwargs):
        # Perform io-blocking view logic using await, sleep for example.
        # await asyncio.sleep(1)
        print(User.objects.all())
        return HttpResponse(User.objects.all())


class VerifView(View):
    def post(self, request, *args, **kwargs):
        payload = Payload.objects.create()
        return JsonResponse({"payload": payload.payload})


class CheckProfView(View):
    def post(self, request, *args, **kwargs):
        # Perform io-blocking view logic using await, sleep for example.
        # await asyncio.sleep(1)
        data = json.loads(request.body.decode("utf-8"))
        try:
            payload = Payload.objects.get(payload=data['proof']['payload'])
            payload.check_payload()
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        check_proof(data)

        profile, created = User.objects.get_or_create(wallet=data['address'])

        session = ClientSession.objects.create()
        session.authorize(profile)

        tonapi = Tonapi(api_key=TON_API_KEY)

        address = data['address']
        account = tonapi.account.get_info(account=address)

        return JsonResponse({
            "key": session.get_session_key(),
            "wallet": json.loads(account.address.json())
        })


# if request.content_type != 'application/json':
#    return HttpResponseBadRequest('Invalid content type')
class CreateServices(View):
    def post(self, request, *args, **kwargs):
        post_data = request.POST.copy()
        session = ClientSession.objects.get(session_key=request.GET.get('session_key'))
        post_data['user'] = session.user_id
        request.POST = post_data

        form = ServicesForm(request.POST, request.FILES)
        if form.is_valid():
            # Обработка формы при ее корректном заполнении
            form.save()
            print(form.data)
            return JsonResponse({'success': True})
        else:
            # Формируем словарь с ошибками валидации
            errors = {field: form.errors[field] for field in form.errors}
            return JsonResponse({'formisvalid': False, 'errors': errors})


class ServicesList(generics.ListAPIView):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer
