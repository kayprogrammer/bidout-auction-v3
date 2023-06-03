from starlite import DTOFactory
from starlite.plugins.sql_alchemy import SQLAlchemyConfig, SQLAlchemyPlugin

from sqlalchemy.ext.declarative import declarative_base

from .config import settings

sqlalchemy_config = SQLAlchemyConfig(
    connection_string=settings.SQLALCHEMY_DATABASE_URL,
    dependency_key="async_session",
)

sqlalchemy_plugin = SQLAlchemyPlugin(config=sqlalchemy_config)
dto_factory = DTOFactory(plugins=[sqlalchemy_plugin])

Base = declarative_base()
