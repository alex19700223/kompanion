"""server default for ui_language

Revision ID: a936b3426397
Revises: e0099bfe46a7
Create Date: 2026-10-07 13:42:00.656068

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a936b3426397'
down_revision: Union[str, Sequence[str], None] = 'e0099bfe46a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "users",
        "ui_language",
        existing_type=sa.VARCHAR(length=5),
        server_default="de",
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users",
        "ui_language",
        existing_type=sa.VARCHAR(length=5),
        server_default=None,
        existing_nullable=True,
    )
