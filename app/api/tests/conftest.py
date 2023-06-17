from starlite import AsyncTestClient
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.utils.auth import Authentication
from app.core.database import Base, session_config
from app.db.managers.accounts import jwt_manager, user_manager
from app.db.managers.listings import category_manager, listing_manager
from app.db.managers.base import file_manager

from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor
import pytest, asyncio

test_db = factories.postgresql_proc(port=None, dbname="test_db")


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine(test_db):
    pg_host = test_db.host
    pg_port = test_db.port
    pg_user = test_db.user
    pg_db = test_db.dbname
    pg_password = test_db.password

    with DatabaseJanitor(
        pg_user, pg_host, pg_port, pg_db, test_db.version, pg_password
    ):
        connection_str = f"postgresql+psycopg://{pg_user}:@{pg_host}:{pg_port}/{pg_db}"
        engine = create_async_engine(connection_str, future=True)
        yield engine
        await engine.dispose()


@pytest.fixture(autouse=True)
async def setup_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
def app(mocker, engine):
    TestAsyncSessionLocal = async_sessionmaker(
        bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
    )
    mocker.patch("app.core.database.AsyncSessionLocal", new=TestAsyncSessionLocal)
    from app.main import app

    return {"app": app, "db_session": TestAsyncSessionLocal}


@pytest.fixture
async def database(app):
    session = app["db_session"]
    async with session() as db:
        yield db


@pytest.fixture
async def client(app):
    async with AsyncTestClient(app=app["app"], session_config=session_config) as client:
        print(client.headers)
        yield client


@pytest.fixture
async def test_user(database):
    user_dict = {
        "first_name": "Test",
        "last_name": "Name",
        "email": "test@example.com",
        "password": "testpassword",
    }
    user = await user_manager.create(database, user_dict)
    return user


@pytest.fixture
async def verified_user(database):
    user_dict = {
        "first_name": "Test",
        "last_name": "Verified",
        "email": "testverifieduser@example.com",
        "password": "testpassword",
        "is_email_verified": True,
    }
    user = await user_manager.create(database, user_dict)
    return user


@pytest.fixture
async def another_verified_user(database):
    create_user_dict = {
        "first_name": "AnotherTest",
        "last_name": "UserVerified",
        "email": "anothertestverifieduser@example.com",
        "password": "anothertestverifieduser123",
        "is_email_verified": True,
    }

    user = await user_manager.create(database, create_user_dict)
    return user


@pytest.fixture
async def authorized_client(verified_user, client, database):
    access = await Authentication.create_access_token(
        {"user_id": str(verified_user.id)}
    )
    refresh = await Authentication.create_refresh_token()
    await jwt_manager.create(
        database,
        {"user_id": verified_user.id, "access": access, "refresh": refresh},
    )
    client.headers = {**client.headers, "Authorization": f"Bearer {access}"}
    return client


@pytest.fixture
async def create_listing(verified_user, database):
    # Create Category
    category = await category_manager.create(database, {"name": "TestCategory"})

    # Create File
    file = await file_manager.create(database, {"resource_type": "image/jpeg"})

    # Create Listing
    listing_dict = {
        "auctioneer_id": verified_user.id,
        "name": "New Listing",
        "desc": "New description",
        "category_id": category.id,
        "price": 1000.00,
        "closing_date": datetime.now() + timedelta(days=1),
        "image_id": file.id,
    }
    listing = await listing_manager.create(database, listing_dict)
    return {"user": verified_user, "listing": listing, "category": category}
