#!/bin/bash

set -e

echo "Waiting for database to be ready..."
until echo > /dev/tcp/db/5432; do
    echo "Database is unavailable. Waiting..."
    sleep 1
done
echo "Database is ready!"

echo "Apply database migrations"
python manage.py migrate

exec "$@"