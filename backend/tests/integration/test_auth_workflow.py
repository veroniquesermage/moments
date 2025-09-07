import pytest
import uuid
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models import User
from app.services.auth.auth_service import AuthService
from app.schemas.auth import GoogleAuthRequest, LoginRequest, RegisterRequest


class TestAuthWorkflow:
    """Tests d'intégration pour les workflows d'authentification complets"""

    @pytest.mark.skip(reason="Auth workflow tests need HTTP client setup")
    @pytest.mark.skip(reason="Auth workflow tests need HTTP client setup")
    @pytest.mark.asyncio
    async def test_complete_google_auth_workflow(self, integration_db_session: AsyncSession):
        """Test du workflow Google Auth complet: Token → Vérification → JWT → DB"""
        # Arrange
        test_uuid = str(uuid.uuid4())[:8]
        mock_google_payload = {
            "sub": f"123456789-{test_uuid}",
            "email": f"test-{test_uuid}@example.com",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User"
        }

        auth_request = GoogleAuthRequest(code="mock_auth_code", code_verifier="mock_verifier", remember_me=False)

        # Act & Assert - Test avec mocks
        with patch('app.core.google_jwt.verify_google_id_token') as mock_verify:
            mock_verify.return_value = mock_google_payload

            # Appeler le service d'authentification
            response = await AuthService.authenticate_google_user(auth_request, integration_db_session)

            # Vérifier que l'utilisateur est créé en DB
            from sqlalchemy import text
            result = await integration_db_session.execute(
                text("SELECT * FROM utilisateur WHERE email = :email"),
                {"email": f"test-{test_uuid}@example.com"}
            )
            user_row = result.fetchone()
            assert user_row is not None
            assert user_row[2] == f"test-{test_uuid}@example.com"  # email column

            # Vérifier la réponse contient un JWT
            assert response.status_code == 200
            response_data = response.body.decode()
            assert "access_token" in response_data or "token" in response_data

    @pytest.mark.skip(reason="Auth workflow tests need HTTP client setup")
    @pytest.mark.asyncio
    async def test_credentials_auth_workflow(self, integration_db_session: AsyncSession):
        """Test du workflow credentials complet: Register → Login → Access"""
        # Phase 1: Register
        test_uuid = str(uuid.uuid4())[:8]
        register_request = RegisterRequest(
            token=f"mock_registration_token_{test_uuid}",
            prenom="Cred",
            nom="User"
        )

        register_response = await AuthService.authenticate_credentials_user(
            register_request, integration_db_session
        )
        assert register_response.status_code == 200

        # Vérifier utilisateur créé en DB
        result = await integration_db_session.execute(
            text("SELECT * FROM utilisateur WHERE email = :email"),
            {"email": f"credentials-{test_uuid}@example.com"}
        )
        user_row = result.fetchone()
        assert user_row is not None

        # Phase 2: Login avec les mêmes credentials
        login_request = LoginRequest(
            email=f"credentials-{test_uuid}@example.com",
            password="TestPassword123!",
            remember_me=False
        )

        login_response = await AuthService.login_with_credentials(
            login_request, integration_db_session
        )
        assert login_response.status_code == 200

        # Vérifier JWT dans la réponse
        response_data = login_response.body.decode()
        assert "access_token" in response_data or "token" in response_data

    @pytest.mark.skip(reason="Auth workflow tests need HTTP client setup")
    @pytest.mark.asyncio
    async def test_invalid_credentials_rejected(self, integration_db_session: AsyncSession):
        """Test que les credentials invalides sont rejetées"""
        # Créer un utilisateur valide d'abord
        test_uuid = str(uuid.uuid4())[:8]
        register_request = RegisterRequest(
            token=f"mock_validation_token_{test_uuid}",
            prenom="Valid",
            nom="User"
        )

        await AuthService.authenticate_credentials_user(register_request, integration_db_session)

        # Tenter login avec mauvais mot de passe
        invalid_login = LoginRequest(
            email=f"valid-{test_uuid}@example.com",
            password="WrongPassword",
            remember_me=False
        )

        with pytest.raises(Exception):  # Should raise HTTPException or similar
            await AuthService.login_with_credentials(invalid_login, integration_db_session)

    @pytest.mark.skip(reason="Auth workflow tests need HTTP client setup")
    @pytest.mark.asyncio
    async def test_google_auth_creates_or_updates_user(self, integration_db_session: AsyncSession):
        """Test que Google Auth crée un nouvel utilisateur ou met à jour l'existant"""
        test_uuid = str(uuid.uuid4())[:8]
        mock_google_payload = {
            "sub": f"existing_user_123_{test_uuid}",
            "email": f"existing-{test_uuid}@example.com",
            "name": "Updated Name",
            "given_name": "Updated",
            "family_name": "Name"
        }

        auth_request = GoogleAuthRequest(code="mock_code", code_verifier="mock_verifier", remember_me=False)

        with patch('app.core.google_jwt.verify_google_id_token') as mock_verify:
            mock_verify.return_value = mock_google_payload

            # Premier appel - création
            response1 = await AuthService.authenticate_google_user(auth_request, integration_db_session)
            assert response1.status_code == 200

            # Deuxième appel - mise à jour du même utilisateur
            mock_google_payload["name"] = "Even More Updated Name"
            response2 = await AuthService.authenticate_google_user(auth_request, integration_db_session)
            assert response2.status_code == 200

            # Vérifier qu'il n'y a toujours qu'un seul utilisateur avec cet email
            result = await integration_db_session.execute(
                text("SELECT COUNT(*) FROM utilisateur WHERE email = :email"),
                {"email": f"existing-{test_uuid}@example.com"}
            )
            count = result.fetchone()[0]
            assert count == 1
