from starlite import Starlite, AsyncTestClient, Provide
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.managers.accounts import user_manager
from app.api.routers import all_routers
from app.main import app

import pytest_asyncio
import asyncio

TEST_DATABASE = f"{settings.SQLALCHEMY_DATABASE_URL}_test"

engine = create_async_engine(TEST_DATABASE, future=True)

TestAsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope='session')
def event_loop():
    """Overrides pytest default function scoped event loop"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def database():
    db = TestAsyncSessionLocal()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield db
    db.close()

# @pytest_asyncio.fixture
# def app(database):
#     def test_get_db():
#         try:
#             yield database
#         finally:
#             database.close()

#     app = Starlite(route_handlers=all_routers, dependencies={"db": Provide(test_get_db)})
#     return app

@pytest_asyncio.fixture(scope='session')
async def client():
    async with AsyncTestClient(app) as client:
        yield client

@pytest_asyncio.fixture
async def test_user(database):
    user_dict = {
        "first_name": "Test",
        "last_name": "Name",
        "email": "test@example.com",
        "password": get_password_hash("testpassword"),
    }
    user = await user_manager.create(database, user_dict)
    return user


@pytest_asyncio.fixture
async def verified_user(database):
    user_dict = {
        "first_name": "Test",
        "last_name": "Name",
        "email": "test@example.com",
        "password": get_password_hash("testpassword"),
        "is_email_verified": True,
    }
    user = await user_manager.create(database, user_dict)
    return user
