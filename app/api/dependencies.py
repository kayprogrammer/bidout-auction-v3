from typing import Optional
from uuid import UUID
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


async def get_client_id(request: Request, db: AsyncSession) -> Optional[UUID]:
    token = request.headers.get("authorization")
    if token:
        user = await get_current_user(request, db)
        return user.id
    guest_jwt_token = request.headers.get("guestusertoken")
    decoded = await Authentication.decode_jwt(guest_jwt_token)
    return decoded["guestuser_id"] if decoded else None
