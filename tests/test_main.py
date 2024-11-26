import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import User
from app import crud

# Создаем тестовую базу данных
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(TEST_DATABASE_URL, echo=True, future=True)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_user():
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data


@pytest.mark.asyncio
async def test_login():
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_create_task():
    # Сначала войдем в систему
    login_response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    access_token = login_response.json()["access_token"]

    # Теперь создадим задачу
    response = client.post(
        "/tasks",
        json={"title": "Test Task", "description": "This is a test task", "status": "todo"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test task"
    assert data["status"] == "todo"


@pytest.mark.asyncio
async def test_get_tasks():
    # Войдем в систему
    login_response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    access_token = login_response.json()["access_token"]

    # Получим список задач
    response = client.get(
        "/tasks",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
