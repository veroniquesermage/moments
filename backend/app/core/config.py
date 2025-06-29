import os
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Choisir dynamiquement le bon fichier .env
env = os.getenv("APP_ENV", "dev")
env_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), f".env.{env}")
load_dotenv(dotenv_path=env_file_path)



class Settings(BaseSettings):
    env: str = env

    # Auth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    google_token_endpoint: str
    jwk_uri: str
    jwt_secret: str

    # Database
    database_url: str
    sync_database_url: str = Field(..., alias="SYNC_DB_URL")

    # Mailing
    mj_apikey_public: str
    mj_apikey_private: str
    mj_sender_email: str
    mj_feedback_email: str

    invitation_link: str

settings = Settings()

print(f"URL base de données : {settings.database_url}")
