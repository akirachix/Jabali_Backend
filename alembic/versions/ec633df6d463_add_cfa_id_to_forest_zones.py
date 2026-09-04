"""add cfa id to forest zones

Revision ID: ec633df6d463
Revises: c995db6b0e70
Create Date: 2026-08-30 14:47:43.537307

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ec633df6d463"
down_revision: Union[str, Sequence[str], None] = "c995db6b0e70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add CFA relationship to forest_zones.
    """

    op.add_column(
        "forest_zones",
        sa.Column(
            "community_forest_association_id",
            sa.UUID(),
            nullable=True
        )
    )


    op.create_index(
        op.f(
            "ix_forest_zones_community_forest_association_id"
        ),
        "forest_zones",
        [
            "community_forest_association_id"
        ],
        unique=False
    )


    op.create_foreign_key(
        "fk_forest_zones_cfa",
        "forest_zones",
        "community_forest_associations",
        [
            "community_forest_association_id"
        ],
        [
            "community_forest_association_id"
        ]
    )



def downgrade() -> None:
    """
    Remove CFA relationship from forest_zones.
    """

    op.drop_constraint(
        "fk_forest_zones_cfa",
        "forest_zones",
        type_="foreignkey"
    )


    op.drop_index(
        op.f(
            "ix_forest_zones_community_forest_association_id"
        ),
        table_name="forest_zones"
    )


    op.drop_column(
        "forest_zones",
        "community_forest_association_id"
    )