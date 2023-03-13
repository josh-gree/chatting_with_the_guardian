import time
import pytest
import docker

from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from alembic.config import Config
from alembic import command

from chatting_with_the_guardian.models.article import Article, ArticleParagraph


@pytest.fixture(scope="session")
def postgres_container():
    # Start Postgres container
    client = docker.from_env()
    container = client.containers.run(
        "postgres:latest",
        detach=True,
        environment={"POSTGRES_PASSWORD": "password"},
        ports={"5432/tcp": 0},
    )

    # Get container IP and port
    container.reload()
    container_port = container.attrs["NetworkSettings"]["Ports"]["5432/tcp"][0][
        "HostPort"
    ]
    connection_string = (
        f"postgresql://postgres:password@localhost:{container_port}/postgres"
    )

    # Wait for Postgres to start
    engine = create_engine(connection_string)
    while True:
        try:
            engine.connect()
            break
        except Exception as err:
            pass
    # Return connection string
    yield connection_string

    # Stop container
    container.stop()


@pytest.fixture(scope="module")
def db_engine(postgres_container):
    engine = create_engine(postgres_container)
    alembic_cfg = Config()
    alembic_cfg.set_main_option("sqlalchemy.url", postgres_container)
    alembic_cfg.set_main_option("script_location", "migrations")
    command.upgrade(alembic_cfg, "head")
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


def test_create_article(db_session):
    article = Article(
        category="Technology", slug="new-article", hash="some-hash", date=date.today()
    )
    db_session.add(article)
    result = db_session.query(Article).filter(Article.slug == "new-article").first()
    assert result is not None


def test_create_article_unique_constraint(db_session):
    article_first = Article(
        category="Technology", slug="new-article", hash="some-hash", date=date.today()
    )
    db_session.add(article_first)
    article_dupe = Article(
        category="Technology", slug="new-article", hash="some-hash", date=date.today()
    )
    db_session.add(article_dupe)
    with pytest.raises(Exception):
        db_session.commit()


def test_try_create_same_text(db_session):
    _, article_first = Article.try_create(
        url="https://www.theguardian.com/media/2023/mar/11/lineker-row-theatens-topple-bbc-chiefs-and-hit-tory-asylum-plans",
        text="some text",
        session=db_session,
    )
    db_session.add(article_first)

    article_old, _ = Article.try_create(
        url="https://www.theguardian.com/media/2023/mar/11/lineker-row-theatens-topple-bbc-chiefs-and-hit-tory-asylum-plans",
        text="some text",
        session=db_session,
    )
    assert article_old is article_first


def test_try_create_different_text(db_session):
    _, article_first = Article.try_create(
        url="https://www.theguardian.com/media/2023/mar/11/lineker-row-theatens-topple-bbc-chiefs-and-hit-tory-asylum-plans",
        text="some text",
        session=db_session,
    )
    db_session.add(article_first)

    assert article_first.valid_to is None

    new_version_of_article, existing_article = Article.try_create(
        url="https://www.theguardian.com/media/2023/mar/11/lineker-row-theatens-topple-bbc-chiefs-and-hit-tory-asylum-plans",
        text="some other text",
        session=db_session,
    )
    db_session.add(new_version_of_article)
    db_session.add(existing_article)

    assert existing_article is article_first
    assert article_first.valid_to is not None

    assert new_version_of_article.hash != article_first.hash

    assert db_session.query(Article).count() == 2

    assert new_version_of_article.created_at - existing_article.valid_to <= timedelta(
        milliseconds=100
    )  # TODO: fix this - should be equal!!


def test_article_article_paragraph_relationship(db_session):
    article = Article(
        category="Technology", slug="new-article", hash="some-hash", date=date.today()
    )
    db_session.add(article)
    assert article.paragraphs == []

    paragraph = ArticleParagraph(article=article, paragraph_text="some text", order=1)
    db_session.add(paragraph)

    assert article.paragraphs == [paragraph]
    assert paragraph.article == article


def test_paragraph_unique_constraint(db_session):
    article = Article(
        category="Technology", slug="new-article", hash="some-hash", date=date.today()
    )
    db_session.add(article)
    paragraph_first = ArticleParagraph(
        article=article, paragraph_text="some text", order=1
    )
    db_session.add(paragraph_first)
    paragraph_dupe = ArticleParagraph(
        article=article, paragraph_text="some text", order=1
    )
    db_session.add(paragraph_dupe)
    with pytest.raises(Exception):
        db_session.commit()
