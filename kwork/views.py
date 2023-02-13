import asyncio
import json
import random
import string

from django.http import HttpResponse, JsonResponse
from django.views import View

from .helpers import check_proof
from .models import User, ClientSession

import nacl.signing
import tonsdk
from tonsdk import boc

import hashlib
import base64


def random_sha256_hash():
    input_data = 'random_input_data'
    hash_object = hashlib.sha256(input_data.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig


class UserPageView(View):
    def get(self, request, *args, **kwargs):
        # Perform io-blocking view logic using await, sleep for example.
        # await asyncio.sleep(1)
        print(User.objects.all())
        return HttpResponse(User.objects.all())


class VerifView(View):
    def post(self, request, *args, **kwargs):
        # Perform io-blocking view logic using await, sleep for example.
        # await asyncio.sleep(1)
        print(request)
        return JsonResponse({"payload": random_sha256_hash()})


class CheckProfView(View):
    def post(self, request, *args, **kwargs):
        # Perform io-blocking view logic using await, sleep for example.
        # await asyncio.sleep(1)
        data = json.loads(request.body.decode("utf-8"))
        check_proof(data)

        profile = User.objects.get(wallet='asdzasscz123')
        session = ClientSession.objects.create()
        session.authorize(profile)

        return JsonResponse({"key": session.get_session_key()})
