from starlite import Controller, get, post
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas.general import (
    SubscriberSchema,
    SiteDetailDataSchema,
    SiteDetailResponseSchema,
    SubscriberResponseSchema,
    ReviewsDataSchema,
    ReviewsResponseSchema,
)

from app.db.managers.general import (
    sitedetail_manager,
    subscriber_manager,
    review_manager,
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
        return SiteDetailResponseSchema(message="Site Details fetched", data=sitedetail)


class SubscriberCreateView(Controller):
    path = "/subscribe"

    @post(
        summary="Add a subscriber",
        description="This endpoint creates a newsletter subscriber in our application",
        response={"application/json": SubscriberResponseSchema},
    )
    async def subscribe(
        self, data: SubscriberSchema, db: AsyncSession
    ) -> SubscriberResponseSchema:
        email = data.email
        subscriber = await subscriber_manager.get_by_email(db, email)
        if not subscriber:
            subscriber = await subscriber_manager.create(db, {"email": email})

        return SubscriberResponseSchema(
            message="Subscription successful", data=subscriber
        )


class ReviewsView(Controller):
    path = "/reviews"

    @get(
        summary="Retrieve site reviews",
        description="This endpoint retrieves a few reviews of the application",
        response={"application/json": ReviewsResponseSchema},
    )
    async def get(self, db: AsyncSession) -> ReviewsResponseSchema:
        reviews = await review_manager.get_active(db)
        data = [review for review in reviews]
        return ReviewsResponseSchema(message="Reviews fetched", data=data)


general_handlers = [SiteDetailView, SubscriberCreateView, ReviewsView]
