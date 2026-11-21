
import sqlite3

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from database import get_connection
from dependencies import get_current_user_id


router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"]
)


class FavoriteCreate(BaseModel):
    arxiv_id: str = Field(min_length=1, max_length=100)


# 1. Add a paper to favorites
@router.post("", status_code=201)
def add_favorite(
    article: FavoriteCreate,
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
        # Check if the paper is already saved
        existing = conn.execute(
            """
            SELECT favorite_id
            FROM favorites
            WHERE user_id = ? AND arxiv_id = ?
            """,
            (user_id, arxiv_id)
        ).fetchone()

        if existing:
            return {
                "favorite_id": existing[0],
                "arxiv_id": arxiv_id,
                "message": "Article already in favorites"
            }

        # Insert new favorite
        cursor = conn.execute(
            """
            INSERT INTO favorites (user_id, arxiv_id)
            VALUES (?, ?)
            """,
            (user_id, arxiv_id)
        )

        conn.commit()

        return {
            "favorite_id": cursor.lastrowid,
            "arxiv_id": arxiv_id,
            "message": "Article added to favorites"
        }

    except sqlite3.IntegrityError as exc:
        conn.rollback()

        raise HTTPException(
            status_code=409,
            detail="Could not add favorite"
        ) from exc

    finally:
        conn.close()


# 2. Get all favorites for the current user
@router.get("")
def get_favorites(
    user_id: int = Depends(get_current_user_id)
):
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT favorite_id, arxiv_id
            FROM favorites
            WHERE user_id = ?
            ORDER BY favorite_id DESC
            """,
            (user_id,)
        ).fetchall()

        return {
            "favorites": [
                {
                    "favorite_id": row[0],
                    "arxiv_id": row[1]
                }
                for row in rows
            ]
        }

    finally:
        conn.close()


# 3. Check whether a paper is favorited
@router.get("/{article_id}")
def check_favorite(
    article_id: str,
    user_id: int = Depends(get_current_user_id)
):
    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT favorite_id
            FROM favorites
            WHERE user_id = ? AND arxiv_id = ?
            """,
            (user_id, article_id)
        ).fetchone()

        return {
            "arxiv_id": article_id,
            "is_favorited": row is not None
        }

    finally:
        conn.close()


# 4. Remove a paper from favorites
@router.delete("/{article_id}")
def remove_favorite(
    article_id: str,
    user_id: int = Depends(get_current_user_id)
):
    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            DELETE FROM favorites
            WHERE user_id = ? AND arxiv_id = ?
            """,
            (user_id, article_id)
        )

        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Favorite not found"
            )

        return {
            "arxiv_id": article_id,
            "message": "Article removed from favorites"
        }

    finally:
        conn.close()
