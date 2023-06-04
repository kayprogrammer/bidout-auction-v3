from starlite import Starlite, Router
from app.api.routes.general import general_handlers

general_router = Router(path="/api/v3/general", route_handlers=general_handlers, tags=['General'])

all_routers = [general_router]