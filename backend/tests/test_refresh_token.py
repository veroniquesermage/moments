import os
import sys
import asyncio
from uuid import uuid4

# Configuration for Settings before any app import
os.environ['GOOGLE_CLIENT_ID'] = 'test'
os.environ['GOOGLE_CLIENT_SECRET'] = 'test'
os.environ['GOOGLE_REDIRECT_URI'] = 'http://localhost'
os.environ['GOOGLE_TOKEN_ENDPOINT'] = 'http://localhost/token'
os.environ['JWK_URI'] = 'http://localhost/jwk'
os.environ['JWT_SECRET'] = 'secret'
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///:memory:'
os.environ['SYNC_DB_URL'] = 'sqlite:///:memory:'
os.environ['CHECK_MAIL'] = 'http://localhost/check_mail'
os.environ['RESET_PASSWORD'] = 'http://localhost/reset-password?token='

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.services.token_service import TokenService
from app.models import RefreshToken

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_models())


def test_refresh_token_replaced_and_revoked():
    async def inner():
        async with AsyncSessionLocal() as session:
            user_id = 1
            jti1 = str(uuid4())
            await TokenService.store_refresh_token(session, user_id, jti1)
            count = (await session.execute(select(func.count(RefreshToken.id)))).scalar_one()
            assert count == 1

            jti2 = str(uuid4())
            await TokenService.store_refresh_token(session, user_id, jti2)
            count = (await session.execute(select(func.count(RefreshToken.id)))).scalar_one()
            assert count == 1  # ancien token supprimé

            await TokenService.revoke_refresh_token(session, jti2, user_id)
            count = (await session.execute(select(func.count(RefreshToken.id)))).scalar_one()
            assert count == 0

    asyncio.run(inner())
