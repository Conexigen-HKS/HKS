"""Add location to company offers

Revision ID: 86dea6ae1a4b
Revises: 204b0cc5b2bd
Create Date: 2024-11-28 10:51:22.128133

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86dea6ae1a4b'
down_revision: Union[str, None] = '204b0cc5b2bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('professional_profile', sa.Column('location_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'professional_profile', 'locations', ['location_id'], ['id'])
    op.drop_column('professional_profile', 'preferred_location')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('professional_profile', sa.Column('preferred_location', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'professional_profile', type_='foreignkey')
    op.drop_column('professional_profile', 'location_id')
    # ### end Alembic commands ###
