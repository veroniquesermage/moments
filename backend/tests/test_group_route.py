import os
import sys
import asyncio

# Configuration for Settings before any app import
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
from app.dependencies.current_user import get_current_user
from app.models import User

# Create an isolated in-memory database for the tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    TEST_DATABASE_URL,
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

async def override_get_current_user():
    return User(id=1, email="user@example.com", prenom="Test", nom="User", google_id="1")

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


def test_get_group_not_found():
    response = client.get("/groupe/999")
    assert response.status_code == 404
