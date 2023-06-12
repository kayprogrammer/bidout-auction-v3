from starlite import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.utils.auth import Authentication
from app.common.exception_handlers import RequestError


async def get_current_user(request: Request, db: AsyncSession):
    token = request.headers.get("authorization")
    user = await Authentication.decodeAuthorization(db, token)
    if not user:
        raise RequestError(
            err_msg="Token is Invalid or Expired",
            status_code=401,
        )
    return user
