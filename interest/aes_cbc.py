import os
import base64
from Crypto.Cipher import AES


def _format(v):
    v = str(v)
    while len(v) % 16 != 0:
        v += '\0'
    return v.encode()


def encrypt(password):
    iv = key = os.environ['aeskey']
    aes = AES.new(_format(key), AES.MODE_CBC, iv)
    dtext = aes.encrypt(_format(password))
    return base64.encodebytes(dtext).decode()


def decrypt(encrypt_password):
    iv = key = os.environ['aeskey']
    text = base64.b64decode(encrypt_password)
    aes = AES.new(_format(key), AES.MODE_CBC, _format(iv))
    return aes.decrypt(text).decode().replace('\0', '')
