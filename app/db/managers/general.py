from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .base import BaseManager
from app.db.models.general import SiteDetail, Subscriber

class SiteDetailManager(BaseManager[SiteDetail]):
    async def get(self, db: AsyncSession) -> Optional[SiteDetail]:
        sitedetail = await db.execute(select(self.model))
        sitedetail = sitedetail.scalar_one_or_none()

        if not sitedetail:
            sitedetail = await self.create(db, {})
        return sitedetail


class SubscriberManager(BaseManager[Subscriber]):
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[Subscriber]:
        subscriber = await db.execute(select(self.model).where(self.model.email == email))
        return subscriber.scalar_one_or_none()


# class ReviewManager(BaseManager[Review]):
#     def get_active(self, db: Session) -> Optional[Review]:
#         reviews = db.query(self.model).filter_by(show=True).all()
#         return reviews

#     def get_count(self, db: Session) -> Optional[int]:
#         reviews_count = db.query(self.model).filter_by(show=True).count()
#         return reviews_count


sitedetail_manager = SiteDetailManager(SiteDetail)
subscriber_manager = SubscriberManager(Subscriber)
# review_manager = ReviewManager(Review)
