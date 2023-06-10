from starlite import Router
from app.api.routes.general import general_handlers
from app.api.routes.healthcheck import healthcheck

general_router = Router(
    path="/api/v3/general", route_handlers=general_handlers, tags=["General"]
)

healthcheck_router = Router(
    path="/api/v3/healthcheck", route_handlers=[healthcheck], tags=["HealthCheck"]
)

all_routers = [general_router, healthcheck_router]
