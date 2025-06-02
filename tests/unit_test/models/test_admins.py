import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
from bson import ObjectId
from src.app.models.admin_model import Admin


def test_admin_creation_with_valid_data():
    oid = ObjectId()
    other_oid = ObjectId()
    email = "admin@example.com"
    hashed_password = "hashed_password"
    admin = Admin(
        _id=oid, email=email, hashed_password=hashed_password, other_id=other_oid
    )
    assert admin.id == oid
    assert admin.email == email
    assert admin.hashed_password == hashed_password
    assert admin.other_id == other_oid
    assert isinstance(admin.signup_date, datetime)
    assert admin.signup_date.tzinfo == timezone.utc


def test_admin_creation_without_other_id():
    oid = ObjectId()
    email = "admin2@example.com"
    hashed_password = "hashed_password2"
    admin = Admin(_id=oid, email=email, hashed_password=hashed_password)
    assert admin.other_id is None


def test_admin_invalid_email():
    oid = ObjectId()
    email = "not-an-email"
    hashed_password = "hashed_password"
    with pytest.raises(ValidationError):
        Admin(_id=oid, email=email, hashed_password=hashed_password)


def test_admin_json_encoder_for_objectid():
    oid = ObjectId()
    email = "admin@example.com"
    hashed_password = "hashed_password"
    admin = Admin(_id=oid, email=email, hashed_password=hashed_password)
    admin_json = admin.model_dump_json(by_alias=True)
    assert str(oid) in admin_json
