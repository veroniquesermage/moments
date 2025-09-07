import pytest
from datetime import datetime, timedelta
from jose import jwt as jose_jwt

from app.core.jwt import create_access_token, SECRET_KEY, ALGORITHM


class TestJWT:
    """Tests pour la logique JWT spécifique à l'application"""

    def test_create_access_token_includes_purpose(self):
        """Test que le token inclut le champ 'purpose' avec 'access_token'"""
        test_data = {"sub": "user123"}
        expires_at = datetime(2030, 12, 31, 23, 59, 59)

        token = create_access_token(test_data, expires_at)

        decoded = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        assert decoded["purpose"] == "access_token"

    def test_create_access_token_preserves_user_data(self):
        """Test que les données utilisateur sont préservées dans le token"""
        test_data = {
            "sub": "user123",
            "email": "test@example.com",
            "roles": ["admin", "user"]
        }
        expires_at = datetime(2030, 12, 31, 23, 59, 59)

        token = create_access_token(test_data, expires_at)

        decoded = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        assert decoded["sub"] == "user123"
        assert decoded["email"] == "test@example.com"
        assert decoded["roles"] == ["admin", "user"]

    def test_create_access_token_does_not_modify_original_data(self):
        """Test que les données originales ne sont pas modifiées"""
        original_data = {"sub": "user123", "role": "admin"}
        data_copy = original_data.copy()
        expires_at = datetime(2030, 12, 31, 23, 59, 59)

        create_access_token(original_data, expires_at)

        assert original_data == data_copy
        assert "purpose" not in original_data
        assert "exp" not in original_data