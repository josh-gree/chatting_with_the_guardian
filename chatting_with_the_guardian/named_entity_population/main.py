from datetime import datetime

from chatting_with_the_guardian.database import ScopedSession
from chatting_with_the_guardian.models.article import Article, NamedEntity


def main():
    session = ScopedSession()

    articles_without_named_entities = session.query(Article).filter(
        ~Article.named_entites.any()
    )

    N = articles_without_named_entities.count()

    print("-" * 80)
    print("\n\n")
    print(f"Found {N} articles without named entities")
    print("-" * 80)

    durations = []
    for ind, article in enumerate(articles_without_named_entities):
        if article.full_text != "":
            print("-" * 80)
            print("\n\n")
            print(f"Processing article {ind} of {N}")
            print("-" * 80)

            start = datetime.now()

            named_entities = [
                NamedEntity(entity_text=entity_text, entity_type=entity_type)
                if session.query(NamedEntity)
                .filter(
                    NamedEntity.entity_text == entity_text,
                    NamedEntity.entity_type == entity_type,
                )
                .count()
                == 0
                else session.query(NamedEntity)
                .filter(
                    NamedEntity.entity_text == entity_text,
                    NamedEntity.entity_type == entity_type,
                )
                .first()
                for entity_text, entity_type in article.get_named_entities()
            ]

            session.add_all(named_entities)

            [ne.articles.append(article) for ne in named_entities]
            article.named_entites += named_entities

            session.commit()

            end = datetime.now()

            duration = end - start
            print(f"Processing took {duration.seconds} seconds")

            durations.append(duration.seconds)

            avg_duration = sum(durations) / len(durations)
            print(f"Average processing time is {avg_duration} seconds")

            estimated_time_left = (N - ind) * avg_duration
            print(f"Estimated time left is {estimated_time_left / 60} minutes")


if __name__ == "__main__":
    main()
