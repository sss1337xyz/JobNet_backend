import json
import logging
import time

from django.http import HttpResponse, JsonResponse
from django.views import View

from .forms import ServicesForm
from .helpers import TonProof
from .models import User, ClientSession, Services

from tonapi import Tonapi
import os
from dotenv import load_dotenv

from .modules.mixins import AuthMixin
from .serializers import ServicesSerializer

from rest_framework import generics
import redis

load_dotenv()

TON_API_KEY = os.getenv("TON_API_KEY")


class UserPageView(View):
    def get(self, request, *args, **kwargs):
        print(User.objects.all())
        return HttpResponse(User.objects.all())


class PayloadView(View):
    def post(self, request, *args, **kwargs):
        # TODO: переделать под Redis с hget hset где должен возвращаться json payload_key: 1, payload_action
        with redis.Redis() as r:
            key = r.incr('payloads_counter')
            payload_key = f'payload_key{key}'
            random_payload = TonProof.generate_random_payload()
            r.set(payload_key, str(random_payload), ex=300)
            response_payload = json.dumps({
                "key": payload_key,
                "payload": random_payload
            })

        return JsonResponse({"payload": response_payload})

    def dispatch(self, *args, **kwargs):
        start_time = time.time()
        response = super().dispatch(*args, **kwargs)
        total = (time.time() - start_time) * 1000
        print(total)
        # or
        # response['X-total-time'] = total
        return response


class CheckProfView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode("utf-8"))
        try:
            payload = json.loads(data['proof']['payload'])
            with redis.Redis() as r:
                r_payload = r.get(payload['key'])

                if r_payload is None:
                    raise Exception("Payload expired")
                if r_payload.decode("utf-8") != payload['payload']:
                    raise Exception("Payload incorrect")

            TonProof.check_proof(data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

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


class CreateServices(AuthMixin, View):
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
