from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from .base import BaseManager
from app.db.models.general import SiteDetail, Subscriber, Review


class SiteDetailManager(BaseManager[SiteDetail]):
    async def get(self, db: AsyncSession) -> Optional[SiteDetail]:
        sitedetail = await db.execute(select(self.model))
        sitedetail = sitedetail.scalar_one_or_none()

        if not sitedetail:
            sitedetail = await self.create(db, {})
        return sitedetail


class SubscriberManager(BaseManager[Subscriber]):
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[Subscriber]:
        subscriber = await db.execute(
            select(self.model).where(self.model.email == email)
        )
        return subscriber.scalar_one_or_none()


class ReviewManager(BaseManager[Review]):
    async def get_active(self, db: AsyncSession) -> Optional[Review]:
        reviews = await db.execute(select(self.model).where(self.model.show == True))
        return reviews.scalars().all()

    async def get_count(self, db: AsyncSession) -> Optional[int]:
        count = await db.execute(
            select(func.count()).select_from(
                select(self.model).where(self.model.show == True)
            )
        )
        return count.scalar_one()


sitedetail_manager = SiteDetailManager(SiteDetail)
subscriber_manager = SubscriberManager(Subscriber)
review_manager = ReviewManager(Review)
