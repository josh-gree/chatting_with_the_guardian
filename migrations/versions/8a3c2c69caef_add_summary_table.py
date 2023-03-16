"""add summary table

Revision ID: 8a3c2c69caef
Revises: 862d1aabf9c4
Create Date: 2023-03-16 20:42:39.215822

"""
from alembic import op
import sqlalchemy as sa

from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = "8a3c2c69caef"
down_revision = "862d1aabf9c4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "article_summaries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("article_id", sa.Integer(), nullable=False),
        sa.Column("summary_text", sa.String(), nullable=False),
        sa.Column("embedding", Vector(dim=1536), nullable=True),
        sa.ForeignKeyConstraint(
            ["article_id"],
            ["articles.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "article_paragraphs",
        sa.Column("embedding", Vector(dim=1536), nullable=True),
    )
    op.drop_column("articles", "embedding")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "articles",
        sa.Column("embedding", sa.NullType(), autoincrement=False, nullable=True),
    )
    op.drop_column("article_paragraphs", "embedding")
    op.drop_table("article_summaries")
    # ### end Alembic commands ###