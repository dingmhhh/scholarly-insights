"""Scholarly Insights – Flask API + static frontend server.

Run:  python backend/app.py   ->  http://localhost:5000
"""
import json
import math
import os
import re

from flask import Flask, abort, jsonify, request, send_from_directory

from db import connect, init_db, now_iso

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
app.json.sort_keys = False

SORTS = {"relevance", "newest", "oldest", "cited"}
THREAD_SORTS = {"latest", "top", "unanswered"}


# --------------------------------------------------------------------------- helpers
def err(message, status=400):
    return jsonify({"error": message}), status


def int_arg(name, default, lo=None, hi=None):
    try:
        v = int(request.args.get(name, default))
    except (TypeError, ValueError):
        return default
    if lo is not None:
        v = max(lo, v)
    if hi is not None:
        v = min(hi, v)
    return v


def tokens(q):
    return [t for t in re.findall(r"[\w'’-]+", (q or "").lower()) if len(t) > 1][:8]


def row_to_article(r, with_abstract=True):
    d = {
        "id": r["id"], "title": r["title"], "authors": json.loads(r["authors"]),
        "keywords": json.loads(r["keywords"]), "journal": r["journal"], "year": r["year"],
        "subject": r["subject"], "type": r["type"], "open_access": bool(r["open_access"]),
        "citations": r["citations"], "doi": r["doi"],
    }
    if with_abstract:
        d["abstract"] = r["abstract"]
    return d


def build_where(args, exclude=()):
    """Translate query-string filters into a SQL WHERE clause.

    `exclude` omits a facet's own filter so facet counts show what *would* match
    if the user changed that facet (standard faceted-search behaviour).
    """
    clauses, params = [], []
    for t in tokens(args.get("q")):
        clauses.append("(LOWER(title) LIKE ? OR LOWER(abstract) LIKE ? OR LOWER(keywords) LIKE ?"
                       " OR LOWER(authors) LIKE ? OR LOWER(journal) LIKE ?)")
        params += [f"%{t}%"] * 5
    for key, col in (("subject", "subject"), ("type", "type")):
        vals = [v for v in args.getlist(key) if v]
        if vals and key not in exclude:
            clauses.append(f"{col} IN ({','.join('?' * len(vals))})")
            params += vals
    if "year" not in exclude:
        for key, op in (("year_from", ">="), ("year_to", "<=")):
            v = args.get(key, type=int)
            if v is not None:
                clauses.append(f"year {op} ?")
                params.append(v)
    if args.get("open_access") in ("1", "true") and "open_access" not in exclude:
        clauses.append("open_access = 1")
    return (" WHERE " + " AND ".join(clauses)) if clauses else "", params


def relevance(row, terms):
    if not terms:
        return 0
    title, abstract = row["title"].lower(), row["abstract"].lower()
    kw, au = row["keywords"].lower(), row["authors"].lower()
    score = 0
    for t in terms:
        score += 5 * title.count(t) + 3 * kw.count(t) + 2 * au.count(t) + abstract.count(t)
    # Mild boost for well-cited work so ties break sensibly.
    return score + math.log10(row["citations"] + 1)


# --------------------------------------------------------------------------- articles
@app.get("/api/articles")
def list_articles():
    args = request.args
    sort = args.get("sort", "relevance")
    if sort not in SORTS:
        return err("Invalid sort option")
    page = int_arg("page", 1, lo=1)
    per_page = int_arg("per_page", 10, lo=1, hi=50)

    conn = connect()
    where, params = build_where(args)
    rows = conn.execute(f"SELECT * FROM articles{where}", params).fetchall()

    terms = tokens(args.get("q"))
    if sort == "relevance":
        rows = sorted(rows, key=lambda r: (-relevance(r, terms), -r["year"]))
    elif sort == "newest":
        rows = sorted(rows, key=lambda r: (-r["year"], -r["citations"]))
    elif sort == "oldest":
        rows = sorted(rows, key=lambda r: (r["year"], -r["citations"]))
    else:
        rows = sorted(rows, key=lambda r: -r["citations"])

    total = len(rows)
    pages = max(1, math.ceil(total / per_page))
    page = min(page, pages)
    items = [row_to_article(r) for r in rows[(page - 1) * per_page: page * per_page]]

    facets = {}
    for facet, col in (("subject", "subject"), ("type", "type")):
        w, p = build_where(args, exclude=(facet,))
        facets[facet] = [
            {"value": r[0], "count": r[1]}
            for r in conn.execute(f"SELECT {col}, COUNT(*) c FROM articles{w} GROUP BY {col} ORDER BY c DESC, {col}", p)
        ]
    w, p = build_where(args, exclude=("year",))
    lo, hi = conn.execute(f"SELECT MIN(year), MAX(year) FROM articles{w}", p).fetchone()
    glo, ghi = conn.execute("SELECT MIN(year), MAX(year) FROM articles").fetchone()
    w, p = build_where(args, exclude=("open_access",))
    oa_count = conn.execute(
        f"SELECT COUNT(*) FROM articles{w + (' AND ' if w else ' WHERE ')}open_access = 1", p
    ).fetchone()[0]
    conn.close()

    return jsonify({
        "items": items, "total": total, "page": page, "pages": pages, "per_page": per_page,
        "facets": {**facets, "open_access": oa_count,
                   "year": {"min": glo, "max": ghi, "matched_min": lo, "matched_max": hi}},
    })


@app.get("/api/articles/<int:article_id>")
def get_article(article_id):
    conn = connect()
    r = conn.execute("SELECT * FROM articles WHERE id=?", (article_id,)).fetchone()
    if not r:
        conn.close()
        return err("Article not found", 404)
    article = row_to_article(r)

    # Related: same subject or overlapping keywords, ranked by overlap then citations.
    kws = set(k.lower() for k in article["keywords"])
    related = []
    for o in conn.execute("SELECT * FROM articles WHERE id != ?", (article_id,)):
        overlap = len(kws & set(k.lower() for k in json.loads(o["keywords"])))
        score = overlap * 3 + (2 if o["subject"] == r["subject"] else 0)
        if score:
            related.append((score, o["citations"], o))
    related.sort(key=lambda x: (-x[0], -x[1]))
    article["related"] = [row_to_article(o, with_abstract=False) for _, _, o in related[:4]]
    article["thread_count"] = conn.execute(
        "SELECT COUNT(*) FROM threads WHERE article_id=?", (article_id,)).fetchone()[0]
    conn.close()
    return jsonify(article)


@app.get("/api/suggest")
def suggest():
    q = (request.args.get("q") or "").strip().lower()
    if len(q) < 2:
        return jsonify({"suggestions": []})
    conn = connect()
    out, seen = [], set()
    for r in conn.execute("SELECT id, title, keywords FROM articles"):
        if q in r["title"].lower():
            out.append({"type": "article", "label": r["title"], "id": r["id"]})
        for k in json.loads(r["keywords"]):
            if q in k.lower() and k.lower() not in seen:
                seen.add(k.lower())
                out.append({"type": "keyword", "label": k})
    conn.close()
    out.sort(key=lambda s: (s["type"] != "keyword", not s["label"].lower().startswith(q), s["label"]))
    return jsonify({"suggestions": out[:8]})


@app.get("/api/stats")
def stats():
    conn = connect()
    d = {
        "articles": conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0],
        "subjects": conn.execute("SELECT COUNT(DISTINCT subject) FROM articles").fetchone()[0],
        "threads": conn.execute("SELECT COUNT(*) FROM threads").fetchone()[0],
        "posts": conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0],
    }
    conn.close()
    return jsonify(d)


# --------------------------------------------------------------------------- forum
THREAD_SELECT = """
SELECT t.*, c.name AS category_name, a.title AS article_title,
       (SELECT COUNT(*) FROM posts p WHERE p.thread_id = t.id) AS replies
FROM threads t
JOIN categories c ON c.slug = t.category
LEFT JOIN articles a ON a.id = t.article_id
"""


def row_to_thread(r, full=False):
    d = {k: r[k] for k in ("id", "title", "author", "category", "category_name", "article_id",
                           "article_title", "votes", "created_at", "last_activity", "replies")}
    d["excerpt"] = (r["body"][:220] + "…") if len(r["body"]) > 220 else r["body"]
    if full:
        d["body"] = r["body"]
    return d


@app.get("/api/forum/categories")
def categories():
    conn = connect()
    rows = conn.execute(
        "SELECT c.*, (SELECT COUNT(*) FROM threads t WHERE t.category=c.slug) AS threads FROM categories c"
    ).fetchall()
    conn.close()
    return jsonify({"categories": [dict(r) for r in rows]})


@app.get("/api/forum/threads")
def list_threads():
    sort = request.args.get("sort", "latest")
    if sort not in THREAD_SORTS:
        return err("Invalid sort option")
    page = int_arg("page", 1, lo=1)
    per_page = int_arg("per_page", 10, lo=1, hi=50)

    clauses, params = [], []
    if request.args.get("category"):
        clauses.append("t.category = ?")
        params.append(request.args["category"])
    if request.args.get("article_id", type=int):
        clauses.append("t.article_id = ?")
        params.append(request.args.get("article_id", type=int))
    for term in tokens(request.args.get("q")):
        clauses.append("(LOWER(t.title) LIKE ? OR LOWER(t.body) LIKE ?)")
        params += [f"%{term}%"] * 2
    if sort == "unanswered":
        clauses.append("(SELECT COUNT(*) FROM posts p WHERE p.thread_id = t.id) = 0")
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    order = {"latest": "t.last_activity DESC", "top": "t.votes DESC, t.last_activity DESC",
             "unanswered": "t.created_at DESC"}[sort]

    conn = connect()
    total = conn.execute(f"SELECT COUNT(*) FROM threads t{where}", params).fetchone()[0]
    rows = conn.execute(
        f"{THREAD_SELECT}{where} ORDER BY {order} LIMIT ? OFFSET ?",
        params + [per_page, (page - 1) * per_page]).fetchall()
    conn.close()
    return jsonify({"items": [row_to_thread(r) for r in rows], "total": total, "page": page,
                    "pages": max(1, math.ceil(total / per_page))})


@app.get("/api/forum/threads/<int:thread_id>")
def get_thread(thread_id):
    conn = connect()
    r = conn.execute(f"{THREAD_SELECT} WHERE t.id = ?", (thread_id,)).fetchone()
    if not r:
        conn.close()
        return err("Thread not found", 404)
    posts = [dict(p) for p in conn.execute(
        "SELECT id, author, body, votes, created_at FROM posts WHERE thread_id=? ORDER BY created_at, id",
        (thread_id,))]
    conn.close()
    t = row_to_thread(r, full=True)
    t["posts"] = posts
    return jsonify(t)


def clean_name(v):
    v = re.sub(r"\s+", " ", (v or "")).strip()
    return v if 2 <= len(v) <= 40 else None


@app.post("/api/forum/threads")
def create_thread():
    data = request.get_json(silent=True) or {}
    author, title, body = clean_name(data.get("author")), (data.get("title") or "").strip(), (data.get("body") or "").strip()
    category, article_id = data.get("category"), data.get("article_id")
    if not author:
        return err("Display name must be 2–40 characters.")
    if not 8 <= len(title) <= 160:
        return err("Title must be 8–160 characters.")
    if not 10 <= len(body) <= 8000:
        return err("Message must be 10–8000 characters.")
    conn = connect()
    if not conn.execute("SELECT 1 FROM categories WHERE slug=?", (category,)).fetchone():
        conn.close()
        return err("Please choose a valid category.")
    if article_id is not None:
        if not conn.execute("SELECT 1 FROM articles WHERE id=?", (article_id,)).fetchone():
            conn.close()
            return err("Linked article does not exist.")
    ts = now_iso()
    cur = conn.execute(
        "INSERT INTO threads (title, body, author, category, article_id, votes, created_at, last_activity)"
        " VALUES (?,?,?,?,?,0,?,?)", (title, body, author, category, article_id, ts, ts))
    conn.commit()
    tid = cur.lastrowid
    conn.close()
    return jsonify({"id": tid}), 201


@app.post("/api/forum/threads/<int:thread_id>/posts")
def create_post(thread_id):
    data = request.get_json(silent=True) or {}
    author, body = clean_name(data.get("author")), (data.get("body") or "").strip()
    if not author:
        return err("Display name must be 2–40 characters.")
    if not 2 <= len(body) <= 8000:
        return err("Reply must be 2–8000 characters.")
    conn = connect()
    if not conn.execute("SELECT 1 FROM threads WHERE id=?", (thread_id,)).fetchone():
        conn.close()
        return err("Thread not found", 404)
    ts = now_iso()
    cur = conn.execute("INSERT INTO posts (thread_id, author, body, votes, created_at) VALUES (?,?,?,0,?)",
                       (thread_id, author, body, ts))
    conn.execute("UPDATE threads SET last_activity=? WHERE id=?", (ts, thread_id))
    conn.commit()
    post = dict(conn.execute("SELECT id, author, body, votes, created_at FROM posts WHERE id=?",
                             (cur.lastrowid,)).fetchone())
    conn.close()
    return jsonify(post), 201


def _vote(table, row_id):
    data = request.get_json(silent=True) or {}
    delta = data.get("delta")
    if delta not in (1, -1):
        return err("delta must be 1 or -1")
    conn = connect()
    cur = conn.execute(f"UPDATE {table} SET votes = votes + ? WHERE id = ?", (delta, row_id))
    if cur.rowcount == 0:
        conn.close()
        return err("Not found", 404)
    conn.commit()
    votes = conn.execute(f"SELECT votes FROM {table} WHERE id=?", (row_id,)).fetchone()[0]
    conn.close()
    return jsonify({"votes": votes})


@app.post("/api/forum/threads/<int:thread_id>/vote")
def vote_thread(thread_id):
    return _vote("threads", thread_id)


@app.post("/api/forum/posts/<int:post_id>/vote")
def vote_post(post_id):
    return _vote("posts", post_id)


# --------------------------------------------------------------------------- pages
@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return err("Not found", 404)
    return send_from_directory(FRONTEND_DIR, "404.html"), 404


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=bool(os.environ.get("DEBUG")))
