"""
Utilitaires de test réutilisables
"""
from typing import Any, Dict, List
from app.core.enum import GiftStatusEnum
from app.models import Gift


def assert_gift_properties(gift: Any, expected_name: str, expected_user_id: int) -> None:
    """Helper pour valider les propriétés de base d'un cadeau"""
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


def assert_http_error(exception_info, expected_status: int, expected_message: str = None) -> None:
    """Helper pour valider les erreurs HTTP"""
    assert exception_info.value.status_code == expected_status
    if expected_message:
        assert expected_message in str(exception_info.value.detail)


def count_gifts_by_status(gifts: List[Gift]) -> Dict[GiftStatusEnum, int]:
    """Compter les cadeaux par statut"""
    counts = {}
    for gift in gifts:
        status = gift.statut
        counts[status] = counts.get(status, 0) + 1
    return counts


def create_gift_update_data(gift_id: int, user_id: int, **overrides) -> dict:
    """Helper pour créer des données GiftUpdate valides"""
    defaults = {
        "id": gift_id,
        "destinataire_id": user_id,
        "nom": "Nom par défaut",
        "priorite": 1
    }
    defaults.update(overrides)
    return defaults


class TestDataBuilder:
    """Builder pour créer des données de test complexes"""
    
    def __init__(self):
        self.data = {}
    
    def with_gift_data(self, **kwargs) -> 'TestDataBuilder':
        gift_defaults = {
            "nom": "Cadeau Test",
            "description": "Description test",
            "prix": 50.0,
            "priorite": 1
        }
        gift_defaults.update(kwargs)
        self.data['gift'] = gift_defaults
        return self
    
    def with_user_data(self, **kwargs) -> 'TestDataBuilder':
        from uuid import uuid4
        unique_id = str(uuid4())[:8]
        user_defaults = {
            "email": f"test{unique_id}@example.com",
            "prenom": "Test",
            "nom": "User",
            "google_id": f"test{unique_id}"
        }
        user_defaults.update(kwargs)
        self.data['user'] = user_defaults
        return self
    
    def build(self) -> dict:
        return self.data.copy()


def mock_service_method(service_class: type, method_name: str, return_value: Any = None):
    """Decorator pour mocker facilement une méthode de service"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            original_method = getattr(service_class, method_name)
            
            async def mock_method(*method_args, **method_kwargs):
                return return_value
            
            setattr(service_class, method_name, mock_method)
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                setattr(service_class, method_name, original_method)
        
        return wrapper
    return decorator