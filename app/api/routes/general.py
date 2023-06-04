from starlite import Controller, Provide, get, post
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.schemas.general import (
    SubscriberSchema,
    SiteDetailDataSchema,
    SiteDetailResponseSchema,
    SubscriberResponseSchema,
    # ReviewsDataSchema,
    # ReviewsResponseSchema,
)

from app.db.managers.general import (
    sitedetail_manager,
    subscriber_manager,
    # review_manager,
)

class SiteDetailView(Controller):
    path = "/site-detail"

    @get(
        summary="Retrieve site details",
        description="This endpoint retrieves few details of the site/application",
        response={"application/json": SiteDetailResponseSchema},
    )
    async def retrieve_site_details(self, db: AsyncSession) -> SiteDetailResponseSchema:
        sitedetail = await sitedetail_manager.get(db)
        return {
            "message": "Site Details fetched",
            "data": SiteDetailDataSchema.from_orm(sitedetail)
        }

class SubscriberCreateView(Controller):
    path = '/subscribe'

    @post(
        summary="Add a subscriber",
        description="This endpoint creates a newsletter subscriber in our application",
        response={"application/json": SubscriberResponseSchema},
    )
    async def subscribe(self, data: SubscriberSchema, db: AsyncSession) -> SubscriberResponseSchema:
        email = data.email
        subscriber = await subscriber_manager.get_by_email(db, email)
        if not subscriber:
            subscriber = await subscriber_manager.create(db, {"email": email})

        return {
            "status": "success",
            "message": "Subscription successful",
            "data": SubscriberSchema.from_orm(subscriber)
        }


# class ReviewsView(HTTPMethodView):
#     @openapi.definition(
#         summary="Retrieve site reviews",
#         description="This endpoint retrieves a few reviews of the application",
#         response={"application/json": ReviewsResponseSchema},
#     )
#     async def get(self, request, **kwargs):
#         db = request.ctx.db
#         reviews = review_manager.get_active(db)[:3]
#         data = [ReviewsDataSchema.from_orm(review).dict() for review in reviews]
#         return CustomResponse.success(message="Reviews fetched", data=data)

general_handlers = [SiteDetailView, SubscriberCreateView]