
import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from database import get_connection
from dependencies import (
    get_firebase_user,
    get_current_user_id
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/sync")
def sync_user(
    firebase_user: dict = Depends(get_firebase_user)
):
    """
    Create or update SQLite user after Firebase login.
    """
    firebase_uid = firebase_user["uid"]
    email = firebase_user.get("email")

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Firebase account has no email"
        )

    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO users (firebase_uid, email)
            VALUES (?, ?)
            ON CONFLICT(firebase_uid)
            DO UPDATE SET email = excluded.email
            """,
            (firebase_uid, email)
        )

        conn.commit()

        user = conn.execute(
            """
            SELECT user_id, firebase_uid, email
            FROM users
            WHERE firebase_uid = ?
            """,
            (firebase_uid,)
        ).fetchone()

        return {
            "user_id": user[0],
            "firebase_uid": user[1],
            "email": user[2]
        }

    except sqlite3.IntegrityError as exc:
        conn.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email is already linked to another user"
        ) from exc

    finally:
        conn.close()


@router.get("/me")
def get_my_profile(
    user_id: int = Depends(get_current_user_id)
):
    """
    Return the authenticated user's SQLite profile.
    """
    conn = get_connection()

    try:
        user = conn.execute(
            """
            SELECT user_id, firebase_uid, email
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return {
            "user_id": user[0],
            "firebase_uid": user[1],
            "email": user[2]
        }

    finally:
        conn.close()
