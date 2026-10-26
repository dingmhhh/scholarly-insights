from datetime import date
from unittest.mock import patch

import pytest

from search import build_search_query, search_articles


def test_keyword():
    assert build_search_query(
        keyword="machine learning"
    ) == 'all:"machine learning"'


def test_author():
    assert build_search_query(
        author="Smith"
    ) == 'au:"Smith"'


def test_category():
    assert build_search_query(
        category="cs.AI"
    ) == "cat:cs.AI"


def test_combined_filters():
    assert build_search_query(
        keyword="AI",
        category="cs.AI"
    ) == 'all:"AI" AND cat:cs.AI'


def test_date_range():
    result = build_search_query(
        date_from=date(2026, 1, 1),
        date_to=date(2026, 10, 25)
    )

    assert result == (
        "submittedDate:[202601010000 TO 202610252359]"
    )


def test_invalid_dates():
    with pytest.raises(ValueError):
        build_search_query(
            date_from=date(2026, 10, 25),
            date_to=date(2026, 1, 1)
        )


def test_empty_search():
    with pytest.raises(ValueError):
        build_search_query()


def test_invalid_keyword():
    with pytest.raises(ValueError):
        build_search_query(keyword='machine "learning"')


@patch("search.fetch_articles")
def test_search_calls_api(mock_fetch):
    mock_fetch.return_value = {
        "total_results": 0,
        "articles": []
    }

    result = search_articles(
        keyword="AI",
        max_results=5
    )

    mock_fetch.assert_called_once_with(
        search_query='all:"AI"',
        start=0,
        max_results=5,
        sort_by="relevance"
    )

    assert result["articles"] == []
