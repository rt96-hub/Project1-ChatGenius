#!/bin/bash

# Check if migration message was provided
if [ -z "$1" ]; then
    echo "Please provide a migration message"
    echo "Usage: ./scripts/create_migration.sh 'migration message'"
    exit 1
fi

# Create new migration
alembic revision --autogenerate -m "$1"

echo "Migration created successfully"