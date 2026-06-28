from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
from hashlib import md5
import hashlib
from uuid import uuid1


def AES_Encrypt(data):
    key = b"u2oh6Vu^HWe4_AES"
    iv = b"u2oh6Vu^HWe4_AES"
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data.encode("utf-8")) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(encrypted_data).decode("utf-8")


def generate_captcha_key(timestamp: int):
    captcha_key = md5((str(timestamp) + str(uuid1())).encode("utf-8")).hexdigest()
    encoded_timestamp = (
        md5((str(timestamp) + "42sxgHoTPTKbt0uZxPJ7ssOvtXr3ZgZ1" + "slide" + captcha_key).encode("utf-8")).hexdigest()
        + ":" + str(int(timestamp) + 0x493E0)
    )
    return [captcha_key, encoded_timestamp]


def verify_param_seatengine(params, submit_enc_value):
    hash_parts = []
    for key in sorted(params.keys()):
        hash_parts.append(f"[{key}={str(params[key])}]")
    hash_parts.append(f"[{submit_enc_value}]")
    return hashlib.md5("".join(hash_parts).encode("utf-8")).hexdigest()
