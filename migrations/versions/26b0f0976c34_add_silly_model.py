"""add silly model

Revision ID: 26b0f0976c34
Revises: 0e0a05f049db
Create Date: 2023-03-13 22:06:24.843710

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26b0f0976c34'
down_revision = '0e0a05f049db'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('foos',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('foos')
    # ### end Alembic commands ###