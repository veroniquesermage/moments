import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException

from app.core.google_jwt import verify_google_id_token


class TestGoogleJWT:
    """Tests pour la vérification des tokens Google (logique métier)"""

    @pytest.mark.asyncio
    async def test_verify_google_id_token_success(self):
        """Test la vérification réussie d'un token Google"""
        mock_token = "valid_token"
        mock_payload = {
            "sub": "12345",
            "email": "test@example.com",
            "name": "Test User"
        }
        mock_jwks = {"keys": [{"kid": "key1", "kty": "RSA"}]}

        with patch('httpx.AsyncClient') as mock_client_class, \
             patch('app.core.google_jwt.jwt.decode') as mock_jwt_decode:
            
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = mock_jwks
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_jwt_decode.return_value = mock_payload

            result = await verify_google_id_token(mock_token)

            assert result == mock_payload

    @pytest.mark.asyncio
    async def test_verify_google_id_token_invalid_token_returns_401(self):
        """Test qu'un token invalide retourne une HTTPException 401"""
        mock_token = "invalid_token"
        mock_jwks = {"keys": [{"kid": "key1", "kty": "RSA"}]}

        with patch('httpx.AsyncClient') as mock_client_class, \
             patch('app.core.google_jwt.jwt.decode') as mock_jwt_decode:
            
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = mock_jwks
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_jwt_decode.side_effect = Exception("Invalid token")

            with pytest.raises(HTTPException) as exc_info:
                await verify_google_id_token(mock_token)

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "id_token Google invalide"

    @pytest.mark.asyncio
    async def test_verify_google_id_token_network_error_returns_401(self):
        """Test qu'une erreur réseau retourne HTTPException 401"""
        mock_token = "valid_token"

        with patch('httpx.AsyncClient') as mock_client_class, \
             patch('app.core.google_jwt.jwt.decode') as mock_jwt_decode:
            
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = {"keys": []}
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_jwt_decode.side_effect = Exception("Network error")

            with pytest.raises(HTTPException) as exc_info:
                await verify_google_id_token(mock_token)

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "id_token Google invalide"