from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'f12acd2668d7'
down_revision: Union[str, None] = 'a77b154a39f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

taskstatus_enum = postgresql.ENUM('OPEN', 'IN_PROGRESS', 'DONE', name='taskstatus')


def upgrade() -> None:
    taskstatus_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'task_status_history',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('changed_by_id', sa.Integer(), nullable=False),
        sa.Column('new_status', postgresql.ENUM('OPEN', 'IN_PROGRESS', 'DONE', name='taskstatus', create_type=False),
                  nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['changed_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id']),
    )


def downgrade() -> None:
    op.drop_table('task_status_history')

    taskstatus_enum.drop(op.get_bind(), checkfirst=True)
