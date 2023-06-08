from starlite import AsyncTestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.core.database import Base
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.managers.accounts import user_manager
import pytest, asyncio

TEST_DATABASE = f"{settings.SQLALCHEMY_DATABASE_URL}_test"

engine = create_async_engine(TEST_DATABASE, pool_size=10, echo=True, max_overflow=10)

TestAsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def app(session_mocker):
    session_mocker.patch(
        "app.core.database.AsyncSessionLocal", new=TestAsyncSessionLocal
    )
    from app.main import app

    return app


@pytest.fixture(scope="session")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest.fixture
async def client(app, setup_db):
    async with AsyncTestClient(app) as client:
        yield client


@pytest.fixture
async def database():
    async with TestAsyncSessionLocal() as db:
        yield db


@pytest.fixture
async def test_user(database):
    user_dict = {
        "first_name": "Test",
        "last_name": "Name",
        "email": "test@example.com",
        "password": get_password_hash("testpassword"),
    }
    user = await user_manager.create(database, user_dict)
    return user


@pytest.fixture
async def verified_user(database):
    user_dict = {
        "first_name": "Test",
        "last_name": "Verified",
        "email": "testverifieduser@example.com",
        "password": get_password_hash("testpassword"),
        "is_email_verified": True,
    }
    user = await user_manager.create(database, user_dict)
    return user
