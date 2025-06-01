from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "dev"  # utile pour plus tard (ex: tests vs prod)

    # Auth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    google_token_endpoint: str
    jwk_uri: str
    jwt_secret: str

    # Database
    database_url: str  # URL principale (async pour FastAPI)
    sync_database_url: str = Field(..., alias="SYNC_DB_URL")  # URL sync pour Alembic

    class Config:
        env_file = ".env"

settings = Settings()
