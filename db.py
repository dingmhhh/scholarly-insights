"""SQLite helpers and schema for Scholarly Insights."""
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone

from seed_data import ARTICLES, CATEGORIES, THREADS

DB_PATH = os.environ.get("SI_DB_PATH", os.path.join(os.path.dirname(__file__), "scholarly.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    abstract TEXT NOT NULL,
    authors TEXT NOT NULL,          -- JSON array
    keywords TEXT NOT NULL,         -- JSON array
    journal TEXT NOT NULL,
    year INTEGER NOT NULL,
    subject TEXT NOT NULL,
    type TEXT NOT NULL,
    open_access INTEGER NOT NULL DEFAULT 0,
    citations INTEGER NOT NULL DEFAULT 0,
    doi TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_articles_subject ON articles(subject);
CREATE INDEX IF NOT EXISTS idx_articles_year ON articles(year);

CREATE TABLE IF NOT EXISTS categories (
    slug TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    author TEXT NOT NULL,
    category TEXT NOT NULL REFERENCES categories(slug),
    article_id INTEGER REFERENCES articles(id),
    votes INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    last_activity TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_threads_category ON threads(category);
CREATE INDEX IF NOT EXISTS idx_threads_article ON threads(article_id);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    author TEXT NOT NULL,
    body TEXT NOT NULL,
    votes INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_posts_thread ON posts(thread_id);
"""


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def now_iso(offset_minutes=0):
    t = datetime.now(timezone.utc) + timedelta(minutes=offset_minutes)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def init_db():
    conn = connect()
    conn.executescript(SCHEMA)
    if conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0] == 0:
        _seed(conn)
    conn.commit()
    conn.close()


def _seed(conn):
    for i, a in enumerate(ARTICLES, start=1):
        conn.execute(
            "INSERT INTO articles (title, abstract, authors, keywords, journal, year, subject, type,"
            " open_access, citations, doi) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (a["title"], a["abstract"], json.dumps(a["authors"]), json.dumps(a["keywords"]),
             a["journal"], a["year"], a["subject"], a["type"], int(a["open_access"]),
             a["citations"], f"10.5555/si.{a['year']}.{i:04d}"),
        )
    conn.executemany("INSERT INTO categories VALUES (?,?,?)", CATEGORIES)

    # Spread seeded timestamps over the past few days so "latest" ordering looks natural.
    for n, (title, body, author, cat, art_idx, votes, replies) in enumerate(THREADS):
        created = now_iso(-60 * (6 + n * 13))
        article_id = art_idx + 1 if art_idx is not None else None
        cur = conn.execute(
            "INSERT INTO threads (title, body, author, category, article_id, votes, created_at, last_activity)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (title, body, author, cat, article_id, votes, created, created),
        )
        tid, last = cur.lastrowid, created
        for k, (r_author, r_body, r_votes) in enumerate(replies):
            last = now_iso(-60 * (4 + n * 13) + k * 20)
            conn.execute(
                "INSERT INTO posts (thread_id, author, body, votes, created_at) VALUES (?,?,?,?,?)",
                (tid, r_author, r_body, r_votes, last),
            )
        conn.execute("UPDATE threads SET last_activity=? WHERE id=?", (last, tid))
