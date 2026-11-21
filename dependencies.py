
from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)
from firebase_admin import auth

from firebase_config import get_firebase_app
from database import get_connection


bearer_scheme = HTTPBearer(auto_error=False)


def get_firebase_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    )
):
    """
    Verify Firebase ID Token and return its claims.
    """
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        decoded_token = auth.verify_id_token(
            credentials.credentials,
            app=get_firebase_app(),
            check_revoked=True
        )

    except (
        ValueError,
        auth.InvalidIdTokenError,
        auth.ExpiredIdTokenError,
        auth.RevokedIdTokenError,
        auth.UserDisabledError
    ) as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired Firebase token",
            headers={"WWW-Authenticate": "Bearer"}
        ) from exc

    return decoded_token


def get_current_user_id(
    firebase_user: dict = Depends(get_firebase_user)
):
    """
    Map Firebase UID to SQLite user_id.
    """
    firebase_uid = firebase_user["uid"]

    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT user_id
            FROM users
            WHERE firebase_uid = ?
            """,
            (firebase_uid,)
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=403,
                detail="User not found. Please sync your account."
            )

        return row[0]

    finally:
        conn.close()
