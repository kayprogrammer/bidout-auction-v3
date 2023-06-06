from datetime import datetime
from starlite import AsyncTestClient, Provide
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.managers.accounts import user_manager
from app.main import app

import pytest_asyncio


TEST_DATABASE = f"{settings.SQLALCHEMY_DATABASE_URL}_test"

engine = create_async_engine(TEST_DATABASE, future=True)

TestAsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture
async def database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    db = TestAsyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest_asyncio.fixture
async def client(database):
    def overide_get_db():
        try:
            yield database
        finally:
            database.close()

    app.dependencies["db"] = Provide(overide_get_db)
    async with AsyncTestClient(app=app) as client:
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
