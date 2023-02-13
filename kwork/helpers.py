import random
import string

from kwork import models
import nacl.signing
import tonsdk
from tonsdk import boc

import hashlib
import base64


def generate_random_password(length=128):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_session_key():
    while True:
        session_key = generate_random_password()
        if not models.ClientSession.objects.filter(session_key=session_key).exists():
            break

    return session_key


def random_sha256_hash(text):
    hash_object = hashlib.sha256(text.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig


def generate_random_payload():
    while True:
        payload = random_sha256_hash(generate_random_password())
        if not models.Payload.objects.filter(payload=payload).exists():
            break

    return payload


def check_proof(data):
    received_state_init = data['proof']['state_init']
    received_address = data['address']
    adr = received_address.split(':')
    state_init = boc.Cell.one_from_boc(base64.b64decode(received_state_init))

    address_hash_part = base64.b16encode(state_init.bytes_hash()).decode('ascii').lower()
    assert received_address.endswith(address_hash_part)

    public_key = state_init.refs[1].bits.array[8:][:32]

    verify_key = nacl.signing.VerifyKey(bytes(public_key))

    received_timestamp = data['proof']['timestamp']
    signature = data['proof']['signature']

    message = (b'ton-proof-item-v2/'
               + (0).to_bytes(4, 'big') + bytearray.fromhex(adr[1])
               + (data['proof']['domain']['lengthBytes']).to_bytes(4, 'little') + data['proof']['domain'][
                   'value'].encode()
               + received_timestamp.to_bytes(8, 'little')
               + data['proof']['payload'].encode())

    signed = b'\xFF\xFF' + b'ton-connect' + hashlib.sha256(message).digest()

    result = verify_key.verify(hashlib.sha256(signed).digest(), base64.b64decode(signature))
