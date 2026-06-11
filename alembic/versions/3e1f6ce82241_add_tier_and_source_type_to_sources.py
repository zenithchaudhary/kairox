from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '3e1f6ce82241'
down_revision: Union[str, None] = '98cb81acd35f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('sources', sa.Column('tier', sa.Integer(), nullable=True))
    op.add_column('sources', sa.Column('source_type', sa.String(), nullable=True))

    op.execute("UPDATE sources SET tier = 5 WHERE tier IS NULL")
    op.execute("UPDATE sources SET source_type = 'rss' WHERE source_type IS NULL")

    op.alter_column('sources', 'tier', nullable=False)
    op.alter_column('sources', 'source_type', nullable=False)

def downgrade() -> None:
    op.drop_column('sources', 'source_type')
    op.drop_column('sources', 'tier')