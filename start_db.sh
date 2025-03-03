#!/bin/bash

# Start the PostgreSQL container
echo "Starting PostgreSQL container..."
docker compose up -d postgres

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 5

# Check if PostgreSQL is running
echo "Checking PostgreSQL connection..."
docker compose exec postgres pg_isready -U postgres

# If successful, print success message
if [ $? -eq 0 ]; then
    echo "PostgreSQL is now running and ready to use!"
    echo "Database Name: $(grep DB_NAME .env | cut -d '=' -f2)"
    echo "Username: $(grep DB_USER .env | cut -d '=' -f2)"
    echo "Port: $(grep DB_PORT .env | cut -d '=' -f2)"
    echo "Host: localhost"
else
    echo "Failed to start PostgreSQL container. Please check the logs with 'docker-compose logs postgres'"
fi
