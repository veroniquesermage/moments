import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.models import User


@pytest.fixture
def auth_client():
    """Client avec authentification mockée"""
    
    def _create_client_for_user(user: User):
        client = TestClient(app)
        
        # Mock la dépendance current_user pour retourner notre utilisateur de test
        with patch('app.dependencies.auth.current_user') as mock_current_user:
            mock_current_user.return_value = user
            
            # Ajouter headers d'authentification fictifs
            client.headers = {"Authorization": f"Bearer mock_token_{user.id}"}
            
            return client
    
    return _create_client_for_user


@pytest.fixture
def mock_auth_dependency():
    """Mock global pour les dépendances d'authentification"""
    
    def _mock_for_user(user: User):
        return patch('app.dependencies.auth.current_user', return_value=user)
    
    return _mock_for_user