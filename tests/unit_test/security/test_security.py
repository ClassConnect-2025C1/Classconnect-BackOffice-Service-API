import pytest
from passlib.context import CryptContext
from src.app.security.security import hash_password


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
