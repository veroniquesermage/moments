import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.auth.google_auth_service import exchange_code_for_tokens


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_code_for_tokens_success(monkeypatch):
    """Test l'échange réussi de code OAuth contre tokens"""
    # Mock de la réponse Google
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id_token": "xyz", "access_token": "abc"}
    mock_response.content = b'{"id_token": "xyz", "access_token": "abc"}'
    
    # Mock du client HTTP persistant
    mock_google_client = AsyncMock()
    mock_google_client.post.return_value = mock_response
    
    # Remplace google_client par le mock
    monkeypatch.setattr("app.services.auth.google_auth_service.google_client", mock_google_client)
    
    tokens = await exchange_code_for_tokens("code", "verifier")
    
    assert tokens["id_token"] == "xyz"
    assert tokens["access_token"] == "abc"
    mock_google_client.post.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exchange_code_for_tokens_failure(monkeypatch):
    """Test l'échec de l'échange OAuth (erreur Google)"""
    # Mock de la réponse d'erreur Google
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.content = b'{"error": "invalid_grant"}'
    
    # Mock du client HTTP persistant
    mock_google_client = AsyncMock()
    mock_google_client.post.return_value = mock_response
    
    # Remplace google_client par le mock
    monkeypatch.setattr("app.services.auth.google_auth_service.google_client", mock_google_client)
    
    with pytest.raises(Exception):
        await exchange_code_for_tokens("code", "verifier")
    
    mock_google_client.post.assert_called_once()

