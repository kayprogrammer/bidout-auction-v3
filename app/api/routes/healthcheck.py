from starlite import get
from app.api.schemas.base import ResponseSchema


@get(
    "/",
    summary="API Health Check",
    description="This endpoint checks the health of the API",
)
async def healthcheck() -> ResponseSchema:
    return ResponseSchema(message="pong")
