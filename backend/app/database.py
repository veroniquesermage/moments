from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# URL de la base (venant du .env)
DATABASE_URL = settings.database_url

# Création du moteur
engine = create_async_engine(DATABASE_URL, echo=True)

# 2) Instrumentation OTel → sur le moteur sync sous-jacent
SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)

# Création de la session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Création de la session pour chaque requête
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Base pour les modèles
Base = declarative_base()
