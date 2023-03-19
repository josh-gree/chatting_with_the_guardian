import torch

from chatting_with_the_guardian.database import ScopedSession
from chatting_with_the_guardian.models.article import ArticleParagraph

from transformers import DistilBertTokenizer, DistilBertModel

tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
model = DistilBertModel.from_pretrained("distilbert-base-uncased")


def get_bert_embedding(text, model, tokenizer):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    cls_embedding = outputs.last_hidden_state[:, 0, :]
    return cls_embedding


def main():
    session = ScopedSession()

    ps = session.query(ArticleParagraph).all()

    ps = [p for p in ps if p.embedding is None]

    N = len(ps)
    for ind, p in enumerate(ps):
        print(f"{ind}/{N}")
        p_embed = get_bert_embedding(p.paragraph_text, model, tokenizer)
        p.embedding = p_embed[0]

        if ind % 100 == 0:
            session.commit()


if __name__ == "__main__":
    main()
