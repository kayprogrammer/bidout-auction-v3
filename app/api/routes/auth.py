from typing import Optional, Union
from starlite import Controller, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.auth import (
    RegisterUserSchema,
    VerifyOtpSchema,
    RequestOtpSchema,
    SetNewPasswordSchema,
    LoginUserSchema,
    RefreshTokensSchema,
    RegisterResponseSchema,
    TokensResponseSchema,
)
from app.common.exception_handlers import RequestError
from app.api.schemas.base import ResponseSchema
from app.db.managers.base import guestuser_manager

from app.db.models.accounts import User
from app.db.managers.accounts import user_manager, otp_manager, jwt_manager
from app.db.managers.listings import watchlist_manager

from app.api.utils.emails import send_email
from app.core.security import verify_password
from app.api.utils.auth import Authentication
from app.db.models.base import GuestUser


class RegisterView(Controller):
    path = "/register"

    @post(
        summary="Register a new user",
        description="This endpoint registers new users into our application",
    )
    async def register(
        self, data: RegisterUserSchema, db: AsyncSession
    ) -> RegisterResponseSchema:
        # Check for existing user
        existing_user = await user_manager.get_by_email(db, data.email)
        if existing_user:
            raise RequestError(
                err_msg="Invalid Entry",
                status_code=422,
                data={"email": "Email already registered!"},
            )

        # Create user
        user = await user_manager.create(db, data.dict())

        # Send verification email
        await send_email(db, user, "activate")

        return RegisterResponseSchema(
            message="Registration successful", data={"email": user.email}
        )


class VerifyEmailView(Controller):
    path = "/verify-email"

    @post(
        summary="Verify a user's email",
        description="This endpoint verifies a user's email",
        status_code=200,
    )
    async def verify_email(
        self, data: VerifyOtpSchema, db: AsyncSession
    ) -> ResponseSchema:
        user_by_email = await user_manager.get_by_email(db, data.email)

        if not user_by_email:
            raise RequestError(err_msg="Incorrect Email", status_code=404)

        if user_by_email.is_email_verified:
            return ResponseSchema(message="Email already verified")

        otp = await otp_manager.get_by_user_id(db, user_by_email.id)
        if not otp or otp.code != data.otp:
            raise RequestError(err_msg="Incorrect Otp", status_code=404)
        if otp.check_expiration():
            raise RequestError(err_msg="Expired Otp")

        user = await user_manager.update(db, user_by_email, {"is_email_verified": True})
        await otp_manager.delete(db, otp)
        # Send welcome email
        await send_email(db, user, "welcome")
        return ResponseSchema(message="Account verification successful")


class ResendVerificationEmailView(Controller):
    path = "/resend-verification-email"

    @post(
        summary="Resend Verification Email",
        description="This endpoint resends new otp to the user's email",
        status_code=200,
    )
    async def resend_verification_email(
        self, data: RequestOtpSchema, db: AsyncSession
    ) -> ResponseSchema:
        user_by_email = await user_manager.get_by_email(db, data.email)
        if not user_by_email:
            raise RequestError(err_msg="Incorrect Email", status_code=404)
        if user_by_email.is_email_verified:
            return ResponseSchema(message="Email already verified")

        # Send verification email
        await send_email(db, user_by_email, "activate")

        return ResponseSchema(message="Verification email sent")


class SendPasswordResetOtpView(Controller):
    path = "/send-password-reset-otp"

    @post(
        summary="Send Password Reset Otp",
        description="This endpoint sends new password reset otp to the user's email",
        status_code=200,
    )
    async def send_password_reset_otp(
        self, data: RequestOtpSchema, db: AsyncSession
    ) -> ResponseSchema:
        user_by_email = await user_manager.get_by_email(db, data.email)
        if not user_by_email:
            raise RequestError(err_msg="Incorrect Email", status_code=404)

        # Send password reset email
        await send_email(db, user_by_email, "reset")

        return ResponseSchema(message="Password otp sent")


class SetNewPasswordView(Controller):
    path = "/set-new-password"

    @post(
        summary="Set New Password",
        description="This endpoint verifies the password reset otp",
        status_code=200,
    )
    async def set_new_password(
        self, data: SetNewPasswordSchema, db: AsyncSession
    ) -> ResponseSchema:
        email = data.email
        otp_code = data.otp
        password = data.password

        user_by_email = await user_manager.get_by_email(db, email)
        if not user_by_email:
            raise RequestError(err_msg="Incorrect Email", status_code=404)

        otp = await otp_manager.get_by_user_id(db, user_by_email.id)
        if not otp or otp.code != otp_code:
            raise RequestError(err_msg="Incorrect Otp", status_code=404)

        if otp.check_expiration():
            raise RequestError(err_msg="Expired Otp")

        await user_manager.update(db, user_by_email, {"password": password})

        # Send password reset success email
        await send_email(db, user_by_email, "reset-success")

        return ResponseSchema(message="Password reset successful")


class LoginView(Controller):
    path = "/login"

    @post(
        summary="Login a user",
        description="This endpoint generates new access and refresh tokens for authentication",
    )
    async def login(
        self,
        data: LoginUserSchema,
        client: Optional[Union["User", "GuestUser"]],
        db: AsyncSession,
    ) -> TokensResponseSchema:
        email = data.email
        plain_password = data.password
        user = await user_manager.get_by_email(db, email)
        if not user or verify_password(plain_password, user.password) == False:
            raise RequestError(err_msg="Invalid credentials", status_code=401)

        if not user.is_email_verified:
            raise RequestError(err_msg="Verify your email first", status_code=401)
        await jwt_manager.delete_by_user_id(db, user.id)

        # Create tokens and store in jwt model
        access = await Authentication.create_access_token({"user_id": str(user.id)})
        refresh = await Authentication.create_refresh_token()
        await jwt_manager.create(
            db, {"user_id": user.id, "access": access, "refresh": refresh}
        )

        # Move all guest user watchlists to the authenticated user watchlists
        guest_user_watchlists = await watchlist_manager.get_by_session_key(
            db, client.id if client else None, user.id
        )
        if len(guest_user_watchlists) > 0:
            data_to_create = [
                {"user_id": user.id, "listing_id": listing_id}.copy()
                for listing_id in guest_user_watchlists
            ]
            await watchlist_manager.bulk_create(db, data_to_create)

        if isinstance(client, GuestUser):
            # Delete client (Almost like clearing sessions)
            await guestuser_manager.delete(db, client)

        return TokensResponseSchema(
            message="Login successful", data={"access": access, "refresh": refresh}
        )


class RefreshTokensView(Controller):
    path = "/refresh"

    @post(
        summary="Refresh tokens",
        description="This endpoint refresh tokens by generating new access and refresh tokens for a user",
    )
    async def refresh(
        self, data: RefreshTokensSchema, db: AsyncSession
    ) -> TokensResponseSchema:
        token = data.refresh
        jwt = await jwt_manager.get_by_refresh(db, token)
        if not jwt:
            raise RequestError(err_msg="Refresh token does not exist", status_code=404)
        if not await Authentication.decode_jwt(token):
            raise RequestError(
                err_msg="Refresh token is invalid or expired", status_code=401
            )

        access = await Authentication.create_access_token({"user_id": str(jwt.user_id)})
        refresh = await Authentication.create_refresh_token()

        await jwt_manager.update(db, jwt, {"access": access, "refresh": refresh})

        return TokensResponseSchema(
            message="Tokens refresh successful",
            data={"access": access, "refresh": refresh},
        )


class LogoutView(Controller):
    path = "/logout"

    @get(
        summary="Logout a user",
        description="This endpoint logs a user out from our application",
    )
    async def logout(self, user: User, db: AsyncSession) -> ResponseSchema:
        await jwt_manager.delete_by_user_id(db, user.id)
        return ResponseSchema(message="Logout successful")


auth_handlers = [
    RegisterView,
    VerifyEmailView,
    ResendVerificationEmailView,
    SendPasswordResetOtpView,
    SetNewPasswordView,
    LoginView,
    RefreshTokensView,
    LogoutView,
]
