"""add blob uuid

Revision ID: 7a1f41ae3b98
Revises: 824b75e2afda
Create Date: 2023-05-08 15:05:50.017791

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a1f41ae3b98'
down_revision = '824b75e2afda'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('article_paragraphs', sa.Column('blob_uuid', sa.String(), nullable=True))
    op.drop_constraint('uq_article_paragraphs_text_order', 'article_paragraphs', type_='unique')
    op.create_unique_constraint('uq_article_paragraphs_text_order', 'article_paragraphs', ['paragraph_text', 'order', 'article_id', 'blob_uuid'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uq_article_paragraphs_text_order', 'article_paragraphs', type_='unique')
    op.create_unique_constraint('uq_article_paragraphs_text_order', 'article_paragraphs', ['paragraph_text', 'order', 'article_id'])
    op.drop_column('article_paragraphs', 'blob_uuid')
    # ### end Alembic commands ###