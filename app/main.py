from starlite import Starlite, TemplateConfig, get, Provide, OpenAPIConfig, OpenAPIController, HTTPException, ValidationException
from starlite.status_codes import HTTP_500_INTERNAL_SERVER_ERROR
from starlite.contrib.jinja import JinjaTemplateEngine

from app.core.config import settings
from app.core.database import get_db
from app.common.exception_handlers import validation_exception_handler, http_exception_handler, internal_server_error_handler
from app.api.routers import all_routers

from pathlib import Path

class MyOpenAPIController(OpenAPIController):
    path = "/"


def create_app() -> Starlite:
    openapi_config = OpenAPIConfig(
        title=settings.PROJECT_NAME,
        version="3.0.0",
        description="A simple bidding API built with Litestar",
        security=[{"BearerToken": []}],
        openapi_controller=MyOpenAPIController,
        root_schema_site="swagger",
    )

    template_config = TemplateConfig(
        directory=Path("app/templates"),
        engine=JinjaTemplateEngine,
    )

    app = Starlite(
        route_handlers=all_routers,
        openapi_config=openapi_config,
        template_config=template_config,
        dependencies = {"db": Provide(get_db)},
        exception_handlers={
            ValidationException: validation_exception_handler,
            HTTPException: http_exception_handler,
            HTTP_500_INTERNAL_SERVER_ERROR: internal_server_error_handler
        },
    )
    return app


app = create_app()


@get(
    "/ping",
    tags=["HealthCheck"],
    summary="API Health Check",
    description="This endpoint checks the health of the API",
)
async def healthcheck() -> dict[str, str]:
    return {"success": "pong!"}


app.register(healthcheck, add_to_openapi_schema=True)
