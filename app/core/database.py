from starlite.plugins.sql_alchemy import SQLAlchemyConfig, SQLAlchemyPlugin
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

sqlalchemy_config = SQLAlchemyConfig(
    connection_string=settings.SQLALCHEMY_DATABASE_URL,
    dependency_key="db",
)

sqlalchemy_plugin = SQLAlchemyPlugin(config=sqlalchemy_config)
# dto_factory = DTOFactory(plugins=[sqlalchemy_plugin]) Could have used this but doesn't support input validations yet!

Base = declarative_base()

AsyncSessionLocal = sessionmaker(
    bind=sqlalchemy_config.engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)


async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()
