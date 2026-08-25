---
project: FindHackathons
generated_by: orpheon
generated_at: 2026-08-22
source_repository: venvennnn/findhackathons
source_commit: c800e204f048fbe344bc82819a29ec3baf5873a8
---

## Architecture

Monorepo: `frontend/` Next.js App Router and Tailwind on Vercel; `backend/` FastAPI, SQLModel, matching engine, Alembic on Railway; `worker/` Modal.com Playwright scrapers plus Instructor and OpenAI on a six-hour cron. PostgreSQL on Supabase, SQLite locally.

On boot the API seeds demo listings if the database is empty. Worker deploy is optional.

Do not commit `OPENAI_API_KEY`, `BACKEND_API_URL`, or `INGEST_TOKEN`.
