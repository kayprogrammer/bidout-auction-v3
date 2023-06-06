from pydantic import validator, Field, EmailStr
from typing import Optional, List, Any

from app.api.utils.file_processors import FileProcessor
from .base import BaseModel, ResponseSchema
from uuid import UUID


# Site Details
class SiteDetailDataSchema(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    fb: str
    tw: str
    wh: str
    ig: str

    class Config:
        orm_mode = True


class SiteDetailResponseSchema(ResponseSchema):
    data: SiteDetailDataSchema


# -----------------------------


# Subscribers
class SubscriberSchema(BaseModel):
    email: EmailStr = Field(..., example="johndoe@example.com")

    class Config:
        orm_mode = True


class SubscriberResponseSchema(ResponseSchema):
    data: SubscriberSchema


# ----------------------


# Reviews
class ReviewsDataSchema(BaseModel):
    reviewer: Optional[Any] = Field(
        None, example={"name": "John Doe", "avatar": "https://image.url"}
    )
    text: str

    @validator("reviewer")
    def show_reviewer(cls, v):
        avatar = None
        if v.avatar_id:
            avatar = FileProcessor.generate_file_url(
                key=v.avatar_id,
                folder="reviewers",
                content_type=v.avatar.resource_type,
            )
        return {"name": v.full_name, "avatar": avatar}

    class Config:
        orm_mode = True


class ReviewsResponseSchema(ResponseSchema):
    data: List[ReviewsDataSchema]


# ---------------------------------
