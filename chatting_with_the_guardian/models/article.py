import hashlib
from typing import List, Optional, Tuple
from pgvector.sqlalchemy import Vector

from datetime import datetime
from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    Date,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

from chatting_with_the_guardian.utils import parse_url

Base = declarative_base()


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    hash = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_to = Column(DateTime, nullable=True)
    paragraphs = relationship("ArticleParagraph", back_populates="article")
    summary = relationship("ArticleSummary", back_populates="article")

    __table_args__ = (
        CheckConstraint(
            "valid_to IS NULL OR valid_to > created_at", name="valid_to_gt_created_at"
        ),
        UniqueConstraint(
            "date", "category", "slug", "hash", name="uq_article_date_category_slug"
        ),
    )

    def __repr__(self):
        out = f"""
        Article(
            category={self.category}, 
            slug={self.slug}, 
            hash={self.hash},
            date={self.date}, 
            created_at={self.created_at}, 
            valid_to={self.valid_to}
        )
        """
        return out

    @classmethod
    def try_create(
        cls, url: str, text: str, session
    ) -> Tuple[Optional["Article"], Optional["Article"]]:
        parsed_url = parse_url(url)
        hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        if (
            existing_article := session.query(cls)
            .filter(
                cls.category == parsed_url["category"],
                cls.slug == parsed_url["slug"],
                cls.date == parsed_url["date"],
            )
            .order_by(cls.created_at.desc())
            .first()
        ):
            if existing_article.hash == hash:
                return existing_article, None
            else:
                existing_article.valid_to = datetime.utcnow()
                new_version_of_article = Article(
                    category=parsed_url["category"],
                    slug=parsed_url["slug"],
                    hash=hash,
                    date=parsed_url["date"],
                )
                return existing_article, new_version_of_article
        else:
            new_article = Article(
                category=parsed_url["category"],
                slug=parsed_url["slug"],
                hash=hash,
                date=parsed_url["date"],
            )
            return None, new_article


class ArticleParagraph(Base):
    __tablename__ = "article_paragraphs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    paragraph_text = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    article = relationship("Article", back_populates="paragraphs")
    embedding = Column(Vector(1536))

    __table_args__ = (
        UniqueConstraint(
            "paragraph_text",
            "order",
            "article_id",
            name="uq_article_paragraphs_text_order",
        ),
    )

    @classmethod
    def add_article_paragraphs(
        cls, article_text: str, article: Article, session
    ) -> List["ArticleParagraph"]:
        paragraphs = []
        for ind, p in enumerate(article_text.split("\n")):
            if p:
                paragraph = ArticleParagraph(
                    article_id=article.id, paragraph_text=p, order=ind
                )
                paragraphs.append(paragraph)

        return paragraphs


class ArticleSummary(Base):
    __tablename__ = "article_summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    summary_text = Column(String, nullable=False)
    article = relationship("Article", back_populates="summary")
    embedding = Column(Vector(1536))
