#!/bin/bash

# Stop any running containers
docker-compose -f docker-compose.local.yml down

# Remove existing volumes (optional, uncomment if you want to start fresh)
# docker volume rm $(docker volume ls -q)

# Build and start containers
docker-compose -f docker-compose.local.yml --env-file .env.local up --build