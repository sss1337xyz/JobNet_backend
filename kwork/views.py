import asyncio
import json
import random
import string

from django.http import HttpResponse, JsonResponse
from django.views import View

from .helpers import check_proof
from .models import User, ClientSession, Payload

import hashlib

from tonapi import Tonapi
import os
from dotenv import load_dotenv

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


class TestMethod(View):
    def get(self, request, *args, **kwargs):
        tonapi = Tonapi(api_key=TON_API_KEY)

        address = "0:22c9618a3b2d18b0e0ccf4b268dfe2569c7a1475b5f63fdd0571b86e52774890"
        account = tonapi.account.get_info(account=address)
        print(account)
        return JsonResponse(account.address.json(), safe=False)
