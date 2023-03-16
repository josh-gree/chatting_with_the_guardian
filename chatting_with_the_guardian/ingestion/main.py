from chatting_with_the_guardian.database import ScopedSession
from chatting_with_the_guardian.models.article import Article, ArticleParagraph
from chatting_with_the_guardian.utils import get_page, get_article_text


def main():
    session = ScopedSession()

    # Get the front page

    sections = [
        "uk",
        "uk-news",
        "politics",
        "education",
        "uk/media",
        "society",
        "law",
        "uk/scotland",
        "uk/wales",
        "uk/northernireland",
        "world",
        "world/europe-news",
        "us-news",
        "world/asia",
        "australia-news",
        "world/middleeast",
        "world/africa",
        "inequality",
        "global-development",
        "climate-crisis",
        "uk/business",
        "business/economics",
        "business/banking",
        "uk/money",
        "money/property",
        "money/pensions",
        "money/savings",
        "money/debt",
        "money/work-and-careers",
        "business/stock-markets",
        "uk/business-to-business",
        "business/retail",
        "uk/environment",
        "environment/climate-crisis",
        "environment/wildlife",
        "environment/energy",
        "environment/pollution",
        "education/schools",
        "science",
        "uk/technology",
        "global-development",
        "obituaries",
    ]

    for section in sections:
        article_urls = get_page(section)

        for article_url in list(set(article_urls)):
            # Get the article text
            article_text = get_article_text(article_url)

            if article_text is None:
                continue
            # Create a new article - TODO: this returning two values is a bit of a mess!!

            existing_article, new_article = Article.try_create(
                article_url, article_text, session
            )

            if existing_article and new_article is None:
                print(f"Article already exists: {existing_article}")

            elif existing_article and new_article:
                print(f"Article already exists: {existing_article}")
                print(f"Updated article: {new_article}")

                if (
                    session.query(Article)
                    .filter(Article.hash == new_article.hash)
                    .count()
                    == 1
                ):
                    print("Article text has reverted to previous version.")
                    continue

                session.add(new_article)
                session.add(existing_article)
                session.commit()

                paragraphs = ArticleParagraph.add_article_paragraphs(
                    article_text, new_article, session
                )

                session.add_all(paragraphs)
                session.commit()

            elif new_article and existing_article is None:
                print(f"Created new article: {new_article}")
                session.add(new_article)
                session.commit()

                paragraphs = ArticleParagraph.add_article_paragraphs(
                    article_text, new_article, session
                )

                session.add_all(paragraphs)
                session.commit()


if __name__ == "__main__":
    main()
