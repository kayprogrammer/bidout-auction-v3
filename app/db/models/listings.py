from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, relationship, validates, backref
from sqlalchemy.sql import func

from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID as GUUID  # General UUID

from app.db.models.accounts import User

from .base import BaseModel, File
from datetime import datetime


class Category(BaseModel):
    __tablename__ = "categories"

    name: Mapped[str] = Column(String(30), unique=True)
    slug: Mapped[str] = Column(String(), unique=True)

    def __repr__(self):
        return self.name

    @validates("name")
    def validate_name(self, key, value):
        if value == "Other":
            raise ValueError("Name must not be 'Other'")
        return value


class Listing(BaseModel):
    __tablename__ = "listings"

    auctioneer_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    name: Mapped[str] = Column(String(70))
    slug: Mapped[str] = Column(String(), unique=True)
    desc: Mapped[str] = Column(Text())
    category_id: Mapped[GUUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    price: Mapped[float] = Column(Numeric(precision=10, scale=2))
    closing_date: Mapped[datetime] = Column(DateTime, nullable=True)
    active: Mapped[bool] = Column(Boolean, default=True)

    image_id: Mapped[GUUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("files.id", ondelete="CASCADE"),
        unique=True,
    )
    image: Mapped[File] = relationship("File", lazy="joined")

    def __repr__(self):
        return self.name

    @property
    def bids_count(self):
        return self.listing_bids.count()

    @property
    def time_left_seconds(self):
        remaining_time = self.closing_date - datetime.utcnow()
        remaining_seconds = remaining_time.total_seconds()
        return remaining_seconds

    @property
    def time_left(self):
        if not self.active:
            return 0
        return self.time_left_seconds

    @property
    def highest_bid(self):
        highest_bid = 0.00
        related_bids = self.listing_bids
        if related_bids:
            highest_bid = (
                related_bids.session.query(func.max(Bid.amount))
                .filter_by(listing_id=self.id)
                .scalar()
            )
            highest_bid = related_bids.filter_by(amount=highest_bid).first()
            if highest_bid:
                highest_bid = highest_bid.amount
            else:
                highest_bid = 0.00

        return highest_bid


class Bid(BaseModel):
    __tablename__ = "bids"

    user_id: Mapped[GUUID] = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    listing_id: Mapped[GUUID] = Column(
        UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE")
    )
    listing: Mapped[Listing] = relationship(
        "Listing",
        foreign_keys=[listing_id],
        backref=backref("listing_bids", lazy="dynamic"),
    )
    amount: Mapped[float] = Column(Numeric(precision=10, scale=2))

    def __repr__(self):
        return f"{self.listing.name} - ${self.amount}"

    __table_args__ = (
        UniqueConstraint("listing_id", "amount", name="unique_listing_amount_bids"),
        UniqueConstraint("user_id", "listing_id", name="unique_user_listing_bids"),
    )


class WatchList(BaseModel):
    __tablename__ = "watchlists"

    user_id: Mapped[GUUID] = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    user: Mapped[User] = relationship("User", lazy="joined")

    listing_id: Mapped[GUUID] = Column(
        UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE")
    )
    listing: Mapped[Listing] = relationship("Listing", lazy="joined")

    session_key: Mapped[str] = Column(String)

    def __repr__(self):
        if self.user:
            return f"{self.listing.name} - {self.user.full_name()}"
        return f"{self.listing.name} - {self.session_key}"

    __table_args__ = (
        UniqueConstraint(
            "user_id", "listing_id", name="unique_user_listing_watchlists"
        ),
        UniqueConstraint(
            "session_key",
            "listing_id",
            name="unique_session_key_listing_watchlists",
        ),
    )
