from starlite import Starlite, Router, Provide
from app.api.routes.general import general_handlers
from app.core.database import get_db

general_router = Router(
    path="/api/v3/general", route_handlers=general_handlers, tags=["General"]
)

all_routers = [general_router]
