from starlite import (
    Starlite,
    OpenAPIConfig,
    OpenAPIController,
    CORSConfig,
)
from starlite.middleware import RateLimitConfig
from pydantic_openapi_schema.v3_1_0 import Components, SecurityScheme

from app.core.config import settings
from app.core.database import sqlalchemy_plugin
from app.common.exception_handlers import exc_handlers
from app.api.routers import all_routers


class MyOpenAPIController(OpenAPIController):
    path = "/"


openapi_config = OpenAPIConfig(
    title=settings.PROJECT_NAME,
    version="3.0.0",
    description="A simple bidding API built with Litestar",
    security=[{"BearerToken": [], "GuestToken": []}],
    components=Components(
        securitySchemes={
            "BearerToken": SecurityScheme(
                type="http",
                scheme="bearer",
            ),
            "GuestUserToken": SecurityScheme(
                type="apiKey",
                security_scheme_in="header",
                name="guestUserToken"
            )
        },
    ),
    openapi_controller=MyOpenAPIController,
    root_schema_site="swagger",
)

rate_limit_config = RateLimitConfig(rate_limit=("minute", 1000))
cors_config = CORSConfig(
    allow_origins=settings.CORS_ALLOWED_ORIGINS, allow_credentials=True
)

app = Starlite(
    route_handlers=all_routers,
    openapi_config=openapi_config,
    middleware=[rate_limit_config.middleware],
    plugins=[sqlalchemy_plugin],
    exception_handlers=exc_handlers,
    cors_config=cors_config,
)

