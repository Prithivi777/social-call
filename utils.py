from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days

SECRET_KEY = 'a5af35141ce9a73cf06aa495514d714a102246f676a261333f66e5aef9fa9749'
REFRESH_KEY = '5efbac0b298ebd9984756e57ac3f22f3a4b4e1b788425fd3a452a107f9184133'
ALGORITHM = 'HS256'

def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, REFRESH_KEY, ALGORITHM)
    return encoded_jwt


def decode_token(token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise RequiresLoginException()
        except jwt.JWTError as e:
            raise RequiresLoginException()
        except Exception as e:
            raise RequiresLoginException()

class RequiresLoginException(Exception):
    pass