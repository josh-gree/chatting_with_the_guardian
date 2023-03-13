import hashlib
from typing import Optional, Tuple

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
                return new_version_of_article, existing_article
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

    __table_args__ = (
        UniqueConstraint(
            "paragraph_text", "order", name="uq_article_paragraphs_text_order"
        ),
    )