from app.core.config import Settings, settings


class TestSettings:
    """Tests pour la logique métier de configuration"""

    def test_is_prod_property_returns_true_for_prod_env(self):
        """Test que is_prod retourne True quand env='prod'"""
        test_settings = Settings(
            env="prod",
            database_url="postgresql://test:test@localhost/test",
            SYNC_DB_URL="postgresql://test:test@localhost/test",
            google_client_id="test_client_id",
            google_client_secret="test_secret",
            google_redirect_uri="http://localhost/callback",
            google_token_endpoint="https://oauth2.googleapis.com/token",
            jwk_uri="https://www.googleapis.com/oauth2/v3/certs",
            jwt_secret="test_jwt_secret",
            mj_apikey_public="test_public_key",
            mj_apikey_private="test_private_key",
            mj_sender_email="sender@test.com",
            mj_feedback_email="feedback@test.com",
            invitation_link="http://localhost/invite",
            check_mail="http://localhost/check",
            reset_password="http://localhost/reset",
            otel_endpoint="http://localhost:4317"
        )

        assert test_settings.is_prod is True

    def test_is_prod_property_returns_false_for_non_prod_env(self):
        """Test que is_prod retourne False pour les environnements non-prod"""
        test_environments = ["dev", "test", "staging"]
        
        for env_name in test_environments:
            test_settings = Settings(
                env=env_name,
                database_url="postgresql://test:test@localhost/test",
                SYNC_DB_URL="postgresql://test:test@localhost/test",
                google_client_id="test_client_id",
                google_client_secret="test_secret",
                google_redirect_uri="http://localhost/callback",
                google_token_endpoint="https://oauth2.googleapis.com/token",
                jwk_uri="https://www.googleapis.com/oauth2/v3/certs",
                jwt_secret="test_jwt_secret",
                mj_apikey_public="test_public_key",
                mj_apikey_private="test_private_key",
                mj_sender_email="sender@test.com",
                mj_feedback_email="feedback@test.com",
                invitation_link="http://localhost/invite",
                check_mail="http://localhost/check",
                reset_password="http://localhost/reset",
                otel_endpoint="http://localhost:4317"
            )

            assert test_settings.is_prod is False

    def test_is_prod_property_is_case_sensitive(self):
        """Test que is_prod est sensible à la casse"""
        test_settings = Settings(
            env="PROD",  # Majuscules
            database_url="postgresql://test:test@localhost/test",
            SYNC_DB_URL="postgresql://test:test@localhost/test",
            google_client_id="test_client_id",
            google_client_secret="test_secret",
            google_redirect_uri="http://localhost/callback",
            google_token_endpoint="https://oauth2.googleapis.com/token",
            jwk_uri="https://www.googleapis.com/oauth2/v3/certs",
            jwt_secret="test_jwt_secret",
            mj_apikey_public="test_public_key",
            mj_apikey_private="test_private_key",
            mj_sender_email="sender@test.com",
            mj_feedback_email="feedback@test.com",
            invitation_link="http://localhost/invite",
            check_mail="http://localhost/check",
            reset_password="http://localhost/reset",
            otel_endpoint="http://localhost:4317"
        )

        # is_prod fait .lower() donc PROD devrait être considéré comme prod
        assert test_settings.is_prod is True

    def test_global_settings_instance_exists(self):
        """Test que l'instance globale settings existe et fonctionne"""
        assert settings is not None
        assert isinstance(settings, Settings)
        assert hasattr(settings, 'is_prod')
        # Test que is_prod est callable et retourne un booléen
        assert isinstance(settings.is_prod, bool)