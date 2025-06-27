#!/bin/sh
et -e

echo "Running alembic migrations..."
alembic upgrade head

echo "Starting FastAPI app..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
