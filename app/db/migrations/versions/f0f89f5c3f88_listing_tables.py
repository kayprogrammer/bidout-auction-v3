"""listing tables

Revision ID: f0f89f5c3f88
Revises: 2673fdb9002d
Create Date: 2023-06-14 20:25:49.429267

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f0f89f5c3f88"
down_revision = "2673fdb9002d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "categories",
        sa.Column("name", sa.String(length=30), nullable=True),
        sa.Column("slug", sa.String(), nullable=True),
        sa.Column("pkid", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("pkid"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "listings",
        sa.Column("auctioneer_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=70), nullable=True),
        sa.Column("slug", sa.String(), nullable=True),
        sa.Column("desc", sa.Text(), nullable=True),
        sa.Column("category_id", sa.UUID(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("closing_date", sa.DateTime(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.Column("image_id", sa.UUID(), nullable=True),
        sa.Column("pkid", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["auctioneer_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["category_id"], ["categories.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["image_id"], ["files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("pkid"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("image_id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "bids",
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("listing_id", sa.UUID(), nullable=True),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("pkid", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("pkid"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("listing_id", "amount", name="unique_listing_amount_bids"),
        sa.UniqueConstraint("user_id", "listing_id", name="unique_user_listing_bids"),
    )
    op.create_table(
        "watchlists",
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("listing_id", sa.UUID(), nullable=True),
        sa.Column("session_key", sa.String(), nullable=True),
        sa.Column("pkid", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("pkid"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint(
            "session_key", "listing_id", name="unique_session_key_listing_watchlists"
        ),
        sa.UniqueConstraint(
            "user_id", "listing_id", name="unique_user_listing_watchlists"
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("watchlists")
    op.drop_table("bids")
    op.drop_table("listings")
    op.drop_table("categories")
    # ### end Alembic commands ###
