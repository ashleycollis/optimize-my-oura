# optimize-my-oura

Personal health dashboard powered by Oura Ring data and AI insights.

A custom dashboard that visualizes your sleep, readiness, and activity metrics more effectively than the native Oura app. It integrates directly with the Oura API and uses AI-generated insights to give personalized health guidance.

## Features

- **Daily Metrics**: Sleep, readiness, and activity scores with 7/30-day trend views
- **AI Coach Summary**: GPT-4o-mini powered recommendations based on your data patterns
- **Workout Tracking**: Activity sessions synced from Oura's workout API
- **Pattern Analysis**: Average sleep, bedtime, and step counts over time
- **Interactive Chat**: Ask questions about your health data in natural language

## Stack

- **Backend**: Django + SQLite (Postgres ready)
- **Frontend**: React + Vite + Tailwind CSS
- **AI**: OpenAI GPT-4o-mini
- **API**: Oura Cloud API v2

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 18+
- Oura Ring account with personal access token
- OpenAI API key

### Installation

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp env.example .env
# Add YOUR_OURA_TOKEN and YOUR_OPENAI_KEY

python manage.py migrate
python manage.py createsuperuser  # optional
python manage.py runserver


source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

```bash
# Frontend
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`
Table data can be be viewed at admin panel: `http://localhost:8000/admin`


## Configure OpenAI 
Get one at: https://platform.openai.com/api-keys"
Set OPENAI_API_KEY in .env file 
Credits required for GPT-4o-mini feature https://platform.openai.com/settings/organization/billing

### Oura Token Setup

1. Generate personal access token at https://cloud.ouraring.com/personal-access-tokens
2. Django admin: `http://localhost:8000/admin`
3. Create UserProfile for your user and paste token and set as OURA_TOKEN in .env profile
4. Refresh frontend to load data

## Architecture

**Data Flow**:
- `/api/metrics/` fetches last 30 days from Oura (cached 1hr)
- Data stored in `OuraMetric` model with daily scores + sleep/activity breakdowns
- OpenAI generates insights with structured JSON responses
- Frontend slices data for 7/30-day views with trend charts

**Caching Strategy**:
- Oura metrics: 1hr TTL on DB queries to reduce API calls
- AI insights: DB-based caching (consider Redis for prod)
- Force refresh with `?force=true` query param

**Cost Analysis**:
- Coach summary: ~$0.25 per generation (cached 1hr)
- Chat responses: ~$0.15 per message
- Trend insights: ~$0.10 per generation
- Estimated $3-5/month for daily usage

## Testing

```bash
cd backend
source venv/bin/activate
python manage.py test
```

Basic unit tests for models and API endpoints



# owner: Ashley Collis-Burgess
