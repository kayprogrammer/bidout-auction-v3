from starlite import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.utils.auth import Authentication
from app.common.exception_handlers import RequestError
from app.db.models.accounts import User


async def get_current_user(request: Request, db: AsyncSession) -> User:
    token = request.headers.get("authorization")
    if not token:
        raise RequestError(
            err_msg="Unauthorized User!",
            status_code=401,
        )
    user = await Authentication.decodeAuthorization(db, token)
    if not user:
        raise RequestError(
            err_msg="Auth Token is Invalid or Expired",
            status_code=401,
        )
    return user


async def get_client_id(request: Request, db: AsyncSession) -> str:
    token = request.headers.get("authorization")
    if token:
        user = await get_current_user(request, db)
        return str(user.id)
    session_key = request.cookies.get("session")
    return session_key
