import bs4
import requests
from datetime import datetime
from urllib.parse import urlparse
from boto3.session import Session

from chatting_with_the_guardian.consts import (
    ACCESS_ID,
    SECRET_KEY,
    DO_SPACES_ENDPOINT_URL,
)

ROOT_URL = "https://www.theguardian.com"


def parse_url(url: str) -> dict:
    parsed_url = urlparse(url)
    try:
        slug = parsed_url.path.split("/")[5]
        category = parsed_url.path.split("/")[1]
        date_part = parsed_url.path.split("/")[2:5]
        date = datetime.strptime("-".join(date_part), "%Y-%b-%d").date()
    except (IndexError, ValueError):
        raise ValueError(f"Could not parse URL: {url}")

    return {"slug": slug, "category": category, "date": date}


def is_article_url(href: str, root_url: str) -> bool:
    starts_with_root = href.startswith(root_url)

    parsed_url = urlparse(href)

    try:
        date_part = parsed_url.path.split("/")[2:5]
        date_part = datetime.strptime("-".join(date_part), "%Y-%b-%d").date()

        has_date = True

    except (IndexError, ValueError):
        has_date = False

    return starts_with_root and has_date


def get_page(section: str) -> dict:
    resp = requests.get(ROOT_URL + f"/{section}")
    soup = bs4.BeautifulSoup(resp.content, features="html.parser")

    article_urls = [
        article.attrs["href"]
        for article in soup.find_all("a", href=True)
        if is_article_url(article.attrs["href"], ROOT_URL)
    ]
    return article_urls


def get_article_text(url: str) -> str:
    resp = requests.get(url)
    soup = bs4.BeautifulSoup(resp.content, features="html.parser")
    try:
        ps = [
            p.text
            for p in soup.find("div", {"id": "maincontent"}).div.find_all(
                "p", recursive=False
            )
        ]
    except AttributeError:
        return None

    return "\n".join(ps)


def upload_text_to_bucket(text: str, bucket_name: str, blob_name: str):
    session = Session()
    client = session.client(
        "s3",
        endpoint_url=DO_SPACES_ENDPOINT_URL,
        aws_access_key_id=ACCESS_ID,
        aws_secret_access_key=SECRET_KEY,
    )

    client.put_object(Body=text, Bucket=bucket_name, Key=blob_name)
