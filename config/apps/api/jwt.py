import time

import jwt
from django.conf import settings


JWT_ALGORITHM = 'HS256'


def create_access_token(*, user) -> str:
    now = int(time.time())
    payload = {
        'sub': str(user.pk),
        'email': user.email,
        'name': user.get_full_name() or user.email,
        'iat': now,
        'exp': now + settings.JWT_ACCESS_TOKEN_TTL_SECONDS,
        'typ': 'access',
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(*, token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[JWT_ALGORITHM])
