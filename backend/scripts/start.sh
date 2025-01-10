#!/bin/bash
set -e

# Function to check if database is ready
check_db() {
    python3 << END
import sys
import psycopg2
import os

try:
    psycopg2.connect(
        dbname=os.environ.get("POSTGRES_DB", "chatapp"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
        host=os.environ.get("POSTGRES_HOST", "db")
    )
except psycopg2.OperationalError:
    sys.exit(1)
sys.exit(0)
END
}

# Wait for database to be ready
until check_db; do
  >&2 echo "Database is unavailable - sleeping"
  sleep 1
done

>&2 echo "Database is up - executing migrations"

# Run migrations
alembic upgrade head

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload