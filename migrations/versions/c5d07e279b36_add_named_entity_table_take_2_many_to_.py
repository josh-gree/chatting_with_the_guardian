"""add named entity table take 2 many to many

Revision ID: c5d07e279b36
Revises: 5e06a4a5dc23
Create Date: 2023-03-16 22:05:20.663947

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5d07e279b36'
down_revision = '5e06a4a5dc23'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('named_entities',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('entity_text', sa.String(), nullable=False),
    sa.Column('entity_type', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('article_named_entity_association',
    sa.Column('article_id', sa.Integer(), nullable=True),
    sa.Column('named_entity_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
    sa.ForeignKeyConstraint(['named_entity_id'], ['named_entities.id'], )
    )
    op.drop_table('article_named_entities')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('article_named_entities',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('article_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('entity_text', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('entity_type', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name='article_named_entities_article_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='article_named_entities_pkey')
    )
    op.drop_table('article_named_entity_association')
    op.drop_table('named_entities')
    # ### end Alembic commands ###