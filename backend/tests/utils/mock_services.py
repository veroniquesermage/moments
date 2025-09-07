"""
Services mockés pour les tests
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Any, Dict


@pytest.fixture
def mock_trace_service(monkeypatch):
    """Mock pour le TraceService"""
    async def mock_record_trace(*args, **kwargs):
        return {"success": True}
    
    monkeypatch.setattr("app.services.trace_service.TraceService.record_trace", mock_record_trace)
    return mock_record_trace


@pytest.fixture
def mock_mail_service(monkeypatch):
    """Mock pour le MailService"""
    async def mock_send_mail(*args, **kwargs):
        return {"success": True, "message_id": "test_123"}
    
    try:
        monkeypatch.setattr("app.services.mailing.mail_service.MailService.send_mail", mock_send_mail)
    except AttributeError:
        pass  # Service may not have this method
    
    return mock_send_mail


@pytest.fixture
def mock_google_oauth(monkeypatch):
    """Mock pour l'authentification Google OAuth"""
    mock_user_info = {
        "id": "google_test_123",
        "email": "test@example.com",
        "given_name": "Test",
        "family_name": "User",
        "picture": "https://example.com/avatar.jpg"
    }
    
    async def mock_get_user_info(*args, **kwargs):
        return mock_user_info
    
    monkeypatch.setattr("app.core.google_auth.get_user_info", mock_get_user_info)
    return mock_user_info


class MockAsyncSession:
    """Mock pour AsyncSession avec les méthodes principales"""
    
    def __init__(self):
        self.execute = AsyncMock()
        self.commit = AsyncMock()
        self.rollback = AsyncMock()
        self.refresh = AsyncMock()
        self.add = MagicMock()
        self.delete = AsyncMock()
        self.close = AsyncMock()
        self._objects = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    def add_mock_result(self, query_result):
        """Ajouter un résultat mocké pour les requêtes"""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = query_result
        mock_result.scalars.return_value.first.return_value = query_result[0] if query_result else None
        self.execute.return_value = mock_result


@pytest.fixture
def mock_db_session():
    """Fixture pour une session de base de données mockée"""
    return MockAsyncSession()


class ServiceMocker:
    """Classe utilitaire pour mocker facilement les services"""
    
    def __init__(self, monkeypatch):
        self.monkeypatch = monkeypatch
        self.mocked_methods = {}
    
    def mock_service_method(self, service_path: str, method_name: str, return_value: Any = None, side_effect: Any = None):
        """Mock une méthode de service"""
        full_path = f"{service_path}.{method_name}"
        
        if side_effect:
            mock_method = AsyncMock(side_effect=side_effect)
        else:
            mock_method = AsyncMock(return_value=return_value)
        
        self.monkeypatch.setattr(full_path, mock_method)
        self.mocked_methods[full_path] = mock_method
        
        return mock_method
    
    def get_mock(self, service_path: str, method_name: str):
        """Récupérer un mock existant"""
        full_path = f"{service_path}.{method_name}"
        return self.mocked_methods.get(full_path)
    
    def assert_called_once(self, service_path: str, method_name: str):
        """Vérifier qu'une méthode mockée a été appelée une fois"""
        mock = self.get_mock(service_path, method_name)
        if mock:
            mock.assert_called_once()
    
    def assert_called_with(self, service_path: str, method_name: str, *args, **kwargs):
        """Vérifier qu'une méthode mockée a été appelée avec des arguments spécifiques"""
        mock = self.get_mock(service_path, method_name)
        if mock:
            mock.assert_called_with(*args, **kwargs)


@pytest.fixture
def service_mocker(monkeypatch):
    """Fixture pour ServiceMocker"""
    return ServiceMocker(monkeypatch)