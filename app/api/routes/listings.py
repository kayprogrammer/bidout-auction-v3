from starlite import Controller, Provide, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.listings import (
    AddOrRemoveWatchlistSchema,
    ListingDataSchema,
    ListingsResponseSchema,
    ListingDetailDataSchema,
    ListingResponseSchema,
    CategoryDataSchema,
    CategoriesResponseSchema,
    CreateBidSchema,
    BidDataSchema,
    BidsResponseDataSchema,
    BidsResponseSchema,
    BidResponseSchema,
    ResponseSchema,
)
from app.api.dependencies import get_client_id
from app.db.managers.listings import (
    listing_manager,
    bid_manager,
    watchlist_manager,
    category_manager,
)
from app.common.exception_handlers import RequestError

from app.api.utils.validators import validate_quantity
from app.db.models.accounts import User


class ListingsView(Controller):
    path = "/"
    dependencies = {"client_id": Provide(get_client_id)}

    @get(
        summary="Retrieve all listings",
        description="This endpoint retrieves all listings",
        parameter={"name": "quantity", "location": "query", "schema": int},
    )
    async def retrieve_listings(
        self, request, db: AsyncSession, client_id: str, quantity: int = None
    ) -> ListingsResponseSchema:
        listings = await listing_manager.get_all(db)
        if quantity:
            # Retrieve based on amount
            listings = listings[:quantity]

        data = [
            ListingDataSchema(
                watchlist=True
                if watchlist_manager.get_by_user_id_or_session_key_and_listing_id(
                    db, client_id, listing.id
                )
                else False,
                bids_count=listing.bids_count,
                highest_bid=listing.highest_bid,
                time_left_seconds=listing.time_left_seconds,
                **listing.__dict__
            ).dict()
            for listing in listings
        ]
        return ListingResponseSchema(message="Listings fetched", data=data)

    @get(
        "/<slug:str>",
        summary="Retrieve listing's detail",
        description="This endpoint retrieves detail of a listing",
        response={"application/json": ListingResponseSchema},
    )
    async def retrieve_listing_detail(
        self, slug: str, db: AsyncSession
    ) -> ListingResponseSchema:
        listing = listing_manager.get_by_slug(db, slug)
        if not listing:
            raise RequestError(err_msg="Listing does not exist!", status_code=404)

        related_listings = listing_manager.get_related_listings(
            db, listing.category_id, slug
        )[:3]
        data = ListingDetailDataSchema(
            listing=ListingDataSchema.from_orm(listing),
            related_listings=[
                ListingDataSchema.from_orm(related_listing)
                for related_listing in related_listings
            ],
        ).dict()
        return ListingResponseSchema.success(
            message="Listing details fetched", data=data
        )


class ListingsByWatchListView(Controller):
    path = "/watchlist"

    @get(
        summary="Retrieve all listings by users watchlist",
        description="This endpoint retrieves all listings",
    )
    async def watchlist(
        self, db: AsyncSession, client_id: str
    ) -> ListingsResponseSchema:
        watchlists = watchlist_manager.get_by_user_id_or_session_key(db, client_id)
        data = [
            ListingDataSchema(
                watchlist=True,
                bids_count=watchlist.listing.bids_count,
                highest_bid=watchlist.listing.highest_bid,
                time_left_seconds=watchlist.listing.time_left_seconds,
                **watchlist.listing.__dict__
            ).dict()
            for watchlist in watchlists
        ]
        return ListingsResponseSchema(message="Watchlists Listings fetched", data=data)

    @post(
        summary="Add or Remove listing from a users watchlist",
        description="This endpoint adds or removes a listing from a user's watchlist, authenticated or not.",
    )
    async def post(
        self,
        request,
        slug: str,
        data: AddOrRemoveWatchlistSchema,
        db: AsyncSession,
        client_id: str,
    ) -> ResponseSchema:
        listing = listing_manager.get_by_slug(db, slug)
        if not listing:
            raise RequestError(err_msg="Listing does not exist!", status_code=404)

        data_entry = {"session_key": client_id, "listing_id": listing.id}
        if hasattr(user, "email"):
            # Here we know its a user object and not a session key string, now we can retrieve id.
            user = user.id
            del data_entry["session_key"]
            data_entry["user_id"] = user

        watchlist = watchlist_manager.get_by_user_id_or_session_key_and_listing_id(
            db, str(user), listing.id
        )

        resp_message = "Listing removed from user watchlist"
        status_code = 200
        if not watchlist:
            watchlist_manager.create(db, data_entry)
            resp_message = "Listing added to user watchlist"
            status_code = 201
        else:
            watchlist_manager.delete(db, watchlist)

        return ResponseSchema(message=resp_message)


class CategoryListView(Controller):
    @get(
        summary="Retrieve all categories",
        description="This endpoint retrieves all categories",
    )
    async def get(self, request, db: AsyncSession) -> CategoriesResponseSchema:
        categories = category_manager.get_all(db)
        data = [CategoryDataSchema.from_orm(category) for category in categories]
        return CategoriesResponseSchema(message="Categories fetched", data=data)


class ListingsByCategoryView(Controller):
    @get(
        summary="Retrieve all listings by category",
        description="This endpoint retrieves all listings in a particular category. Use slug 'other' for category other",
    )
    async def get(
        self, request, slug: str, db: AsyncSession, client_id: str
    ) -> ListingsResponseSchema:
        # listings with category 'other' have category column as null
        category = None
        if slug != "other":
            category = category_manager.get_by_slug(db, slug)
            if not category:
                raise RequestError(err_msg="Invalid category", status_code=404)

        listings = listing_manager.get_by_category(db, category)
        data = [
            ListingDataSchema(
                watchlist=True
                if watchlist_manager.get_by_user_id_or_session_key_and_listing_id(
                    db, client_id, listing.id
                )
                else False,
                bids_count=listing.bids_count,
                highest_bid=listing.highest_bid,
                time_left_seconds=listing.time_left_seconds,
                **listing.__dict__
            ).dict()
            for listing in listings
        ]
        return ListingsResponseSchema(message="Category Listings fetched", data=data)


class BidsView(Controller):
    @get(
        summary="Retrieve bids in a listing",
        description="This endpoint retrieves at most 3 bids from a particular listing.",
    )
    async def get(self, request, db: AsyncSession, slug: str) -> BidsResponseSchema:
        listing = listing_manager.get_by_slug(db, slug)
        if not listing:
            raise RequestError(err_msg="Listing does not exist!", status_code=404)

        bids = bid_manager.get_by_listing_id(db, listing.id)[:3]

        data = BidsResponseDataSchema(
            listing=listing.name,
            bids=[BidDataSchema.from_orm(bid) for bid in bids],
        ).dict()
        return BidsResponseSchema(message="Listing Bids fetched", data=data)

    @post(
        summary="Add a bid to a listing",
        description="This endpoint adds a bid to a particular listing.",
    )
    async def post(
        self, request, slug: str, data: CreateBidSchema, db: AsyncSession, user: User
    ) -> BidResponseSchema:
        listing = listing_manager.get_by_slug(db, slug)
        if not listing:
            raise RequestError(err_msg="Listing does not exist!", status_code=404)

        amount = data["amount"]
        if user.id == listing.auctioneer_id:
            raise RequestError(
                err_msg="You cannot bid your own product!", status_code=403
            )
        elif not listing.active:
            raise RequestError(err_msg="This auction is closed!", status_code=410)
        elif listing.time_left < 1:
            raise RequestError(
                err_msg="This auction is expired and closed!", status_code=410
            )
        elif amount < listing.price:
            raise RequestError(
                err_msg="Bid amount cannot be less than the bidding price!"
            )
        elif amount <= listing.highest_bid:
            raise RequestError(err_msg="Bid amount must be more than the highest bid!")

        bid = bid_manager.get_by_user_and_listing_id(db, user.id, listing.id)
        if bid:
            bid = bid_manager.update(db, bid, {"amount": amount})
        else:
            bid = bid_manager.create(
                db,
                {"user_id": user.id, "listing_id": listing.id, "amount": amount},
            )

        data = BidDataSchema.from_orm(bid).dict()
        return BidResponseSchema(message="Bid added to listing", data=data)


listings_router = [
    ListingsView,
    ListingsByWatchListView,
    CategoryListView,
    ListingsByCategoryView,
    BidsView,
]

# listings_router.add_route(ListingsView.as_view(), "/")
# listings_router.add_route(CategoryListView.as_view(), "/categories")
# listings_router.add_route(ListingsByCategoryView.as_view(), "/categories/<slug>")
# listings_router.add_route(BidsView.as_view(), "/<slug>/bids")
