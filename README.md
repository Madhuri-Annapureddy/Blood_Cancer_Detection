# Leukemia Detection Platform

Pediatric blood cancer (leukemia) detection platform: React + TypeScript frontend, FastAPI backend, and a separate ML training/evaluation pipeline.

> **Note**: This project is currently in the initial scaffolding phase. While the architecture is established, most backend API routes are stubs, and the frontend dashboards are empty placeholders. The image classification ML model has been trained and saved, but is not yet connected to the backend inference pipeline.

## Layout

- `frontend/` — React + TypeScript UI (Currently contains skeleton dashboards and mocked authentication context)
- `backend/` — FastAPI API and database models (Currently contains database schemas for PostgreSQL; API routes return "not implemented")
- `ml/` — model training, evaluation, and saved artifacts (Contains trained `efficientnet_b0_cnmc.keras` model)
- `docs/` — problem statement, architecture, evaluation, limitations

## Local development

See `docker-compose.yml` for optional frontend + backend + database setup.
