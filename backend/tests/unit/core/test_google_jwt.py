import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import RequestError

# Le module à tester
from app.core import google_jwt
from app.core.google_jwt import force_refresh_jwks

# Marque tous les tests de ce fichier comme asynchrones pour pytest
pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def mock_common_dependencies(mocker):
    """
    Mock les dépendances communes à tous les tests de ce fichier
    pour isoler la logique de la fonction `force_refresh_jwks`.
    """
    mocker.patch.object(google_jwt, 'tracer', MagicMock())
    mocker.patch.object(google_jwt, 'logger', MagicMock())
    # Mock le module time pour contrôler la valeur du timestamp
    mocker.patch.object(google_jwt, 'time', MagicMock())


async def test_force_refresh_jwks_on_success(mocker):
    """
    Vérifie que `force_refresh_jwks` récupère avec succès les clés,
    met à jour le cache et retourne les nouvelles clés.
    """
    # Arrange
    # 1. Préparation des données de test
    sample_jwks = {"keys": [{"kid": "test_kid_123", "alg": "RS256"}]}
    fixed_timestamp = 1234567890.0

    # 2. Mock de la réponse du client HTTP
    mock_response = MagicMock()
    mock_response.json.return_value = sample_jwks

    mock_google_client = MagicMock()
    mock_google_client.get = AsyncMock(return_value=mock_response)
    mocker.patch.object(google_jwt, 'google_client', mock_google_client)

    # 3. Mock de time.time() pour retourner une valeur prédictible
    mocker.patch.object(google_jwt.time, 'time', return_value=fixed_timestamp)

    # 4. Initialisation de l'état du cache avant l'appel
    google_jwt._jwks_cache = ({"keys": ["old_key"]}, 0)

    # Act
    result = await force_refresh_jwks()

    # Assert
    # 1. Vérifie que le client HTTP a été appelé avec la bonne URL
    mock_google_client.get.assert_awaited_once_with(google_jwt.GOOGLE_JWK_URL)

    # 2. Vérifie que la fonction retourne les clés récupérées
    assert result == sample_jwks

    # 3. Vérifie que le cache global a été correctement mis à jour
    assert google_jwt._jwks_cache == (sample_jwks, fixed_timestamp)

    # 4. Vérifie qu'un message de log a bien été émis
    google_jwt.logger.info.assert_called_once_with("Force refresh du cache JWK")


async def test_force_refresh_jwks_on_http_error(mocker):
    """
    Vérifie que `force_refresh_jwks` propage correctement une exception
    en cas d'échec de la requête HTTP et que le cache n'est pas altéré.
    """
    # Arrange
    # 1. Mock du client HTTP pour qu'il lève une exception
    mock_google_client = MagicMock()
    mock_google_client.get = AsyncMock(side_effect=RequestError("Erreur réseau simulée"))
    mocker.patch.object(google_jwt, 'google_client', mock_google_client)

    # 2. Sauvegarde de l'état initial du cache
    initial_cache_state = ({"keys": ["initial_key"]}, 123.0)
    google_jwt._jwks_cache = initial_cache_state

    # Act & Assert
    # Vérifie qu'une exception RequestError est bien levée
    with pytest.raises(RequestError, match="Erreur réseau simulée"):
        await force_refresh_jwks()

    # 1. Vérifie que le cache n'a pas été modifié après l'échec
    assert google_jwt._jwks_cache == initial_cache_state

    # 2. Vérifie que la tentative de refresh a bien été loguée malgré l'erreur
    google_jwt.logger.info.assert_called_once_with("Force refresh du cache JWK")
