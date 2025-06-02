from passlib.context import CryptContext
import os
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from src.app.exceptions.exceptions import GetDataFromTokenError
from src.app.entities.admin_entity import User

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(id: str, email: str) -> str:
    to_encode = {"id": id, "email": email}

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("id")
        email = payload.get("email")
        if id is None or email is None:
            raise GetDataFromTokenError()
        return User(id=str(id), email=str(email))
    except JWTError:
        raise GetDataFromTokenError()
