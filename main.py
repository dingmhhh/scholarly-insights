
from fastapi import FastAPI, Query
from typing import Literal
from datetime import date

app = FastAPI(
    title="Scholarly Insight API",
    description="Backend for scholarly article search",
    version="0.1.0"
)

@app.get("/")
def home():
    return {"message": "Welcome to Scholarly Insight"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/articles/search")
def search_articles(
    keyword: str | None = None,
    author: str | None = None,
    category: str | None = None,
    date_from: date | None = Query(None, description="Start date in YYYY-MM-DD format"),
    date_to: date | None = Query(None, description="End date in YYYY-MM-DD format"),
    start: int = Query(0, ge=0, description="Starting index for pagination"),
    max_results: int = Query(10, ge=1, le=100, description="Maximum number of results to return"),
    sort_by: Literal[
        "relevance", "submittedDate", "lastUpdatedDate"
        ] = Query("relevance", description="Sort results by relevance or date")
):
    """
    Search for scholarly articles using optional filters.

    Currently returns a placeholder response.
    The search module will be integrated separately. 
    """
    # Placeholder for actual search logic
    return {
        "query": {
            "keyword": keyword,
            "author": author,
            "category": category,
            "date_from": date_from,
            "date_to": date_to,
            "start": start,
            "max_results": max_results,
            "sort_by": sort_by
        },
        "articles": []  # Placeholder for actual search results
    }