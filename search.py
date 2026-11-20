import re
from datetime import date
from arxiv_client import fetch_articles

def validate_text(value):
    if value is None:
        return None
    value = value.strip()
    if any(char in value for char in ['"', '\n', '\r']):
        raise ValueError("Invalid characters in input.")
    return value or None

def build_search_query(keyword=None,
    author=None,
    category=None,
    date_from=None,
    date_to=None):
    """Construct the search query for the arXiv API."""
    conditions = []
    keyword = validate_text(keyword)
    author = validate_text(author)
    category = validate_text(category)

    if keyword:
        conditions.append(f'all:"{keyword}"')
    if author:
        conditions.append(f'au:"{author}"')
    if category:
        if not re.fullmatch(r"[A-Za-z0-9.-]+", category):
            raise ValueError("Invalid arXiv category")
        conditions.append(f"cat:{category}")
    if date_from or date_to:
        start_date = date_from or date(1991, 1, 1)
        end_date = date_to or date.today()

        if start_date > end_date:
            raise ValueError("date_from cannot be after date_to")

        conditions.append(
            f"submittedDate:[{start_date:%Y%m%d}0000 "
            f"TO {end_date:%Y%m%d}2359]"
        )
    if not conditions:
        raise ValueError("At least one search parameter must be provided.")

    return " AND ".join(conditions)

def search_articles(
    keyword=None,
    author=None,
    category=None,
    date_from=None,
    date_to=None,
    start=0,
    max_results=10,
    sort_by="relevance"
):
    """Search for scholarly articles using the arXiv API."""
    search_query = build_search_query(keyword, author, category, date_from, date_to)
    return fetch_articles(search_query=search_query, start=start, max_results=max_results, sort_by=sort_by)