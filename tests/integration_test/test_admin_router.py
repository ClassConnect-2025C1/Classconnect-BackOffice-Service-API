import pytest
import pytest_asyncio
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
    from httpx import ASGITransport

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
    from httpx import ASGITransport

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
