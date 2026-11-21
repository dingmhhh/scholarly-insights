import sqlite3

from datetime import datetime, timedelta, timezone
from arxiv_client import fetch_articles

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from database import get_connection
from dependencies import get_current_user_id


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)

# Model for subscribing to a research category
class AlertCreate(BaseModel):
    category: str = Field(min_length=1, max_length=100)
    
# 1. Subscribe to a research category
@router.post("", status_code=201)
def add_alert(
    alert: AlertCreate,
    user_id: int = Depends(get_current_user_id)
):
    category = alert.category.strip()

    if not category:
        raise HTTPException(
            status_code=422,
            detail="Category cannot be empty"
        )
    conn = get_connection()

    try:
        # Check if the user is already subscribed to this category
        existing = conn.execute(
            """
            SELECT alert_id
            FROM alerts
            WHERE user_id = ? AND category = ?
            """,
            (user_id, category)
        ).fetchone()
        
        if existing:
            return {
                "alert_id": existing[0],
                "category": category,
                "message": "Already subscribed to this category"
            }
        
        # Add a new category subscription
        cursor = conn.execute(
            """
            INSERT INTO alerts (user_id, category)
            VALUES (?, ?)
            """,
            (user_id, category)
        )

        conn.commit()
        
        return {
            "alert_id": cursor.lastrowid,
            "category": category,
            "message": "Successfully subscribed to category"
        }
    except sqlite3.IntegrityError as exc:
        conn.rollback()

        raise HTTPException(
            status_code=409,
            detail="Could not subscribe to category"
        ) from exc

    finally:
        conn.close()
        
# 2. Get all subscribed research categories
@router.get("")
def get_alerts(
    user_id: int = Depends(get_current_user_id)
):
    conn = get_connection()

    try:
        # Get all categories subscribed to by this user
        rows = conn.execute(
            """
            SELECT alert_id, category, created_at
            FROM alerts
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        ).fetchall()

        return {
            "alerts": [
                {
                    "alert_id": row[0],
                    "category": row[1],
                    "created_at": row[2]
                }
                for row in rows
            ]
        }

    finally:
        conn.close()
        
# 3. Unsubscribe from a research category
@router.delete("/{alert_id}")
def delete_alert(
    alert_id: int,
    user_id: int = Depends(get_current_user_id)
):
    conn = get_connection()

    try:
        # Delete only the current user's subscription
        cursor = conn.execute(
            """
            DELETE FROM alerts
            WHERE alert_id = ? AND user_id = ?
            """,
            (alert_id, user_id)
        )

        # Check if a matching subscription was found
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Subscription not found"
            )

        # Save the deletion
        conn.commit()

        return {
            "message": "Successfully unsubscribed from category"
        }

    finally:
        conn.close()
        
# 4. Find recently published papers in a research category
def find_new_publications(category, days=1):
    result = fetch_articles(
        search_query=f"cat:{category}",
        max_results=50,
        sort_by="submittedDate"
    )

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    new_articles = []

    for article in result["articles"]:
       # Convert the publication date into a timezone-aware datetime
        published = datetime.fromisoformat(article["published"].replace("Z", "+00:00"))
        
        if published >= cutoff:
            new_articles.append(article)

    return new_articles

# 5. Get newly published papers from subscribed categories
@router.get("/new-publications")
def get_new_publications(
    user_id: int = Depends(get_current_user_id)
):
    conn = get_connection()

    try:
        # Get categories subscribed to by the current user
        rows = conn.execute(
            """
            SELECT category
            FROM alerts
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchall()

    finally:
        conn.close()

    # Find new papers in each subscribed category
    articles = {}

    for row in rows:
        category = row[0]

        # Find recently published papers
        new_articles = find_new_publications(category)

        # Save them as notifications for the current user
        save_notifications(user_id, category, new_articles)

        # Remove duplicate papers from the API response
        for article in new_articles:
            articles[article["id"]] = article

    return {
        "total": len(articles),
        "articles": list(articles.values())
    }
    
# 6. Save new publications as notifications
def save_notifications(user_id, category, articles):
    conn = get_connection()

    try:
        for article in articles:
            conn.execute(
                """
                INSERT OR IGNORE INTO notifications
                (user_id, arxiv_id, category, title, article_url)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    article["id"],
                    category,
                    article["title"],
                    article["article_url"]
                )
            )

        conn.commit()

    finally:
        conn.close()
        
# 7. Get saved notifications for the current user
@router.get("/notifications")
def get_notifications(
    user_id: int = Depends(get_current_user_id)
):
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT notification_id, arxiv_id, category,
                   title, article_url, is_read, created_at
            FROM notifications
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        ).fetchall()

        notifications = []

        for row in rows:
            notifications.append({
                "notification_id": row[0],
                "arxiv_id": row[1],
                "category": row[2],
                "title": row[3],
                "article_url": row[4],
                "is_read": bool(row[5]),
                "created_at": row[6]
            })

        return {
            "total": len(notifications),
            "notifications": notifications
        }

    finally:
        conn.close()
        
# 8. Mark a notification as read
@router.patch("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    user_id: int = Depends(get_current_user_id)
):
    conn = get_connection()

    try:
        # Update only the current user's notification
        cursor = conn.execute(
            """
            UPDATE notifications
            SET is_read = 1
            WHERE notification_id = ? AND user_id = ?
            """,
            (notification_id, user_id)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Notification not found"
            )

        conn.commit()

        return {
            "message": "Notification marked as read"
        }

    finally:
        conn.close()