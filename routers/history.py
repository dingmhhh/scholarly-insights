
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import sqlite3

from database import get_connection
from dependencies import get_current_user_id

router = APIRouter(
    prefix="/history",
    tags=["Reading History"]
)


class HistoryCreate(BaseModel):
    arxiv_id: str = Field(min_length=1, max_length=100)


@router.post("", status_code=201)
def record_history(
    article: HistoryCreate,
    user_id: int = Depends(get_current_user_id)
):
    arxiv_id = article.arxiv_id.strip()

    if not arxiv_id:
        raise HTTPException(
            status_code=422,
            detail="Article ID cannot be empty"
        )

    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO reading_history (
                user_id, arxiv_id, viewed_at
            )
            VALUES (?, ?, CURRENT_TIMESTAMP)
            """,
            (user_id, arxiv_id)
        )

        conn.commit()

        return {
            "history_id": cursor.lastrowid,
            "arxiv_id": arxiv_id,
            "message": "Reading history recorded"
        }

    except sqlite3.IntegrityError as exc:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail="Could not record reading history"
        ) from exc

    finally:
        conn.close()


@router.get("")
def get_history(
    user_id: int = Depends(get_current_user_id)
):
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT history_id, arxiv_id, viewed_at
            FROM reading_history
            WHERE user_id = ?
            ORDER BY viewed_at DESC, history_id DESC
            LIMIT 100
            """,
            (user_id,)
        ).fetchall()

        return {
            "history": [
                {
                    "history_id": row[0],
                    "arxiv_id": row[1],
                    "viewed_at": row[2]
                }
                for row in rows
            ]
        }

    finally:
        conn.close()
