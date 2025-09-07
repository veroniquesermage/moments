"""
Configuration spécifique aux tests unitaires
"""
import pytest
import pytest_asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base


@pytest_asyncio.fixture(scope="session")
async def unit_test_engine():
    """Moteur de base de données dédié aux tests unitaires"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def unit_db_session(unit_test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Session de base de données isolée pour tests unitaires"""
    AsyncSessionLocal = sessionmaker(
        bind=unit_test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            pass