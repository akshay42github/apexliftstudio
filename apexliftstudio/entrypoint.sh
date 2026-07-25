#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Only seed demo data if SEED_DEMO_DATA env var is set to true
if [ "$SEED_DEMO_DATA" = "true" ]; then
    echo "Seeding demo data..."
    python manage.py seed_demo
fi

echo "Starting Gunicorn server on port ${PORT:-8000}..."
exec gunicorn apexliftstudio.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --timeout 120 \
    --log-file -