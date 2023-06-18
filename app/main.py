from starlite import (
    Starlite,
    OpenAPIConfig,
    OpenAPIController,
)
from pydantic_openapi_schema.v3_1_0 import Components, SecurityScheme

from app.core.config import settings
from app.core.database import session_config, sqlalchemy_plugin
from app.common.exception_handlers import exc_handlers
from app.api.routers import all_routers


class MyOpenAPIController(OpenAPIController):
    path = "/"


openapi_config = OpenAPIConfig(
    title=settings.PROJECT_NAME,
    version="3.0.0",
    description="A simple bidding API built with Litestar",
    security=[{"BearerToken": []}],
    components=Components(
        securitySchemes={
            "BearerToken": SecurityScheme(
                type="http",
                scheme="bearer",
            )
        },
    ),
    openapi_controller=MyOpenAPIController,
    root_schema_site="swagger",
)

app = Starlite(
    route_handlers=all_routers,
    openapi_config=openapi_config,
    middleware=[session_config.middleware],
    plugins=[sqlalchemy_plugin],
    exception_handlers=exc_handlers,
)
