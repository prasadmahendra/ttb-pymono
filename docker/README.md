# Docker Setup for Treasury TTB API

This directory contains Docker configuration for running the Treasury TTB GraphQL API.

## Prerequisites

- Docker and Docker Compose installed
- Sample SQLite database included in the image at `/tmp/treasury_db_local.db`

## Quick Start

### Build the Image

```bash
cd docker && ./docker-build.sh
```

### Run the API

```bash
# Basic run (uses .env file from project root if it exists)
./docker-run.sh api

# Or with docker-compose
docker-compose up -d
```

The GraphQL API will be accessible at:
- **GraphQL endpoint**: http://localhost:8080/graphql
- **Health check**: http://localhost:8080/health

## Passing Environment Variables

### Method 1: Using docker-run.sh with -e flags

Pass individual environment variables directly from command line:

```bash
# Single environment variable
./docker-run.sh api -e OPENAI_API_KEY=sk-your-key-here

# Multiple environment variables
./docker-run.sh api -e OPENAI_API_KEY=sk-xxx -e LOG_LEVEL=DEBUG

# All common variables
./docker-run.sh api \
  -e OPENAI_API_KEY=sk-xxx \
  -e ENV=production \
  -e LOG_LEVEL=INFO \
  -e DEBUG=false
```

### Method 2: Using docker-run.sh with custom .env file

```bash
# Use a custom environment file
./docker-run.sh api --env-file /path/to/custom.env

# Example with staging environment
./docker-run.sh api --env-file ../config/staging.env
```

### Method 3: Using docker-compose with environment variables

```bash
# Pass environment variables to docker-compose
OPENAI_API_KEY=sk-xxx LOG_LEVEL=DEBUG docker-compose up -d

# Or export them first
export ENV=prod
export OPENAI_API_KEY=sk-xxx
export LOG_LEVEL=INFO
docker-compose up -d
```

### Method 4: Using docker-compose with custom .env file

```bash
# Use a custom .env file with docker-compose
docker-compose --env-file ../config/production.env up -d

# Combine with production overrides
docker-compose \
  --env-file ../config/production.env \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  up -d
```

### Method 5: Direct docker run command

For maximum control, use docker directly:

```bash
docker run --rm \
  --name pymono-api \
  -p 8080:8080 \
  -e OPENAI_API_KEY=sk-xxx \
  -e LOG_LEVEL=DEBUG \
  -e APP_ENV=development \
  -e PYTHONUNBUFFERED=1 \
  -v "$(pwd)/../logs:/app/logs" \
  treasury/pymono:latest \
  treasury/services/gateways/ttb_api/__main__.py
```

