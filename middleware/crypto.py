import os
import base64
import hashlib
import hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from middleware.setup import AES_KEY, HMAC_KEY


def encrypt(data: str):
    iv = os.urandom(16)

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()

    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv))
    encryptor = cipher.encryptor()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return base64.b64encode(iv + ciphertext).decode()


def decrypt(enc_data: str):
    raw = base64.b64decode(enc_data)

    iv = raw[:16]
    ciphertext = raw[16:]

    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv))
    decryptor = cipher.decryptor()

    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    return data.decode()


def sign(message: str):
    signature = hmac.new(HMAC_KEY, message.encode(), hashlib.sha256).hexdigest()

    return signature


def verify(message: str, signature: str):
    expected = sign(message)
    return hmac.compare_digest(expected, signature)
