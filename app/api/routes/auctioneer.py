from typing import Any, Optional
from starlite import Controller, get, post, put, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.listings import (
    ListingDataSchema,
    ListingsResponseSchema,
    BidDataSchema,
    BidsResponseDataSchema,
    BidsResponseSchema,
)

from app.api.schemas.auctioneer import (
    CreateListingSchema,
    UpdateListingSchema,
    CreateListingResponseSchema,
    CreateListingResponseDataSchema,
    UpdateProfileSchema,
    UpdateProfileResponseDataSchema,
    UpdateProfileResponseSchema,
    ProfileDataSchema,
    ProfileResponseSchema,
)
from app.common.exception_handlers import RequestError
from app.db.managers.listings import (
    category_manager,
    listing_manager,
    bid_manager,
)
from app.db.managers.accounts import user_manager
from app.db.managers.base import file_manager
from app.db.models.accounts import User


class ProfileView(Controller):
    path = "/"

    @get(
        summary="Get Profile",
        description="This endpoint gets the current user's profile.",
    )
    async def retrieve_profile(self, user: User) -> ProfileResponseSchema:
        data = ProfileDataSchema.from_orm(user)
        return ProfileResponseSchema(message="User details fetched!", data=data)

    @put(
        summary="Update Profile",
        description="This endpoint updates an authenticated user's profile. Note: use the returned upload_url to upload avatar to cloudinary",
    )
    async def update_profile(
        self, data: UpdateProfileSchema, user: User, db: AsyncSession
    ) -> UpdateProfileResponseSchema:
        file_type = data.file_type
        data = data.dict()
        if file_type:
            # Create file object
            file = await file_manager.create(db, {"resource_type": file_type})
            data.update({"avatar_id": file.id})
        data.pop("file_type", None)

        user = await user_manager.update(db, user, data)
        data = UpdateProfileResponseDataSchema.from_orm(user)
        return UpdateProfileResponseSchema(message="User updated!", data=data)


class AuctioneerListingsView(Controller):
    path = "/listings"

    @get(
        summary="Retrieve all listings by the current user",
        description="This endpoint retrieves all listings by the current user",
    )
    async def retrieve_listings(
        self, user: User, quantity: Optional[int], db: AsyncSession
    ) -> ListingsResponseSchema:
        listings = await listing_manager.get_by_auctioneer_id(db, user.id)

        if quantity:
            # Retrieve based on amount
            listings = listings[:quantity]
        data = [ListingDataSchema.from_orm(listing) for listing in listings]
        return ListingsResponseSchema(message="Auctioneer Listings fetched", data=data)

    @post(
        summary="Create a listing",
        description="This endpoint creates a new listing. Note: Use the returned upload_url to upload image to cloudinary",
    )
    async def create_listing(
        self, data: CreateListingSchema, user: User, db: AsyncSession
    ) -> CreateListingResponseSchema:
        category = data.category

        if not category == "other":
            category = await category_manager.get_by_slug(db, category)
            if not category:
                # Return a data validation error
                return RequestError(
                    err_msg="Invalid entry",
                    data={"category": "Invalid category"},
                    status_code=422,
                )
        else:
            category = None

        data = data.dict()
        data.update(
            {
                "auctioneer_id": user.id,
                "category_id": category.id if category else None,
            }
        )
        data.pop("category", None)

        # Create file object
        file = await file_manager.create(db, {"resource_type": data["file_type"]})
        data.update({"image_id": file.id})
        data.pop("file_type")

        listing = await listing_manager.create(db, data)
        data = CreateListingResponseDataSchema.from_orm(listing)
        return CreateListingResponseSchema(
            message="Listing created successfully", data=data
        )

    @patch(
        "/{slug:str}",
        summary="Update a listing",
        description="This endpoint update a particular listing.",
    )
    async def update_listing(
        self, slug: str, data: UpdateListingSchema, user: User, db: AsyncSession
    ) -> CreateListingResponseSchema:
        category = data.category

        listing = await listing_manager.get_by_slug(db, slug)
        if not listing:
            return RequestError(err_msg="Listing does not exist!", status_code=404)

        if user.id != listing.auctioneer_id:
            return RequestError(err_msg="This listing doesn't belong to you!")

        # Remove keys with values of None
        data = data.dict()
        data = {k: v for k, v in data.items() if v not in (None, "")}

        if category:
            if not category == "other":
                category = await category_manager.get_by_slug(db, category)
                if not category:
                    # Return a data validation error
                    return RequestError(
                        err_msg="Invalid entry",
                        data={"category": "Invalid category"},
                        status_code=422,
                    )
            else:
                category = None

            data.update({"category_id": category.id if category else None})
            data.pop("category", None)

        file_type = data.get("file_type")
        if file_type:
            await file_manager.delete(db, listing.image)
            # Create file object
            file = await file_manager.create(db, {"resource_type": file_type})
            data.update({"image_id": file.id})
        data.pop("file_type", None)

        listing = await listing_manager.update(db, listing, data)
        data = CreateListingResponseDataSchema.from_orm(listing)
        return CreateListingResponseSchema(
            message="Listing updated successfully", data=data
        )

    @get(
        "/{slug:str}/bids",
        summary="Retrieve all bids in a listing (current user)",
        description="This endpoint retrieves all bids in a particular listing by the current user.",
    )
    async def retrieve_bids(
        self, slug: str, user: User, db: AsyncSession
    ) -> BidsResponseSchema:
        # Get listing by slug
        listing = await listing_manager.get_by_slug(db, slug)
        if not listing:
            return RequestError(err_msg="Listing does not exist!", status_code=404)

        # Ensure the current user is the listing's owner
        if user.id != listing.auctioneer_id:
            return RequestError(err_msg="This listing doesn't belong to you!")

        bids = await bid_manager.get_by_listing_id(db, listing.id)
        data = BidsResponseDataSchema(
            listing=listing.name,
            bids=[BidDataSchema.from_orm(bid) for bid in bids],
        )
        return BidsResponseSchema(message="Listing Bids fetched", data=data)


auctioneer_handlers = [ProfileView, AuctioneerListingsView]
