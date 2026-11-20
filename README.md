# Scholarly Insights — Frontend and API Integration

This version adds a responsive HTML/CSS/JavaScript frontend to the existing FastAPI and SQLite scholarly article project.

## Features

- Search arXiv papers by keyword, author, category and publication date.
- Sort by relevance, submitted date or last updated date.
- Paginated search results.
- Article detail modal with abstract, authors, categories and arXiv/PDF links.
- Discussion forum attached to each article.
- SQLite persistence for discussion posts.
- Responsive layout for desktop, tablet and mobile.

## Project structure

```text
scholarly-insights-frontend/
├── main.py
├── search.py
├── arxiv_client.py
├── database.py
├── schema.sql
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    ├── styles.css
    └── app.js
```

`search.py`, `arxiv_client.py` and `requirements.txt` should be copied from the supplied `Local.zip` project version. The frontend/API integration uses their existing search function and arXiv response structure.

## Run locally

1. Copy `search.py`, `arxiv_client.py` and `requirements.txt` from `scholarly-insights-local-integration` into this project folder.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the API and frontend:

   ```bash
   uvicorn main:app --reload
   ```

4. Open `http://127.0.0.1:8000`.

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Serve frontend |
| GET | `/health` | Health check |
| GET | `/articles/search` | Search/filter/paginate articles |
| GET | `/articles/{article_id}` | Retrieve article details |
| GET | `/articles/{article_id}/discussions` | List discussion posts |
| POST | `/articles/{article_id}/discussions` | Create a discussion post |

## Notes

- Search and article details are retrieved live from arXiv. Network access is required.
- Discussion posts are stored in the local SQLite database.
- The discussion form currently accepts a display name and message; it is not authenticated. Add Firebase token verification before using it as a public production forum.
- The project keeps the existing FastAPI route and function style. It does not introduce a frontend framework or a separate Node.js build step.
