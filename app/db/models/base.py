import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.core.database import Base


class BaseModel(Base):
    __abstract__ = True
    pkid: Mapped[int] = Column(Integer, primary_key=True)
    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = Column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )


class File(BaseModel):
    __tablename__ = "files"

    resource_type: Mapped[str] = Column(String)
    user_avatar: Mapped["User"] = relationship(
        "User", foreign_keys="User.avatar_id", back_populates="avatar", uselist=False
    )
    # listing_image = relationship(
    #     "Listing",
    #     foreign_keys="Listing.image_id",
    #     back_populates="image",
    #     uselist=False,
    # )

class GuestUser(BaseModel):
    __tablename__ = "guestusers"
