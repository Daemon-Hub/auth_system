from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from uuid import uuid4

from ..settings import settings 

__all__ = ("create_access_token", "decode_token")

def create_access_token(data: dict):
    to_encode = data.copy()
    access_token_expires = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jti = str(uuid4())
    to_encode.update({
        "exp": access_token_expires,
        "jti": jti,
    })
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
