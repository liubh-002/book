#!/bin/bash
set -e

echo "=== Pet Wash System Startup ==="

# Run database migrations
echo ">>> Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo ">>> Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start gunicorn on Railway's PORT
echo ">>> Starting gunicorn on port ${PORT:-8000}..."
exec gunicorn pet_wash_system.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
