# Backend - Optimize My Oura

## Setup

1. Create and activate venv

```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment

- Create `backend/.env` file with:
```
APP_NAME=Optimize My Oura API
ENVIRONMENT=development
OURA_PERSONAL_ACCESS_TOKEN=your_pat_here
# SQLite (default)
DATABASE_URL=sqlite:///./oura.db
# Or Postgres
# DATABASE_URL=postgresql+psycopg://oura:oura@localhost:5432/oura
```

- Personal Access Token (PAT): create at `https://cloud.ouraring.com/personal-access-tokens`.

3. Run server

```
uvicorn app.main:app --reload --port 8000
```

## Postgres (optional)

Start a local Postgres using Docker:

```
docker compose up -d db
```

Then set:

```
DATABASE_URL=postgresql+psycopg://oura:oura@localhost:5432/oura
```

## API

- GET `/health` → `{ "status": "ok" }`
- GET `/api/sleep/daily?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- GET `/api/readiness/daily?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- GET `/api/activity/daily?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
