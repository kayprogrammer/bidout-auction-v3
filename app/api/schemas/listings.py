from typing import Optional, List, Any
from uuid import UUID

from pydantic import BaseModel, validator, Field
from datetime import datetime
from .base import ResponseSchema

from app.api.utils.file_processors import FileProcessor

from decimal import Decimal

# LISTINGS


class AddOrRemoveWatchlistSchema(BaseModel):
    slug: str = Field(..., example="listing_slug")


class AddOrRemoveWatchlistResponseDataSchema(BaseModel):
    guestuser_id: Optional[UUID]


class AddOrRemoveWatchlistResponseSchema(ResponseSchema):
    data: Optional[AddOrRemoveWatchlistResponseDataSchema]


class ListingDataSchema(BaseModel):
    name: str

    auctioneer: dict = Field(
        ..., example={"name": "John Doe", "avatar": "https://image.url"}
    )

    slug: Optional[str]
    desc: str

    category: Optional[str]

    price: Decimal = Field(..., example=1000.00, decimal_places=2)
    closing_date: datetime
    time_left_seconds: int
    active: bool
    bids_count: int
    highest_bid: Decimal
    image: Optional[Any]
    watchlist: Optional[bool]

    @validator("active", pre=True)
    def set_active(cls, v, values):
        time_left_seconds = values.get("time_left_seconds")
        if v and time_left_seconds > 0:
            return True
        return False

    @validator("closing_date", pre=True)
    def assemble_closing_date(cls, v):
        return v.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @validator("auctioneer", pre=True)
    def show_auctioneer(cls, v):
        avatar = None
        if v.avatar_id:
            avatar = FileProcessor.generate_file_url(
                key=v.avatar_id,
                folder="avatars",
                content_type=v.avatar.resource_type,
            )
        return {
            "id": str(v.id),
            "name": v.full_name,
            "avatar": avatar,
        }

    @validator("category", pre=True)
    def show_category(cls, v):
        return v.name if v else "Other"

    @validator("image", pre=True)
    def assemble_image_url(cls, v):
        if v:
            file_url = FileProcessor.generate_file_url(
                key=v.id,
                folder="listings",
                content_type=v.resource_type,
            )
            return file_url
        return None

    class Config:
        orm_mode = True


class ListingDetailDataSchema(BaseModel):
    listing: ListingDataSchema
    related_listings: List[ListingDataSchema]


class ListingResponseSchema(ResponseSchema):
    data: ListingDetailDataSchema


class ListingsResponseSchema(ResponseSchema):
    data: List[ListingDataSchema]


# ------------------------------------------------------ #


# CATEGORIES
class CategoryDataSchema(BaseModel):
    name: str
    slug: str

    class Config:
        orm_mode = True


class CategoriesResponseSchema(ResponseSchema):
    data: List[CategoryDataSchema]


# ------------------------------------------------------ #


# BIDS #
class CreateBidSchema(BaseModel):
    amount: Decimal = Field(..., example=1000.00, decimal_places=2)


class BidDataSchema(BaseModel):
    user: dict = Field(..., example={"name": "John Doe", "avatar": "https://image.url"})
    amount: Decimal = Field(..., example=1000.00, decimal_places=2)
    created_at: datetime
    updated_at: datetime

    @validator("created_at", "updated_at", pre=True)
    def assemble_date(cls, v):
        return v.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @validator("user", pre=True)
    def show_user(cls, v):
        avatar = None
        if v.avatar_id:
            avatar = FileProcessor.generate_file_url(
                key=v.avatar_id,
                folder="avatars",
                content_type=v.avatar.resource_type,
            )
        return {"name": v.full_name, "avatar": avatar}

    class Config:
        orm_mode = True


class BidResponseSchema(ResponseSchema):
    data: BidDataSchema


class BidsResponseDataSchema(BaseModel):
    listing: str
    bids: List[BidDataSchema]


class BidsResponseSchema(ResponseSchema):
    data: BidsResponseDataSchema


# -------------------------------------------- #
