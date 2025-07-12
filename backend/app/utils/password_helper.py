import os
import base64
import hashlib
import hmac

ITERATIONS = 100_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, ITERATIONS)
    return base64.b64encode(salt + dk).decode()


def verify_password(password: str, hashed: str) -> bool:
    data = base64.b64decode(hashed.encode())
    salt = data[:16]
    dk = data[16:]
    new_dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, ITERATIONS)
    return hmac.compare_digest(dk, new_dk)

