import pytest

from functools import partial
from datetime import date
from chatting_with_the_guardian.utils import (
    get_page,
    is_article_url,
    parse_url,
    get_article_text,
)


def test_parse_url():
    url = "https://example.com/world/2023/mar/11/ukraine-crisis-russia-troops-border-zelenskiy"
    expected_output = {
        "slug": "ukraine-crisis-russia-troops-border-zelenskiy",
        "category": "world",
        "date": date(2023, 3, 11),
    }
    assert parse_url(url) == expected_output

    # Test an invalid URL that should raise an exception
    with pytest.raises(ValueError):
        parse_url("https://example.com/2021-June-30/news/headlines")


def test_is_article_url():
    # Test for a valid article URL with a date
    href = "https://www.theguardian.com/world/2023/mar/11/ukraine-crisis-russia-troops-border-zelenskiy"
    root_url = "https://www.theguardian.com"
    assert is_article_url(href, root_url) is True

    # Test for an article URL without a date
    href = "https://www.theguardian.com/world/ukraine-crisis-russia-troops-border-zelenskiy"
    root_url = "https://www.theguardian.com"
    assert is_article_url(href, root_url) is False

    # Test for a URL from a different domain
    href = "https://www.example.com/article/2023/mar/11/test-article"
    root_url = "https://www.theguardian.com"
    assert is_article_url(href, root_url) is False


class MockResponse:
    def __init__(self, content):
        self.content = content
        self.status_code = 200
        self.headers = {"Content-Type": "text/html"}

    def text(self):
        return self.content


def test_get_front_page(mocker):
    with open("./tests/html/the_guardian_frontpage.html", "r") as f:
        html = f.read()
        mocker.patch("requests.get", return_value=MockResponse(html))

    # Test that the front page returns a list of article URLs
    get_front_page = partial(get_page, section="uk")
    article_urls = get_front_page()
    assert isinstance(article_urls, list)
    assert len(article_urls) > 0

    # Test that each URL is a valid article URL
    root_url = "https://www.theguardian.com"
    for url in article_urls:
        assert is_article_url(url, root_url) is True


def test_get_article_text(mocker):
    with open("./tests/html/the_guardian_article.html", "r") as f:
        html = f.read()
        mocker.patch("requests.get", return_value=MockResponse(html))

    article = get_article_text(
        "https://www.theguardian.com/politics/2023/mar/12/home-office-removed-image-huw-edwards-tweet-migration-bill-bbc-complaints"
    )

    assert article.split("\n")[0] == "This is a fake article"
    assert article.split("\n")[1] == "It Only has two paragraphs"

    assert len(article.split("\n")) == 2
