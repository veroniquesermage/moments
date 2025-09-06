"""
Configuration spécifique aux tests d'intégration
"""
import pytest
import pytest_asyncio
from typing import AsyncGenerator

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.dependencies.current_user import get_current_user_from_cookie
from app.models import User


@pytest_asyncio.fixture(scope="session")
async def integration_test_engine():
    """Moteur de base de données dédié aux tests d'intégration"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def integration_db_session(integration_test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Session de base de données pour tests d'intégration"""
    AsyncSessionLocal = sessionmaker(
        bind=integration_test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            pass


@pytest.fixture
def integration_test_user() -> User:
    """Utilisateur de test pour l'intégration"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User(
        email=f"integration{unique_id}@example.com",
        prenom="Integration",
        nom="User",
        google_id=f"integration{unique_id}"
    )


@pytest.fixture
def test_client_with_auth(integration_db_session: AsyncSession, integration_test_user: User) -> TestClient:
    """Client de test FastAPI avec authentification mockée"""
    
    async def override_get_db():
        yield integration_db_session
    
    async def override_get_current_user():
        return integration_test_user
    
    # Override des dépendances
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_from_cookie] = override_get_current_user
    
    client = TestClient(app)
    
    yield client
    
    # Cleanup
    app.dependency_overrides.clear()