
from fastapi import FastAPI, Query, HTTPException
from typing import Literal
from datetime import date
import requests
from search import search_articles as run_article_search

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
@app.get("/articles/search")
def search_articles_endpoint(
    keyword: str | None = None,
    author: str | None = None,
    category: str | None = None,
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    start: int = Query(0, ge=0),
    max_results: int = Query(10, ge=1, le=100),
    sort_by: Literal[
        "relevance", "submittedDate", "lastUpdatedDate"
    ] = "relevance"
):
    """Search arXiv articles using optional filters."""
    try:
        result = run_article_search(
            keyword=keyword,
            author=author,
            category=category,
            date_from=date_from,
            date_to=date_to,
            start=start,
            max_results=max_results,
            sort_by=sort_by
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except requests.RequestException as exc:
        print(f"arXiv API error: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve data from arXiv"
        ) from exc