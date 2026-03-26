# SmartKhaana

AI-powered restaurant intelligence dashboard built for HackNiche by Team ByteForge.

SmartKhaana helps restaurant owners turn reviews, social chatter, and web signals into practical business decisions across operations, marketing, ORM, and strategy.

## What This Project Does

- Aggregates review and social signals from multiple sources
- Runs aspect-based sentiment analysis on restaurant feedback
- Generates strategic frameworks such as SWOT, PESTEL, MECE, BCG, and Ansoff
- Provides ORM support for review response workflows
- Shows market intelligence with trend news and rating forecast
- Supports RAG chatbot-style Q and A on ingested restaurant context

## Repository Structure

- [backend](backend): FastAPI backend, ML pipeline, integrations, database layer
- [client](client): Next.js dashboard UI and framework pages
- [docker-compose.yml](docker-compose.yml): Root compose to run backend container

## Tech Stack

### Backend

- FastAPI, Pydantic, SQLAlchemy, PostgreSQL
- Transformers plus PyTorch for sentiment pipeline
- NLTK for sentence and keyword processing
- ChromaDB for local vector context
- Google Maps API, AirTop, web scraping services

### Frontend

- Next.js (App Router), React, TypeScript
- Tailwind CSS v4, Radix UI, Recharts

## Key Backend APIs

- POST /analyze/business/insights
	End-to-end ingestion plus ABSA plus dashboard payload
- POST /analyze/frameworks/swot
- POST /analyze/frameworks/pestel
- POST /analyze/frameworks/mece
- POST /analyze/frameworks/four-ps
- POST /analyze/frameworks/bcg
- POST /analyze/frameworks/ansoff
- POST /market-intelligence
- POST /insights/orm-reviews
- POST /insights/publish-review-reply
- POST /chatbot/rag

Interactive docs: http://localhost:8000/docs

## Setup Guide

## 1. Prerequisites

- Python 3.11+
- Node.js 18+
- npm or pnpm
- Docker Desktop (optional but recommended)

## 2. Backend Environment

Create [backend/.env](backend/.env) with required keys:

- GOOGLE_MAPS_API_KEY
- GEMINI_API_KEY
- DATABASE_URL
- RAPIDAPI_TWITTER_KEY
- AIRTOP_API_KEY
- AGENT_ID
- AIRTOP_INVOCATION_ID
- FEATHERLESS_API_KEY
- FEATHERLESS_MODEL
- FEATHERLESS_FALLBACK_MODELS

## 3. Run Backend

### Option A: Docker

From repo root:

```bash
docker compose up --build backend
```

If only env changed:

```bash
docker compose up -d --force-recreate backend
```

### Option B: Local Python

From [backend](backend):

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 4. Run Frontend

From [client](client):

```bash
npm install
npm run dev
```

Frontend: http://localhost:3000

## 5. Initialize Database (if needed)

From [backend](backend):

```bash
python init_db.py
```

Note: current initializer is destructive and recreates schema objects.

## End-to-End Flow

1. User enters business details on dashboard
2. Frontend calls /analyze/business/insights
3. Backend fetches source data and performs ABSA
4. Dashboard renders overview and triggers framework APIs
5. Framework cards populate progressively
6. Fallback mocks are shown in frontend for unavailable integrations to keep demo continuity

## Current Demo Behavior

- Loading overlay appears while analysis is running
- Floating chatbot is available globally in UI
- Some sections use realistic frontend mocks when backend endpoints fail or are partially integrated

## Troubleshooting

- Business not found in framework API:
	pass place_id from insights response in framework request
- Env key changed but backend still old:
	recreate container with force-recreate
- Gemini quota errors:
	this is usually project quota, not key mismatch
- Duplicate logs in dev:
	can occur with reload and repeated client calls

## Submission Notes

- Keep both backend and frontend running during demo
- Run one clean analysis first to warm caches and DB records
- Use fallback-enabled dashboard flow if external APIs throttle

## Team

ByteForge
