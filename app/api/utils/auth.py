import random
import string
from datetime import datetime, timedelta

from jose import jwt

from app.core.config import settings
from app.db.managers.accounts import user_manager, jwt_manager


class Authentication(object):
    def __init__(self, algorithm="HS256") -> None:
        self.algorithm = algorithm

    # generate random string
    def get_random(self, length):
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    # generate access token based and encode user's id
    async def create_access_token(self, payload: dict):
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {"exp": expire, **payload}
        encoded_jwt = await jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=self.algorithm
        )
        return encoded_jwt

    # generate random refresh token
    async def create_refresh_token(
        self,
        expire=datetime.utcnow()
        + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    ):
        return await jwt.encode(
            {"exp": expire, "data": self.get_random(10)},
            settings.SECRET_KEY,
            algorithm=self.algorithm,
        )

    # verify refresh token
    async def verify_refresh_token(self, token):
        try:
            await jwt.decode(token, settings.SECRET_KEY, algorithms=[self.algorithm])
            return True
        except:
            return False

    # deocde access token from header
    async def decodeJWT(self, db, token):
        if not token:
            return None

        try:
            decoded = await jwt.decode(
                token[7:], settings.SECRET_KEY, algorithms=[self.algorithm]
            )
        except:
            return None

        if decoded:
            user = await user_manager.get_by_id(db, decoded.get("user_id"))
            if user:
                jwt_obj = await jwt_manager.get_by_user_id(db, user.id)
                if (
                    not jwt_obj
                ):  # to confirm the validity of the token (it's existence in our database)
                    return None
                return user
            return None
