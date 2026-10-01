# Leukemia Detection Platform

Pediatric blood cancer (leukemia) detection platform: React + TypeScript frontend, FastAPI backend, and a separate ML training/evaluation pipeline.

## Layout

- `frontend/` — React + TypeScript UI (patient upload, doctor review, XAI)
- `backend/` — FastAPI API, auth, inference, and database
- `ml/` — model training, evaluation, and saved artifacts (kept separate from serving)
- `docs/` — problem statement, architecture, evaluation, limitations

## Local development

See `docker-compose.yml` for optional frontend + backend + database setup.
