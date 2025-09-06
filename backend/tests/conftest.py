"""
Configuration globale pour les tests - Fixtures communes réutilisables
"""
import os
import sys
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from uuid import uuid4

# Configuration des variables d'environnement avant tout import
os.environ.update({
    'GOOGLE_CLIENT_ID': 'test',
    'GOOGLE_CLIENT_SECRET': 'test',
    'GOOGLE_REDIRECT_URI': 'http://localhost',
    'GOOGLE_TOKEN_ENDPOINT': 'http://localhost/token',
    'JWK_URI': 'http://localhost/jwk',
    'JWT_SECRET': 'secret',
    'DATABASE_URL': 'sqlite+aiosqlite:///:memory:',
    'SYNC_DB_URL': 'sqlite:///:memory:',
    'CHECK_MAIL': 'http://localhost/check_mail',
    'RESET_PASSWORD': 'http://localhost/reset-password?token=',
    'MAILJET_API_KEY': 'test',
    'MAILJET_SECRET': 'test'
})

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Imports après configuration des variables d'environnement
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models import User, Gift, GiftIdeas, Group, UserGroup
from app.core.enum import GiftStatusEnum, RoleUtilisateur
from app.dependencies.current_user import get_current_user_from_cookie


@pytest.fixture(scope="session")
def event_loop():
    """Fixture pour créer un event loop pour toute la session de tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Fixture pour créer un moteur de base de données de test"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Créer toutes les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Fixture pour créer une session de base de données isolée pour chaque test"""
    AsyncSessionLocal = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            # Pas de rollback explicite, la session sera fermée automatiquement
            pass


@pytest.fixture
def test_user() -> User:
    """Fixture pour créer un utilisateur de test standard"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User(
        email=f"test{unique_id}@example.com",
        prenom="Test",
        nom="User",
        google_id=f"test{unique_id}"
    )


@pytest.fixture
def test_user_2() -> User:
    """Fixture pour créer un second utilisateur de test"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User(
        email=f"test2{unique_id}@example.com",
        prenom="Test2",
        nom="User2",
        google_id=f"test2{unique_id}"
    )


@pytest_asyncio.fixture
async def persisted_test_user(db_session: AsyncSession, test_user: User) -> User:
    """Fixture pour créer un utilisateur persisté en base"""
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)
    return test_user


@pytest_asyncio.fixture
async def persisted_test_user_2(db_session: AsyncSession, test_user_2: User) -> User:
    """Fixture pour créer un second utilisateur persisté en base"""
    db_session.add(test_user_2)
    await db_session.commit()
    await db_session.refresh(test_user_2)
    return test_user_2


@pytest.fixture
def test_group() -> Group:
    """Fixture pour créer un groupe de test"""
    return Group(
        id=1,
        nom="Groupe Test",
        description="Description du groupe test",
        code_invitation=str(uuid4())[:8],
        createur_id=1
    )


@pytest_asyncio.fixture
async def persisted_test_group(db_session: AsyncSession, test_group: Group, persisted_test_user: User) -> Group:
    """Fixture pour créer un groupe persisté avec relation utilisateur"""
    db_session.add(test_group)
    await db_session.commit()
    await db_session.refresh(test_group)
    
    # Ajouter la relation utilisateur-groupe
    user_group = UserGroup(
        utilisateur_id=persisted_test_user.id,
        groupe_id=test_group.id,
        role=RoleUtilisateur.ADMIN
    )
    db_session.add(user_group)
    await db_session.commit()
    
    return test_group


@pytest.fixture
def test_gift_data() -> dict:
    """Fixture pour les données de cadeau de test"""
    return {
        "nom": "Cadeau Test",
        "description": "Description du cadeau test",
        "prix": 50.0,
        "destinataire_id": 1,
        "priorite": 1
    }


@pytest.fixture
def test_gift() -> Gift:
    """Fixture pour créer un cadeau de test"""
    return Gift(
        nom="Cadeau Test",
        description="Description test",
        prix=50.0,
        statut=GiftStatusEnum.DISPONIBLE,
        priorite=1
    )


@pytest_asyncio.fixture
async def persisted_test_gift(db_session: AsyncSession, test_gift: Gift, persisted_test_user: User) -> Gift:
    """Fixture pour créer un cadeau persisté en base"""
    test_gift.destinataire_id = persisted_test_user.id
    db_session.add(test_gift)
    await db_session.commit()
    await db_session.refresh(test_gift)
    return test_gift


@pytest.fixture
def test_gift_idea() -> GiftIdeas:
    """Fixture pour créer une idée de cadeau"""
    return GiftIdeas()


@pytest_asyncio.fixture
async def persisted_test_gift_idea(db_session: AsyncSession, test_gift_idea: GiftIdeas, persisted_test_user_2: User) -> GiftIdeas:
    """Fixture pour créer une idée de cadeau persistée"""
    test_gift_idea.proposee_par_id = persisted_test_user_2.id
    db_session.add(test_gift_idea)
    await db_session.commit()
    await db_session.refresh(test_gift_idea)
    return test_gift_idea


@pytest_asyncio.fixture
async def test_gift_with_idea(
    db_session: AsyncSession, 
    persisted_test_user: User, 
    persisted_test_gift_idea: GiftIdeas
) -> Gift:
    """Fixture pour créer un cadeau basé sur une idée"""
    gift = Gift(
        nom="Cadeau depuis idée",
        description="Description cadeau depuis idée",
        destinataire_id=persisted_test_user.id,
        gift_idea_id=persisted_test_gift_idea.id,
        statut=GiftStatusEnum.DISPONIBLE,
        priorite=1
    )
    db_session.add(gift)
    await db_session.commit()
    await db_session.refresh(gift)
    return gift


@pytest.fixture
def test_client(db_session: AsyncSession, test_user: User) -> TestClient:
    """Fixture pour créer un client de test FastAPI avec dépendances mockées"""
    
    async def override_get_db():
        yield db_session
    
    async def override_get_current_user():
        return test_user
    
    # Override des dépendances
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_from_cookie] = override_get_current_user
    
    client = TestClient(app)
    
    yield client
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def mock_trace_service(monkeypatch):
    """Mock pour le TraceService pour éviter les logs durant les tests"""
    async def mock_record_trace(*args, **kwargs):
        pass
    
    monkeypatch.setattr("app.services.trace_service.TraceService.record_trace", mock_record_trace)


@pytest.fixture
def mock_mail_service(monkeypatch):
    """Mock pour le MailService pour éviter l'envoi d'emails durant les tests"""
    async def mock_send_mail(*args, **kwargs):
        return {"success": True}
    
    # Mock la méthode existante dans le MailService
    try:
        monkeypatch.setattr("app.services.mailing.mail_service.MailService.send_mail", mock_send_mail)
    except AttributeError:
        # Si la méthode n'existe pas, on ignore
        pass


# Helper functions pour les tests
@pytest.fixture
def assert_gift_basic_properties():
    """Helper pour valider les propriétés de base d'un cadeau"""
    def _assert(gift, expected_name: str, expected_user_id: int):
        # Si c'est un GiftResponse (Pydantic), utiliser destinataire.id
        if hasattr(gift, 'destinataire') and hasattr(gift.destinataire, 'id'):
            user_id = gift.destinataire.id
            # GiftResponse n'a pas de statut, on vérifie juste les autres propriétés
            assert gift.nom == expected_name
            assert user_id == expected_user_id
            assert gift.priorite is not None
        # Si c'est un Gift model (SQLAlchemy), utiliser destinataire_id
        elif hasattr(gift, 'destinataire_id'):
            user_id = gift.destinataire_id
            assert gift.nom == expected_name
            assert user_id == expected_user_id
            assert gift.statut == GiftStatusEnum.DISPONIBLE
            assert gift.priorite is not None
        else:
            raise AssertionError(f"Cannot determine user ID from gift object: {type(gift)}")
    
    return _assert


# Configuration pytest spécifique
def pytest_configure(config):
    """Configuration spécifique pour les tests"""
    config.addinivalue_line("markers", "integration: marque les tests d'intégration")
    config.addinivalue_line("markers", "unit: marque les tests unitaires")
    config.addinivalue_line("markers", "slow: marque les tests lents")