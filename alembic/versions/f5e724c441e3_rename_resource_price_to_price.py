"""rename resource price to price

Revision ID: f5e724c441e3
Revises: ec633df6d463
Create Date: 2026-08-30 14:54:56.335059

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f5e724c441e3"
down_revision: Union[str, Sequence[str], None] = "ec633df6d463"
branch_labels = None
depends_on = None



def upgrade() -> None:

    op.alter_column(
        "forest_zones",
        "resource_price",
        new_column_name="price",
        existing_type=sa.Numeric(
            precision=10,
            scale=2
        )
    )



def downgrade() -> None:

    op.alter_column(
        "forest_zones",
        "price",
        new_column_name="resource_price",
        existing_type=sa.Numeric(
            precision=10,
            scale=2
        )
    )