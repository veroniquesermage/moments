"""
Fixtures spécialisées pour les cadeaux
"""
import pytest
import pytest_asyncio
from uuid import uuid4

from app.models import Gift, GiftIdeas, User
from app.core.enum import GiftStatusEnum
from app.schemas.gift.gift_create import GiftCreate


@pytest.fixture
def gift_create_data() -> dict:
    """Données de base pour créer un cadeau"""
    return {
        "nom": "Cadeau Test",
        "description": "Description du cadeau test",
        "prix": 50.0,
        "priorite": 1
    }


@pytest.fixture
def gift_factory():
    """Factory pour créer des cadeaux avec des données variées"""
    def _create_gift(**overrides) -> Gift:
        defaults = {
            "nom": f"Cadeau {uuid4().hex[:8]}",
            "description": "Description par défaut",
            "prix": 25.0,
            "statut": GiftStatusEnum.DISPONIBLE,
            "priorite": 1
        }
        defaults.update(overrides)
        return Gift(**defaults)
    
    return _create_gift


@pytest.fixture
def gift_idea_factory():
    """Factory pour créer des idées de cadeaux"""
    def _create_gift_idea(**overrides) -> GiftIdeas:
        defaults = {
            "visibilite": False
        }
        defaults.update(overrides)
        return GiftIdeas(**defaults)
    
    return _create_gift_idea


@pytest_asyncio.fixture
async def sample_gifts(unit_db_session, persisted_test_user):
    """Créer plusieurs cadeaux échantillons pour les tests"""
    gifts = [
        Gift(
            nom="Livre Python",
            description="Livre sur Python avancé",
            prix=30.0,
            destinataire_id=persisted_test_user.id,
            statut=GiftStatusEnum.DISPONIBLE,
            priorite=1
        ),
        Gift(
            nom="Clavier mécanique",
            description="Clavier pour développeur",
            prix=120.0,
            destinataire_id=persisted_test_user.id,
            statut=GiftStatusEnum.RESERVE,
            priorite=2
        )
    ]
    
    for gift in gifts:
        unit_db_session.add(gift)
    
    await unit_db_session.commit()
    
    for gift in gifts:
        await unit_db_session.refresh(gift)
    
    return gifts