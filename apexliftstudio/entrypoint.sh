#!/bin/bash

# Exit on error
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute command
exec "$@"
```

---

## .gitignore
```
# Python
*.py[cod]
__pycache__/
*.so
*.egg
*.egg-info/
dist/
build/
.venv/
venv/
env/

# Django
*.log
db.sqlite3
db.sqlite3-journal
/media
/staticfiles
/static

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
htmlcov/
.pytest_cache/
```

---

## Procfile
```
web: gunicorn apexliftstudio.wsgi:application --log-file -
release: python manage.py migrate --noinput