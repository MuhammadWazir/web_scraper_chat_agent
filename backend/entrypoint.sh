#!/bin/sh

# Wait for the database to be ready
echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

# Run migrations
echo "Running database migrations..."
uv run alembic upgrade head

# Start the application
echo "Starting application..."
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 1800 --limit-concurrency 100
