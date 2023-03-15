from chatting_with_the_guardian.database import ScopedSession
from chatting_with_the_guardian.models.article import Article, ArticleParagraph
from chatting_with_the_guardian.utils import get_front_page, get_article_text


def main():
    session = ScopedSession()

    # Get the front page
    article_urls = get_front_page()

    for article_url in list(set(article_urls)):
        # Get the article text
        article_text = get_article_text(article_url)

        if article_text is None:
            continue
        # Create a new article
        existing_article, article = Article.try_create(
            article_url, article_text, session
        )

        if existing_article and (not article):
            print(f"Article already exists: {existing_article}")
        if article and (not existing_article):
            print(f"Created new article: {article}")
            session.add(article)
            session.commit()

            paragraphs = ArticleParagraph.add_article_paragraphs(
                article_text, article, session
            )

            session.add_all(paragraphs)
            session.commit()
        if article and existing_article:
            print(f"Article already exists: {existing_article}")
            print(f"Updated article: {article}")
            session.add(article)
            session.add(existing_article)
            session.commit()

            paragraphs = ArticleParagraph.add_article_paragraphs(
                article_text, article, session
            )

            session.add_all(paragraphs)
            session.commit()


if __name__ == "__main__":
    main()
