"""
Configuration pour tests d'intégration avec authentification mockée
"""
import pytest
import pytest_asyncio
import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.dependencies.current_user import get_current_user_from_cookie, get_current_user_from_cookie_with_tiers, get_current_group_id
from unittest.mock import patch
from app.models import User, Group, UserGroup
from app.core.enum import RoleEnum


# Session globale pour les tests
test_db_session = None


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
    global test_db_session
    
    AsyncSessionLocal = sessionmaker(
        bind=integration_test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with AsyncSessionLocal() as session:
        test_db_session = session  # Stocker globalement pour les overrides
        yield session
        test_db_session = None


def get_test_db():
    """Override pour get_db qui retourne la session de test"""
    global test_db_session
    if test_db_session:
        yield test_db_session
    else:
        raise RuntimeError("No test database session available")


@pytest_asyncio.fixture
async def test_user(integration_db_session: AsyncSession):
    """Créer un utilisateur de test"""
    test_uuid = str(uuid.uuid4())[:8]
    
    user = User(
        email=f"test-user-{test_uuid}@example.com",
        prenom="Test",
        nom="User",
        google_id=f"test-{test_uuid}",
        is_compte_tiers=False
    )
    integration_db_session.add(user)
    await integration_db_session.commit()
    await integration_db_session.refresh(user)
    
    return user


@pytest_asyncio.fixture
async def test_admin_user(integration_db_session: AsyncSession):
    """Créer un utilisateur admin de test"""
    test_uuid = str(uuid.uuid4())[:8]
    
    user = User(
        email=f"admin-user-{test_uuid}@example.com",
        prenom="Admin",
        nom="User",
        google_id=f"admin-{test_uuid}",
        is_compte_tiers=False
    )
    integration_db_session.add(user)
    await integration_db_session.commit()
    await integration_db_session.refresh(user)
    
    return user


@pytest_asyncio.fixture
async def test_group(integration_db_session: AsyncSession, test_admin_user: User):
    """Créer un groupe de test avec un admin"""
    test_uuid = str(uuid.uuid4())[:8]
    
    group = Group(
        nom_groupe=f"Test Group {test_uuid}",
        description=f"Group for integration tests {test_uuid}",
        code=f"CODE{test_uuid.upper()}"
    )
    integration_db_session.add(group)
    await integration_db_session.commit()
    await integration_db_session.refresh(group)
    
    # Ajouter l'admin au groupe
    user_group = UserGroup(
        utilisateur_id=test_admin_user.id,
        groupe_id=group.id,
        role=RoleEnum.ADMIN
    )
    integration_db_session.add(user_group)
    await integration_db_session.commit()
    
    return group


@pytest_asyncio.fixture
async def test_user_and_group(integration_db_session: AsyncSession, test_user: User, test_group: Group):
    """Ajouter un utilisateur normal au groupe de test"""
    user_group = UserGroup(
        utilisateur_id=test_user.id,
        groupe_id=test_group.id,
        role=RoleEnum.MEMBRE
    )
    integration_db_session.add(user_group)
    await integration_db_session.commit()
    
    return test_user, test_group


class IntegratedTestClient:
    """Client de test avec authentification et base de données intégrées"""
    
    def __init__(self, user: User, group: Group = None):
        self.user = user
        self.group = group
        self.client = None
        self._original_overrides = {}
        self._setup_client()
    
    def _setup_client(self):
        """Configure le client avec tous les mocks nécessaires"""
        # Sauvegarder les overrides existants
        self._original_overrides = app.dependency_overrides.copy()
        
        # Mock functions - doit correspondre exactement aux signatures des fonctions originales
        def mock_get_current_user():
            return self.user
            
        def mock_get_group_id():
            return self.group.id if self.group else 1
            
        # Override des dépendances
        app.dependency_overrides[get_db] = get_test_db
        app.dependency_overrides[get_current_user_from_cookie] = mock_get_current_user
        app.dependency_overrides[get_current_user_from_cookie_with_tiers()] = mock_get_current_user
        app.dependency_overrides[get_current_group_id] = mock_get_group_id
        
        self.client = TestClient(app)
    
    
    def get(self, url: str, **kwargs):
        """GET avec authentification"""
        headers = kwargs.get('headers', {})
        if self.group:
            headers['X-Group-Id'] = str(self.group.id)
        kwargs['headers'] = headers
        return self.client.get(url, **kwargs)
    
    def post(self, url: str, **kwargs):
        """POST avec authentification"""
        headers = kwargs.get('headers', {})
        if self.group:
            headers['X-Group-Id'] = str(self.group.id)
        headers['Content-Type'] = 'application/json'
        kwargs['headers'] = headers
        return self.client.post(url, **kwargs)
    
    def put(self, url: str, **kwargs):
        """PUT avec authentification"""
        headers = kwargs.get('headers', {})
        if self.group:
            headers['X-Group-Id'] = str(self.group.id)
        headers['Content-Type'] = 'application/json'
        kwargs['headers'] = headers
        return self.client.put(url, **kwargs)
    
    def patch(self, url: str, **kwargs):
        """PATCH avec authentification"""
        headers = kwargs.get('headers', {})
        if self.group:
            headers['X-Group-Id'] = str(self.group.id)
        headers['Content-Type'] = 'application/json'
        kwargs['headers'] = headers
        return self.client.patch(url, **kwargs)
    
    def delete(self, url: str, **kwargs):
        """DELETE avec authentification"""
        headers = kwargs.get('headers', {})
        if self.group:
            headers['X-Group-Id'] = str(self.group.id)
        kwargs['headers'] = headers
        return self.client.delete(url, **kwargs)
    
    def cleanup(self):
        """Restaure les overrides originaux"""
        app.dependency_overrides.clear()
        app.dependency_overrides.update(self._original_overrides)


@pytest.fixture
def auth_client():
    """Factory pour créer des clients authentifiés"""
    created_clients = []
    
    def _create_client(user: User, group: Group = None) -> IntegratedTestClient:
        client = IntegratedTestClient(user, group)
        created_clients.append(client)
        return client
    
    yield _create_client
    
    # Cleanup après le test
    for client in created_clients:
        client.cleanup()


@pytest.fixture
def admin_client(auth_client, test_admin_user: User, test_group: Group) -> IntegratedTestClient:
    """Client authentifié en tant qu'admin du groupe"""
    return auth_client(test_admin_user, test_group)


@pytest.fixture
def member_client(auth_client, test_user: User, test_group: Group) -> IntegratedTestClient:
    """Client authentifié en tant que membre du groupe"""
    return auth_client(test_user, test_group)


@pytest.fixture
def unauthenticated_client():
    """Client sans authentification pour tester les erreurs 401"""
    app.dependency_overrides.clear()
    return TestClient(app)


# Pour compatibilité avec l'ancien système
@pytest.fixture
def integration_test_user() -> User:
    """Utilisateur de test pour l'intégration (pour compatibilité)"""
    unique_id = str(uuid.uuid4())[:8]
    return User(
        email=f"integration{unique_id}@example.com",
        prenom="Integration",
        nom="User",
        google_id=f"integration{unique_id}"
    )


@pytest.fixture
def test_client_with_auth(integration_db_session: AsyncSession, integration_test_user: User) -> TestClient:
    """Client de test FastAPI avec authentification mockée (pour compatibilité)"""
    
    def override_get_current_user():
        return integration_test_user
    
    app.dependency_overrides[get_db] = lambda: integration_db_session
    app.dependency_overrides[get_current_user_from_cookie] = override_get_current_user
    
    client = TestClient(app)
    
    yield client
    
    app.dependency_overrides.clear()