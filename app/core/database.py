from starlite.plugins.sql_alchemy import SQLAlchemyConfig, SQLAlchemyPlugin
from sqlalchemy.ext.declarative import declarative_base
from .config import settings

Base = declarative_base()

sqlalchemy_config = SQLAlchemyConfig(
    connection_string=settings.SQLALCHEMY_DATABASE_URL,
    dependency_key="db",
)

sqlalchemy_plugin = SQLAlchemyPlugin(config=sqlalchemy_config)