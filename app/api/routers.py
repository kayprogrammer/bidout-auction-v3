from starlite import Router, Provide
from app.api.routes.general import general_handlers
from app.api.routes.auth import auth_handlers
from app.api.routes.listings import listings_handlers
from app.api.routes.healthcheck import healthcheck
from app.api.dependencies import get_client_id, get_current_user

general_router = Router(
    path="/api/v3/general", route_handlers=general_handlers, tags=["General"]
)

auth_router = Router(
    path="/api/v3/auth",
    route_handlers=auth_handlers,
    tags=["Auth"],
    dependencies={"user": Provide(get_current_user)},
)

listings_router = Router(
    path="/api/v3/listings",
    route_handlers=listings_handlers,
    tags=["Listings"],
    dependencies={
        "user": Provide(get_current_user),
        "client_id": Provide(get_client_id),
    },
)

healthcheck_router = Router(
    path="/api/v3/healthcheck",
    route_handlers=[healthcheck],
    tags=["HealthCheck"],
)

all_routers = [general_router, auth_router, listings_router, healthcheck_router]
