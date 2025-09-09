import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException

from app.core.google_jwt import verify_google_id_token


class TestGoogleJWT:
    """Tests pour la vérification des tokens Google (logique métier)"""

    @pytest.mark.asyncio
    async def test_verify_google_id_token_success(self, monkeypatch):
        """Test la vérification réussie d'un token Google"""
        mock_token = "valid_token"
        mock_payload = {
            "sub": "12345",
            "email": "test@example.com",
            "name": "Test User"
        }
        mock_jwks = {"keys": [{"kid": "key1", "kty": "RSA"}]}

        # Mock du client HTTP persistant
        mock_google_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = mock_jwks
        mock_google_client.get.return_value = mock_response
        
        # Mock du cache (force cache miss pour tester le fetch)
        monkeypatch.setattr("app.core.google_jwt._jwks_cache", None)
        monkeypatch.setattr("app.core.google_jwt.google_client", mock_google_client)

        with patch('app.core.google_jwt.jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = mock_payload

            result = await verify_google_id_token(mock_token)

            assert result == mock_payload
            mock_google_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_google_id_token_cache_hit(self, monkeypatch):
        """Test que le cache JWK fonctionne (pas d'appel réseau)"""
        mock_token = "valid_token"
        mock_payload = {
            "sub": "12345",
            "email": "test@example.com", 
            "name": "Test User"
        }
        mock_jwks = {"keys": [{"kid": "key1", "kty": "RSA"}]}

        # Mock du cache (simuler cache hit)
        import time
        monkeypatch.setattr("app.core.google_jwt._jwks_cache", (mock_jwks, time.time()))
        
        # Mock du client (ne devrait PAS être appelé avec cache hit)
        mock_google_client = AsyncMock()
        monkeypatch.setattr("app.core.google_jwt.google_client", mock_google_client)

        with patch('app.core.google_jwt.jwt.decode') as mock_jwt_decode:
            mock_jwt_decode.return_value = mock_payload

            result = await verify_google_id_token(mock_token)

            assert result == mock_payload
            # Vérifier que le client n'a PAS été appelé (cache hit)
            mock_google_client.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_verify_google_id_token_fallback_refresh(self, monkeypatch):
        """Test du fallback avec refresh forcé du cache"""
        mock_token = "valid_token"
        mock_payload = {
            "sub": "12345",
            "email": "test@example.com",
            "name": "Test User"
        }
        mock_jwks = {"keys": [{"kid": "key1", "kty": "RSA"}]}

        # Mock du client HTTP persistant
        mock_google_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = mock_jwks
        mock_google_client.get.return_value = mock_response
        
        monkeypatch.setattr("app.core.google_jwt._jwks_cache", None)
        monkeypatch.setattr("app.core.google_jwt.google_client", mock_google_client)

        with patch('app.core.google_jwt.jwt.decode') as mock_jwt_decode:
            # Premier appel échoue, deuxième réussit (fallback)
            mock_jwt_decode.side_effect = [Exception("Invalid key"), mock_payload]

            result = await verify_google_id_token(mock_token)

            assert result == mock_payload
            # Vérifier que le client a été appelé 2 fois (cache + force refresh)
            assert mock_google_client.get.call_count == 2

    @pytest.mark.asyncio
    async def test_verify_google_id_token_complete_failure(self, monkeypatch):
        """Test de l'échec complet (même après fallback)"""
        mock_token = "invalid_token"
        mock_jwks = {"keys": [{"kid": "key1", "kty": "RSA"}]}

        # Mock du client HTTP persistant
        mock_google_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = mock_jwks
        mock_google_client.get.return_value = mock_response
        
        monkeypatch.setattr("app.core.google_jwt._jwks_cache", None)
        monkeypatch.setattr("app.core.google_jwt.google_client", mock_google_client)

        with patch('app.core.google_jwt.jwt.decode') as mock_jwt_decode:
            # Les deux tentatives échouent
            mock_jwt_decode.side_effect = Exception("Invalid token")

            with pytest.raises(HTTPException) as exc_info:
                await verify_google_id_token(mock_token)

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "id_token Google invalide"