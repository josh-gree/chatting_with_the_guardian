from chatting_with_the_guardian.database import ScopedSession
from chatting_with_the_guardian.models.article import Article, NamedEntity


def main():
    session = ScopedSession()

    articles_without_named_entities = session.query(Article).filter(
        ~Article.named_entites.any()
    )

    for article in articles_without_named_entities:
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


if __name__ == "__main__":
    main()
