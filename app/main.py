from starlite import Starlite, TemplateConfig, get
from starlite import OpenAPIConfig, OpenAPIController
from app.core.config import settings

from pydantic import ValidationError
from starlite.contrib.jinja import JinjaTemplateEngine

from pathlib import Path
from app.core import database


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
        route_handlers=[],
        openapi_config=openapi_config,
        template_config=template_config,
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
