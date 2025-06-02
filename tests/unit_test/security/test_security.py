import pytest
from passlib.context import CryptContext

from src.app.exceptions.exceptions import GetDataFromTokenError
from src.app.entities.admin_entity import User
from jose import jwt
from src.app.security.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)


def test_hash_password_returns_hashed_string():
    password = "mysecretpassword"
    hashed = hash_password(password)
    assert isinstance(hashed, str)
    assert hashed != password
    assert (
        hashed.startswith("$2b$")
        or hashed.startswith("$2a$")
        or hashed.startswith("$2y$")
    )


def test_hash_password_different_hashes_for_same_password():
    password = "repeatpassword"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    assert hash1 != hash2


def test_verify_password_correct_and_incorrect():
    password = "testpassword"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token_contains_id_and_email():
    id = "123"
    email = "test@example.com"
    token = create_access_token(id, email)
    decoded = jwt.decode(token, "supersecret", algorithms=["HS256"])
    assert decoded["id"] == id
    assert decoded["email"] == email


def test_decode_token_returns_user_object():
    id = "456"
    email = "user@example.com"
    token = create_access_token(id, email)
    user = decode_token(token)
    assert isinstance(user, User)
    assert user.id == id
    assert user.email == email


def test_decode_token_raises_on_invalid_token():
    with pytest.raises(GetDataFromTokenError):
        decode_token("invalid.token.value")


def test_decode_token_raises_on_missing_fields(monkeypatch):
    # Create a token missing 'email'
    payload = {"id": "789"}
    token = jwt.encode(payload, "supersecret", algorithm="HS256")
    with pytest.raises(GetDataFromTokenError):
        decode_token(token)
    # Create a token missing 'id'
    payload = {"email": "missingid@example.com"}
    token = jwt.encode(payload, "supersecret", algorithm="HS256")
    with pytest.raises(GetDataFromTokenError):
        decode_token(token)
