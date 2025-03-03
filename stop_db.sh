#!/bin/bash

# Stop the PostgreSQL container
echo "Stopping PostgreSQL container..."
docker compose down

# If successful, print success message
if [ $? -eq 0 ]; then
    echo "PostgreSQL container has been stopped."
else
    echo "Failed to stop PostgreSQL container. Please check the logs with 'docker compose logs postgres'"
fi
