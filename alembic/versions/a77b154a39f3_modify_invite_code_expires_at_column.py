"""modify_invite_code_expires_at_column

Revision ID: a77b154a39f3
Revises: b5fbeef75200
Create Date: 2025-06-14 00:28:43.548619

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'a77b154a39f3'
down_revision = 'b5fbeef75200'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'teams',
        'invite_code_expires_at',
        type_=postgresql.TIMESTAMP(timezone=True),
        postgresql_using='invite_code_expires_at AT TIME ZONE \'UTC\'',
        nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        'teams',
        'invite_code_expires_at',
        type_=sa.DateTime(),
        postgresql_using='invite_code_expires_at',
        nullable=True
    )
