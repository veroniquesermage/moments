from datetime import datetime

from jose import jwt

from app.core.config import settings

# Paramètres JWT
SECRET_KEY = settings.jwt_secret
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_at: datetime) -> str:
    to_encode = data.copy()
    to_encode.update({"purpose": 'access_token', "exp": expires_at})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
