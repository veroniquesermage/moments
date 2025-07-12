import os
import sys
import asyncio

os.environ['GOOGLE_CLIENT_ID'] = 'test'
os.environ['GOOGLE_CLIENT_SECRET'] = 'test'
os.environ['GOOGLE_REDIRECT_URI'] = 'http://localhost'
os.environ['GOOGLE_TOKEN_ENDPOINT'] = 'http://localhost/token'
os.environ['JWK_URI'] = 'http://localhost/jwk'
os.environ['JWT_SECRET'] = 'secret'
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///:memory:'
os.environ['SYNC_DB_URL'] = 'sqlite:///:memory:'

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

engine = create_async_engine(
    os.environ['DATABASE_URL'],
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_models())

async def override_get_db():
    async with AsyncSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_check_user_not_found():
    response = client.post('/api/auth/check-user', json={'email': 'a@b.com', 'isGoogleLogin': False})
    assert response.status_code == 404


def test_register_and_login():
    reg_payload = {
        'prenom': 'John',
        'nom': 'Doe',
        'email': 'john@example.com',
        'password': 'secret',
        'rememberMe': True,
    }
    response = client.post('/api/auth/register', json=reg_payload)
    assert response.status_code == 201

    bad = client.post('/api/auth/login', json={'email': 'john@example.com', 'password': 'wrong', 'rememberMe': False})
    assert bad.status_code == 401

    good = client.post('/api/auth/login', json={'email': 'john@example.com', 'password': 'secret', 'rememberMe': True})
    assert good.status_code == 200

