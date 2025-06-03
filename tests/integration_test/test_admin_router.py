import pytest
import pytest_asyncio
from httpx import ASGITransport
from httpx import AsyncClient
from datetime import datetime, timezone

from src.app.main import app
from src.app.db.db_client import get_db
from src.app.security.security import create_access_token, hash_password

from motor.motor_asyncio import AsyncIOMotorClient


MONGO_TEST_URI = "mongodb://localhost:27017"
TEST_DB_NAME = "test_backoffice_db"


@pytest_asyncio.fixture(scope="function")
async def override_db():
    client = AsyncIOMotorClient(MONGO_TEST_URI)
    db = client[TEST_DB_NAME]

    app.dependency_overrides[get_db] = lambda: db

    yield db

    # Cleanup (al terminar cada test)
    await db["admin"].delete_many({})
    await client.drop_database(TEST_DB_NAME)


@pytest.mark.asyncio
async def test_register_admin(override_db):

    # Setup: insertar un admin “creador”
    result = await override_db["admin"].insert_one(
        {
            "email": "creator@example.com",
            "hashed_password": "dummy",
            "signup_date": datetime.now(timezone.utc),
            "other_id": None,
        }
    )

    # Crear token válido para ese creador
    token = create_access_token(id=str(result.inserted_id), email="creator@example.com")

    # Ejecutar request

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/admin/register",
            json={
                "email": "newadmin@example.com",
                "password": "newpass123",
                "name": "New Admin",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    # Comprobaciones
    assert response.status_code == 200

    # Verificar en la base que fue insertado
    created = await override_db["admin"].find_one({"email": "newadmin@example.com"})
    assert created is not None
    assert created["email"] == "newadmin@example.com"
    assert created["other_id"] == str(result.inserted_id)


@pytest.mark.asyncio
async def test_login_admin_success(override_db):
    # Insertar admin con contraseña hasheada
    raw_password = "securepass123"
    await override_db["admin"].insert_one(
        {
            "email": "admin@example.com",
            "hashed_password": hash_password(raw_password),
            "signup_date": datetime.now(timezone.utc),
            "other_id": None,
        }
    )

    # Ejecutar request de login
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/admin/login",
            json={"email": "admin@example.com", "password": raw_password},
        )

    # Comprobaciones
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


"""
@pytest.mark.asyncio
async def test_block_user_logs_action(override_db):
    # Insert an admin and create token
    admin = await override_db["admin"].insert_one(
        {
            "email": "adminblock@example.com",
            "hashed_password": "dummy",
            "signup_date": datetime.now(timezone.utc),
            "other_id": None,
        }
    )
    token = create_access_token(
        id=str(admin.inserted_id), email="adminblock@example.com"
    )
    user_id = "user123"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.patch(
            f"/admin/block/{user_id}",
            json={"to_block": True},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    assert response.json()["message"] == "User blocked"
    # Check log entry
    log = await override_db["log"].find_one({"user_id": user_id, "action": "block"})
    assert log is not None
    assert log["user_id"] == user_id
    assert log["action"] == "block"
    assert "timestamp" in log


@pytest.mark.asyncio
async def test_block_user_logs_unblock_action(override_db):
    # Insert an admin and create token
    admin = await override_db["admin"].insert_one(
        {
            "email": "adminblock2@example.com",
            "hashed_password": "dummy",
            "signup_date": datetime.now(timezone.utc),
            "other_id": None,
        }
    )
    token = create_access_token(
        id=str(admin.inserted_id), email="adminblock2@example.com"
    )
    user_id = "user456"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.patch(
            f"/admin/block/{user_id}",
            json={"to_block": False},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    assert response.json()["message"] == "User unblocked"
    # Check log entry
    log = await override_db["log"].find_one({"user_id": user_id, "action": "unblock"})
    assert log is not None
    assert log["user_id"] == user_id
    assert log["action"] == "unblock"
    assert "timestamp" in log


@pytest.mark.asyncio
async def test_change_user_role_logs_action(override_db):
    # Insert an admin and create token
    admin = await override_db["admin"].insert_one(
        {
            "email": "adminrole@example.com",
            "hashed_password": "dummy",
            "signup_date": datetime.now(timezone.utc),
            "other_id": None,
        }
    )
    token = create_access_token(
        id=str(admin.inserted_id), email="adminrole@example.com"
    )
    user_id = "user789"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.patch(
            f"/admin/change_role/{user_id}",
            json={"rol": "teacher"},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    assert response.json()["message"] == "User role changed"
    # Check log entry
    log = await override_db["log"].find_one({"user_id": user_id, "action": "teacher"})
    assert log is not None
    assert log["user_id"] == user_id
    assert log["action"] == "teacher"
    assert "timestamp" in log


@pytest.mark.asyncio
async def test_change_user_role_invalid_role(override_db):
    # Insert an admin and create token
    admin = await override_db["admin"].insert_one(
        {
            "email": "adminrole2@example.com",
            "hashed_password": "dummy",
            "signup_date": datetime.now(timezone.utc),
            "other_id": None,
        }
    )
    token = create_access_token(
        id=str(admin.inserted_id), email="adminrole2@example.com"
    )
    user_id = "user999"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.patch(
            f"/admin/change_role/{user_id}",
            json={"rol": "invalidrole"},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 400
    assert "Invalid role provided" in response.json()["detail"]


@pytest.mark.asyncio
async def test_change_user_role_logs_student_action(override_db):
    # Insert an admin and create token
    admin = await override_db["admin"].insert_one(
        {
            "email": "adminrole3@example.com",
            "hashed_password": "dummy",
            "signup_date": datetime.now(timezone.utc),
            "other_id": None,
        }
    )
    token = create_access_token(
        id=str(admin.inserted_id), email="adminrole3@example.com"
    )
    user_id = "user1000"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.patch(
            f"/admin/change_role/{user_id}",
            json={"rol": "student"},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    assert response.json()["message"] == "User role changed"
    # Check log entry
    log = await override_db["log"].find_one({"user_id": user_id, "action": "student"})
    assert log is not None
    assert log["user_id"] == user_id
    assert log["action"] == "student"
    assert "timestamp" in log

"""
