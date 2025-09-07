"""
Configuration spécifique aux tests d'intégration
"""
import pytest
import pytest_asyncio
from typing import AsyncGenerator

from fastapi.testclient import TestClient
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.dependencies.current_user import get_current_user_from_cookie, get_current_user_from_cookie_with_tiers, get_current_group_id
from app.models import User, Group, UserGroup
from app.core.enum import RoleEnum


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


class AuthenticatedTestClient:
    """Client de test avec authentification avancée mockée"""
    
    def __init__(self, user: User, group: Group = None):
        self.user = user
        self.group = group
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """Configure le client avec l'authentification mockée"""
        
        def get_mock_user_func():
            """Fonction qui retourne une fonction FastAPI Depends"""
            def get_mock_user():
                return self.user
            return Depends(get_mock_user)
            
        def get_mock_group_id_func():
            return self.group.id if self.group else 1
        
        # Override database dependency to use integration database
        from app.database import get_db
        async def override_get_db():
            # Nous devons utiliser la session de base de données des tests
            yield integration_db_session

        # Override des dépendances FastAPI pour les tests
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user_from_cookie_with_tiers] = get_mock_user_func
        app.dependency_overrides[get_current_user_from_cookie] = lambda: self.user
        
        if self.group:
            app.dependency_overrides[get_current_group_id] = get_mock_group_id_func
        
        self.client = TestClient(app)
        
        # Ajouter des headers pour simuler l'authentification
        self.client.cookies = {"access_token": f"mock_token_for_user_{self.user.id}"}
    
    def cleanup(self):
        """Nettoie les overrides de dépendances"""
        if get_current_user_from_cookie in app.dependency_overrides:
            del app.dependency_overrides[get_current_user_from_cookie]
        if get_current_user_from_cookie_with_tiers in app.dependency_overrides:
            del app.dependency_overrides[get_current_user_from_cookie_with_tiers]
        if get_current_group_id in app.dependency_overrides:
            del app.dependency_overrides[get_current_group_id]


@pytest_asyncio.fixture
async def test_user(integration_db_session: AsyncSession):
    """Créer un utilisateur de test"""
    import uuid
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
    import uuid
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
    import uuid
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


@pytest.fixture
def auth_client():
    """Factory pour créer des clients authentifiés"""
    created_clients = []
    
    def _create_client(user: User, group: Group = None) -> AuthenticatedTestClient:
        client = AuthenticatedTestClient(user, group)
        created_clients.append(client)
        return client
    
    yield _create_client
    
    # Cleanup après le test
    for client in created_clients:
        client.cleanup()


@pytest.fixture
def admin_client(auth_client, test_admin_user: User, test_group: Group) -> AuthenticatedTestClient:
    """Client authentifié en tant qu'admin du groupe"""
    return auth_client(test_admin_user, test_group)


@pytest.fixture
def member_client(auth_client, test_user: User, test_group: Group) -> AuthenticatedTestClient:
    """Client authentifié en tant que membre du groupe"""
    return auth_client(test_user, test_group)


@pytest.fixture
def unauthenticated_client():
    """Client sans authentification pour tester les erreurs 401"""
    # S'assurer qu'aucune dépendance n'est overridée
    app.dependency_overrides.clear()
    return TestClient(app)