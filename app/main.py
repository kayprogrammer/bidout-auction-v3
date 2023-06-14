from starlite import (
    Starlite,
    TemplateConfig,
    Provide,
    OpenAPIConfig,
    OpenAPIController,
    HTTPException,
    ValidationException,
)
from pydantic_openapi_schema.v3_1_0 import Components, SecurityScheme, Tag
from starlite.status_codes import HTTP_500_INTERNAL_SERVER_ERROR
from starlite.contrib.jinja import JinjaTemplateEngine

from app.core.config import settings
from app.core.database import get_db, session_config
from app.common.exception_handlers import (
    validation_exception_handler,
    http_exception_handler,
    internal_server_error_handler,
    request_error_handler,
    RequestError,
)
from app.api.routers import all_routers

from pathlib import Path


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

template_config = TemplateConfig(
    directory=Path("app/templates"),
    engine=JinjaTemplateEngine,
)

app = Starlite(
    dependencies={"db": Provide(get_db)},
    route_handlers=all_routers,
    openapi_config=openapi_config,
    template_config=template_config,
    middleware=[session_config.middleware],
    exception_handlers={
        ValidationException: validation_exception_handler,
        HTTPException: http_exception_handler,
        HTTP_500_INTERNAL_SERVER_ERROR: internal_server_error_handler,
        RequestError: request_error_handler,
    },
)
