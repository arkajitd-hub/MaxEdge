# Max AI (Internal Sports Agency AI)

Max AI is an internal-first AI assistant + analytics platform for a sports agency handling football, tennis, F1, Indy, and basketball talent.

## MVP Architecture
- **Backend:** FastAPI
- **Database:** PostgreSQL (SQLite fallback for local quickstart)
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **LLM API:** OpenAI (pluggable)
- **Frontend:** Streamlit

## Features
- Chat-style internal assistant for quick questions.
- Athlete + sponsor database with seeded sample data (120 athletes).
- Analytics endpoints for sport mix, sponsor concentration, and top talent.
- Sponsor-fit recommendation logic for athletes.

## Quickstart

### 1) Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Environment variables
```bash
cp .env.example .env
```

Set values:
- `DATABASE_URL` (recommended PostgreSQL URL)
- `OPENAI_API_KEY` (optional for LLM-enhanced chat)

### 3) Initialize database + seed sample records
```bash
python scripts/init_db.py
```

### 4) Run backend
```bash
uvicorn backend.app.main:app --reload --port 8000
```

### 5) Run Streamlit UI
```bash
streamlit run frontend/app.py
```

## API Endpoints (MVP)
- `GET /health`
- `GET /athletes`
- `GET /athletes/{athlete_id}`
- `GET /analytics/overview`
- `GET /suggestions/sponsor-fit?athlete_id=...`
- `POST /chat/query`

## Notes
- For production, run PostgreSQL + pgvector and move recommendation/ranking to vector + feature store.
- Add Celery + Redis when async ingestion/tasks are needed.
