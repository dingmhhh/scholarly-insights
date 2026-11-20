
import requests
import xml.etree.ElementTree as ET
import re

ARXIV_API_URL = "https://export.arxiv.org/api/query"

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/"
}


def parse_arxiv_response(xml_content):
    """Convert an arXiv Atom XML feed into article dictionaries."""
    root = ET.fromstring(xml_content)

    total = root.findtext(
        "opensearch:totalResults",
        default="0",
        namespaces=NS
    )

    articles = []

    for entry in root.findall("atom:entry", NS):
        article_url = entry.findtext("atom:id", "", NS)
        title = entry.findtext("atom:title", "", NS)
        abstract = entry.findtext("atom:summary", "", NS)
        published = entry.findtext("atom:published", "", NS)

        authors = [
            author.findtext("atom:name", "", NS)
            for author in entry.findall("atom:author", NS)
        ]

        categories = [
            category.get("term")
            for category in entry.findall("atom:category", NS)
            if category.get("term")
        ]

        pdf_url = None
        for link in entry.findall("atom:link", NS):
            if link.get("title") == "pdf":
                pdf_url = link.get("href")
                break

        arxiv_id = article_url.rstrip("/").split("/")[-1]
        arxiv_id = re.sub(r"v\d+$", "", arxiv_id)
        articles.append({
            "id": arxiv_id,
            "title": " ".join(title.split()),
            "authors": authors,
            "abstract": " ".join(abstract.split()),
            "published": published[:10],
            "categories": categories,
            "pdf_url": pdf_url,
            "article_url": article_url
        })

    return {
        "total_results": int(total),
        "articles": articles
    }


def fetch_articles(
    search_query,
    start=0,
    max_results=10,
    sort_by="relevance"
):
    """Fetch scholarly articles from the arXiv API."""
    params = {
        "search_query": search_query,
        "start": start,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": "descending"
    }

    response = requests.get(
        ARXIV_API_URL,
        params=params,
        headers={"User-Agent": "ScholarlyInsights/0.1 (student project)"},
        timeout=30
    )

    response.raise_for_status()
    return parse_arxiv_response(response.content)


if __name__ == "__main__":
    result = fetch_articles(
        search_query="cat:cs.AI",
        max_results=3
    )

    for article in result["articles"]:
        print(article["title"])
