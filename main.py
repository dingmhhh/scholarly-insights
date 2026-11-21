from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Literal
from datetime import date
from pathlib import Path
import requests

from search import search_articles as run_article_search
from arxiv_client import fetch_articles
from database import get_connection, intialize_database

from routers.auth import router as auth_router
from routers.history import router as history_router

app = FastAPI(
    title="Scholarly Insight API",
    description="Backend for scholarly article search and discussion",
    version="0.2.0"
)

app.include_router(auth_router)
app.include_router(history_router)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class DiscussionCreate(BaseModel):
    arxiv_id: str = Field(min_length=1, max_length=100)
    author_name: str = Field(min_length=1, max_length=80)
    content: str = Field(min_length=1, max_length=3000)


@app.on_event("startup")
def startup_event():
    intialize_database()


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "templates" / "index.html")

@app.get("/login")
def login_page():
    return FileResponse(BASE_DIR / "templates" / "login.html")

@app.get("/reading-history", include_in_schema=False)
def history_page():
    return FileResponse(
        BASE_DIR / "templates" / "history.html"
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}


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
    try:
        return run_article_search(
            keyword=keyword,
            author=author,
            category=category,
            date_from=date_from,
            date_to=date_to,
            start=start,
            max_results=max_results,
            sort_by=sort_by
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve data from arXiv"
        ) from exc


@app.get("/articles/{article_id}")
def get_article(article_id: str):
    try:
        result = fetch_articles(
            search_query=f"id:{article_id}",
            max_results=1
        )
        if not result["articles"]:
            raise HTTPException(status_code=404, detail="Article not found")
        return result["articles"][0]
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve article from arXiv"
        ) from exc


@app.get("/articles/{article_id}/discussions")
def get_discussions(article_id: str):
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT discussion_id, arxiv_id, author_name, content, created_at
               FROM discussions
               WHERE arxiv_id = ?
               ORDER BY created_at DESC""",
            (article_id,)
        ).fetchall()
        return {"discussions": [
            {
                "discussion_id": row[0],
                "arxiv_id": row[1],
                "author_name": row[2],
                "content": row[3],
                "created_at": row[4]
            } for row in rows
        ]}
    finally:
        conn.close()


@app.post("/articles/{article_id}/discussions", status_code=201)
def create_discussion(article_id: str, discussion: DiscussionCreate):
    if discussion.arxiv_id != article_id:
        raise HTTPException(status_code=400, detail="Article ID mismatch")

    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO discussions (arxiv_id, author_name, content)
               VALUES (?, ?, ?)""",
            (
                article_id,
                discussion.author_name.strip(),
                discussion.content.strip()
            )
        )
        conn.commit()
        return {
            "discussion_id": cursor.lastrowid,
            "message": "Discussion posted successfully"
        }
    finally:
        conn.close()
